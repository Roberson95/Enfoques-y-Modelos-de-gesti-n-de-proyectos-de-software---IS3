#!/usr/bin/env python3
"""SaludUni - servidor (API + base de datos + entrega de la interfaz).
Solo usa la biblioteca estándar de Python 3.8+. No hay nada que instalar.

Uso:      python server.py        ->  abrir http://127.0.0.1:8000
Variables opcionales: PORT, HOST (0.0.0.0 en la nube), DB_PATH,
ADMIN_PASSWORD (contraseña inicial del admin), TZ_OFFSET (horas, ej. -3)."""
import datetime as dt, hashlib, hmac, json, os, re, secrets, sqlite3, tempfile, time, traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE, "saluduni.db"))
ROLES = ["Alumno", "Profesor", "Médico", "Administrador"]
# Plantillas de horario inicial (lunes a sábado). Equivalen a los turnos fijos anteriores.
TEMPLATES = {"Mañana": ("08:00", "12:00"), "Tarde": ("14:00", "18:00"), "Noche": ("18:00", "21:00")}
DURS = (10, 15, 20, 30, 40, 45, 60)
ID_RE = re.compile(r"^[\w.@+-]{3,60}$")
HM_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
SESSION_DAYS = 7
LOG_KEEP = 50000  # cantidad máxima de registros de actividad que se conservan
FAILS = {}

SCHEMA = """
CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, salt TEXT, hash TEXT, role TEXT, pid TEXT);
CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, uid TEXT, created REAL);
CREATE TABLE IF NOT EXISTS specs(name TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS pros(id TEXT PRIMARY KEY, name TEXT, spec TEXT, shift TEXT);
CREATE TABLE IF NOT EXISTS apps(id TEXT PRIMARY KEY, uid TEXT, pid TEXT, date TEXT, time TEXT, st TEXT, created REAL);
CREATE UNIQUE INDEX IF NOT EXISTS one_active ON apps(pid, date, time) WHERE st='activo';
CREATE TABLE IF NOT EXISTS hours(pid TEXT, wd INTEGER, ini TEXT, fin TEXT);
CREATE INDEX IF NOT EXISTS hours_pid ON hours(pid);
CREATE TABLE IF NOT EXISTS blocks(id TEXT PRIMARY KEY, pid TEXT, d1 TEXT, d2 TEXT, why TEXT);
CREATE TABLE IF NOT EXISTS logs(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, uid TEXT, role TEXT, act TEXT, det TEXT, ip TEXT);
"""

class Err(Exception):
    def __init__(self, code, msg): self.code, self.msg = code, msg

class File:  # respuesta binaria para descargar
    def __init__(self, data, name, ctype="application/octet-stream"): self.data, self.name, self.ctype = data, name, ctype

def db():
    c = sqlite3.connect(DB_PATH, timeout=10)
    c.row_factory = sqlite3.Row
    return c

def now():
    off = os.environ.get("TZ_OFFSET")
    if off: return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None) + dt.timedelta(hours=float(off))
    return dt.datetime.now()

def hpw(pw, salt): return hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 200000).hex()
def tm(s): return int(s[:2]) * 60 + int(s[3:5])
def hm(m): return "%02d:%02d" % (m // 60, m % 60)

def add_user(c, uid, pw, role, pid=None, must=0):
    salt = secrets.token_hex(16)
    c.execute("INSERT INTO users(id,salt,hash,role,pid,must_change) VALUES(?,?,?,?,?,?)",
              (uid, salt, hpw(pw, salt), role, pid, must))

def tmpl_hours(c, pid, shift):
    ini, fin = TEMPLATES.get(shift, TEMPLATES["Mañana"])
    for wd in range(6): c.execute("INSERT INTO hours VALUES(?,?,?,?)", (pid, wd, ini, fin))

def log(c, uid, role, act, det="", ip=""):
    c.execute("INSERT INTO logs(ts,uid,role,act,det,ip) VALUES(?,?,?,?,?,?)",
              (now().strftime("%Y-%m-%d %H:%M:%S"), uid, role, act, det[:300], ip))

def L(c, u, ip, act, det=""): log(c, u["id"], u["role"], act, det, ip)

def init():
    c = db()
    had_hours = c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='hours'").fetchone()
    c.executescript(SCHEMA)
    cols = lambda t: [r[1] for r in c.execute("PRAGMA table_info(%s)" % t)]
    if "must_change" not in cols("users"):  # migraciones automáticas
        c.execute("ALTER TABLE users ADD COLUMN must_change INTEGER DEFAULT 0")
    if "dur" not in cols("pros"):
        c.execute("ALTER TABLE pros ADD COLUMN dur INTEGER DEFAULT 30")
    if not c.execute("SELECT 1 FROM specs").fetchone():
        data = {"Medicina General": ["Dra. Laura Méndez", "Dr. Martín Silva", "Dra. Ana Varela"],
                "Odontología": ["Dr. Carlos Benítez", "Dra. Sofía Ríos", "Dr. Pablo Duarte"],
                "Psicología": ["Dra. Elena Giménez", "Dr. Diego Acosta", "Dra. Lucía Romero"],
                "Nutrición": ["Lic. Marta Ortiz", "Lic. Javier Franco", "Lic. Paula Núñez"],
                "Enfermería": ["Lic. Rosa Vera", "Lic. Hugo Paredes", "Lic. Nora Cabral"]}
        i = 0
        for s, names in data.items():
            c.execute("INSERT INTO specs VALUES(?)", (s,))
            for k, n in enumerate(names):
                i += 1; c.execute("INSERT INTO pros(id,name,spec,shift,dur) VALUES(?,?,?,?,30)",
                                  ("p%d" % i, n, s, list(TEMPLATES)[k]))
        add_user(c, "admin", os.environ.get("ADMIN_PASSWORD", "admin123"), "Administrador")
        add_user(c, "medico1", "medico123", "Médico", "p1")
        print("Datos iniciales creados. Admin: admin / admin123 (cambiala). Médico demo: medico1 / medico123")
    if not had_hours:  # primera vez con horarios propios: se copian los turnos fijos anteriores
        for p in c.execute("SELECT id, shift FROM pros").fetchall(): tmpl_hours(c, p["id"], p["shift"])
    c.execute("DELETE FROM logs WHERE id <= (SELECT MAX(id) FROM logs) - ?", (LOG_KEEP,))
    c.commit(); c.close()

def auth(c, h):
    a = h.get("Authorization", "")
    t = h.get("X-Token") or (a[7:] if a.startswith("Bearer ") else "")
    if not t: return None
    return c.execute("SELECT u.* FROM sessions s JOIN users u ON u.id=s.uid WHERE s.token=? AND s.created>?",
                     (t, time.time() - SESSION_DAYS * 86400)).fetchone()

def need_role(u, *roles):
    if u["role"] not in roles: raise Err(403, "No tenés permiso para esta acción")

def session(c, uid):
    t = secrets.token_urlsafe(32)
    c.execute("DELETE FROM sessions WHERE created<?", (time.time() - SESSION_DAYS * 86400,))
    c.execute("INSERT INTO sessions VALUES(?,?,?)", (t, uid, time.time()))
    return {"token": t}

def creds(b):
    uid, pw = str(b.get("id", "")).strip().lower(), str(b.get("password", ""))
    if not ID_RE.match(uid): raise Err(400, "Usuario inválido (3 a 60 caracteres: letras, números . @ + - _)")
    if len(pw) < 6: raise Err(400, "La contraseña debe tener al menos 6 caracteres")
    return uid, pw

def own_pro(c, u, pid):
    """El admin puede editar cualquier profesional; el profesional, solo el suyo."""
    if not (u["role"] == "Administrador" or (u["role"] == "Médico" and u["pid"] == pid)):
        raise Err(403, "No tenés permiso para esta acción")
    p = c.execute("SELECT * FROM pros WHERE id=?", (pid,)).fetchone()
    if not p: raise Err(404, "Profesional no encontrado")
    return p

def slots(c, p, d):
    """Horarios de inicio de consulta de un profesional en una fecha."""
    ds, dur = d.isoformat(), p["dur"] or 30
    if c.execute("SELECT 1 FROM blocks WHERE pid=? AND d1<=? AND d2>=?", (p["id"], ds, ds)).fetchone(): return []
    out = []
    for h in c.execute("SELECT ini, fin FROM hours WHERE pid=? AND wd=? ORDER BY ini", (p["id"], d.weekday())):
        m = tm(h["ini"])
        while m + dur <= tm(h["fin"]): out.append(hm(m)); m += dur
    return out

def desc(c, a):
    p = c.execute("SELECT name FROM pros WHERE id=?", (a["pid"],)).fetchone()
    return "%s · %s · %s %s · paciente %s" % (a["id"], p["name"] if p else a["pid"], a["date"], a["time"], a["uid"])

# ---------- endpoints ----------
def state(c, u, b, ip):
    r, today = u["role"], now().date().isoformat()
    priv = lambda pid: r == "Administrador" or (r == "Médico" and u["pid"] == pid)
    hours, blocks = {}, {}
    for h in c.execute("SELECT * FROM hours ORDER BY wd, ini"): hours.setdefault(h["pid"], []).append([h["wd"], h["ini"], h["fin"]])
    for x in c.execute("SELECT * FROM blocks WHERE d2>=? ORDER BY d1", (today,)):
        d = {"id": x["id"], "d1": x["d1"], "d2": x["d2"]}
        if priv(x["pid"]): d["why"] = x["why"]
        blocks.setdefault(x["pid"], []).append(d)
    pros = []
    for x in c.execute("SELECT id,name,spec,shift,dur FROM pros ORDER BY rowid"):
        pros.append(dict(x, dur=x["dur"] or 30, hours=hours.get(x["id"], []), blocks=blocks.get(x["id"], [])))
    out = {"user": {"id": u["id"], "role": r, "pid": u["pid"], "must_change": bool(u["must_change"])},
           "specs": [x[0] for x in c.execute("SELECT name FROM specs ORDER BY rowid")], "pros": pros, "apps": [],
           "today": today}
    q = "SELECT a.*, u.role AS urole FROM apps a LEFT JOIN users u ON u.id=a.uid ORDER BY a.date, a.time"
    for a in c.execute(q):
        own = r == "Administrador" or a["uid"] == u["id"] or (r == "Médico" and a["pid"] == u["pid"])
        if not own and not (a["st"] == "activo" and a["date"] >= today): continue
        d = {k: a[k] for k in ("id", "pid", "date", "time", "st")}
        if own: d.update(uid=a["uid"], uname=a["uid"], role=a["urole"])
        out["apps"].append(d)
    if r == "Administrador":
        out["users"] = [dict(x) for x in c.execute("SELECT id,role,pid FROM users ORDER BY rowid")]
    return out

def register(c, u, b, ip):
    uid, pw = creds(b)
    if b.get("role") not in ("Alumno", "Profesor"): raise Err(400, "Perfil inválido")
    if c.execute("SELECT 1 FROM users WHERE id=?", (uid,)).fetchone(): raise Err(409, "Ese usuario ya existe")
    add_user(c, uid, pw, b["role"]); log(c, uid, b["role"], "Registro", "Cuenta nueva", ip)
    return session(c, uid)

def login(c, u, b, ip):
    uid, t = str(b.get("id", "")).strip().lower(), time.time()
    key = (ip, uid); FAILS[key] = [x for x in FAILS.get(key, []) if t - x < 300]
    if len(FAILS[key]) >= 5: raise Err(429, "Demasiados intentos. Esperá 5 minutos.")
    r = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if not r or not hmac.compare_digest(hpw(str(b.get("password", "")), r["salt"]), r["hash"]):
        FAILS[key].append(t)
        log(c, uid[:60], r["role"] if r else None, "Ingreso fallido", "Contraseña incorrecta" if r else "Usuario inexistente", ip)
        raise Err(401, "Usuario o contraseña incorrectos")
    L(c, r, ip, "Ingreso"); return session(c, uid)

def logout(c, u, b, ip):
    c.execute("DELETE FROM sessions WHERE uid=?", (u["id"],)); L(c, u, ip, "Salida"); return {"ok": True}

def book(c, u, b, ip):
    need_role(u, "Alumno", "Profesor")
    a = None
    if b.get("re"):
        a = c.execute("SELECT * FROM apps WHERE id=? AND uid=? AND st='activo'", (b["re"], u["id"])).fetchone()
        if not a: raise Err(404, "Turno no encontrado")
    p = c.execute("SELECT * FROM pros WHERE id=?", (a["pid"] if a else b.get("pid"),)).fetchone()
    if not p: raise Err(404, "Profesional no encontrado")
    try: d = dt.date.fromisoformat(str(b.get("date")))
    except ValueError: raise Err(400, "Fecha inválida")
    t, n, dur = b.get("time"), now(), p["dur"] or 30
    if d < n.date() or d > n.date() + dt.timedelta(days=60): raise Err(400, "Fecha no disponible")
    if t not in slots(c, p, d): raise Err(400, "Ese horario no está disponible para este profesional")
    if dt.datetime.combine(d, dt.time.fromisoformat(t)) <= n: raise Err(400, "Ese horario ya pasó")
    for x in c.execute("SELECT id, time FROM apps WHERE pid=? AND date=? AND st='activo'", (p["id"], d.isoformat())):
        if x["id"] != (a["id"] if a else None) and abs(tm(x["time"]) - tm(t)) < dur:
            raise Err(409, "Ese horario ya fue tomado")
    if a:
        c.execute("UPDATE apps SET date=?, time=? WHERE id=?", (d.isoformat(), t, a["id"]))
        L(c, u, ip, "Reprogramación", "%s · de %s %s a %s %s" % (a["id"], a["date"], a["time"], d.isoformat(), t))
        return {"id": a["id"]}
    if c.execute("SELECT COUNT(*) FROM apps WHERE uid=? AND st='activo'", (u["id"],)).fetchone()[0] >= 5:
        raise Err(400, "Ya tenés 5 turnos activos")
    i = "SU-" + secrets.token_hex(3).upper()
    c.execute("INSERT INTO apps VALUES(?,?,?,?,?,?,?)", (i, u["id"], p["id"], d.isoformat(), t, "activo", time.time()))
    L(c, u, ip, "Reserva", "%s · %s · %s %s" % (i, p["name"], d.isoformat(), t))
    return {"id": i}

def status(c, u, b, ip):
    a, st, r = c.execute("SELECT * FROM apps WHERE id=?", (b.get("id"),)).fetchone(), b.get("st"), u["role"]
    if not a or a["st"] != "activo": raise Err(404, "Turno no disponible")
    if st not in ("cancelado", "atendido"): raise Err(400, "Estado inválido")
    if r == "Administrador" or (r == "Médico" and a["pid"] == u["pid"]): pass
    elif a["uid"] == u["id"] and st == "cancelado":
        if dt.datetime.fromisoformat(a["date"] + " " + a["time"]) - now() < dt.timedelta(hours=2):
            raise Err(400, "Solo podés cancelar hasta 2 horas antes")
    else: raise Err(403, "No tenés permiso para esta acción")
    c.execute("UPDATE apps SET st=? WHERE id=?", (st, a["id"]))
    L(c, u, ip, "Cancelación" if st == "cancelado" else "Atendido", desc(c, a)); return {"ok": True}

def pro_add(c, u, b, ip):
    need_role(u, "Administrador"); n = str(b.get("name", "")).strip()
    if not 2 <= len(n) <= 80: raise Err(400, "Nombre inválido")
    if not c.execute("SELECT 1 FROM specs WHERE name=?", (b.get("spec"),)).fetchone(): raise Err(400, "Especialidad inválida")
    if b.get("shift") not in TEMPLATES: raise Err(400, "Horario inicial inválido")
    pid = "p" + secrets.token_hex(4)
    c.execute("INSERT INTO pros(id,name,spec,shift,dur) VALUES(?,?,?,?,30)", (pid, n, b["spec"], b["shift"]))
    tmpl_hours(c, pid, b["shift"]); L(c, u, ip, "Profesional agregado", "%s · %s" % (n, b["spec"])); return {"ok": True}

def pro_del(c, u, b, ip):
    need_role(u, "Administrador")
    p = c.execute("SELECT * FROM pros WHERE id=?", (b.get("id"),)).fetchone()
    if not p: raise Err(404, "Profesional no encontrado")
    if c.execute("SELECT 1 FROM apps WHERE pid=? AND st='activo'", (p["id"],)).fetchone():
        raise Err(400, "Tiene turnos activos: cancelalos primero")
    if c.execute("SELECT 1 FROM users WHERE pid=?", (p["id"],)).fetchone():
        raise Err(400, "Tiene una cuenta de acceso: quitala antes desde Usuarios")
    for t in ("hours", "blocks"): c.execute("DELETE FROM %s WHERE pid=?" % t, (p["id"],))
    c.execute("DELETE FROM pros WHERE id=?", (p["id"],)); L(c, u, ip, "Profesional quitado", p["name"]); return {"ok": True}

def pro_hours(c, u, b, ip):
    p = own_pro(c, u, b.get("pid"))
    dur, hs = b.get("dur"), b.get("hours")
    if dur not in DURS: raise Err(400, "Duración de consulta inválida")
    if not isinstance(hs, list) or len(hs) > 40: raise Err(400, "Horarios inválidos")
    DN, by = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"], {}
    for h in hs:
        if not (isinstance(h, list) and len(h) == 3 and h[0] in range(7)
                and all(isinstance(x, str) and HM_RE.match(x) for x in h[1:])):
            raise Err(400, "Horarios inválidos")
        if tm(h[1]) + dur > tm(h[2]):
            raise Err(400, "La franja %s–%s del %s es más corta que una consulta de %d min" % (h[1], h[2], DN[h[0]], dur))
        by.setdefault(h[0], []).append((h[1], h[2]))
    for wd, fr in by.items():
        fr.sort()
        for x, y in zip(fr, fr[1:]):
            if y[0] < x[1]: raise Err(400, "Las franjas del %s se superponen (%s–%s y %s–%s)" % (DN[wd], x[0], x[1], y[0], y[1]))
    c.execute("DELETE FROM hours WHERE pid=?", (p["id"],))
    for wd, fr in by.items():
        for ini, fin in fr: c.execute("INSERT INTO hours VALUES(?,?,?,?)", (p["id"], wd, ini, fin))
    c.execute("UPDATE pros SET dur=? WHERE id=?", (dur, p["id"]))
    p = c.execute("SELECT * FROM pros WHERE id=?", (p["id"],)).fetchone()
    today, outside = now().date().isoformat(), 0
    for a in c.execute("SELECT date, time FROM apps WHERE pid=? AND st='activo' AND date>=?", (p["id"], today)).fetchall():
        if a["time"] not in slots(c, p, dt.date.fromisoformat(a["date"])): outside += 1
    resumen = "; ".join("%s %s" % (DN[wd][:3], ", ".join("%s–%s" % f for f in by[wd])) for wd in sorted(by)) or "sin horarios"
    L(c, u, ip, "Horarios modificados", "%s · %d min · %s" % (p["name"], dur, resumen))
    return {"ok": True, "outside": outside}

def block_add(c, u, b, ip):
    p = own_pro(c, u, b.get("pid"))
    try: d1, d2 = dt.date.fromisoformat(str(b.get("d1"))), dt.date.fromisoformat(str(b.get("d2")))
    except ValueError: raise Err(400, "Fechas inválidas")
    why = str(b.get("why", "")).strip()[:80]
    if d2 < d1: raise Err(400, "La fecha final es anterior a la inicial")
    if d2 < now().date(): raise Err(400, "Ese período ya pasó")
    if (d2 - d1).days > 366: raise Err(400, "El período no puede superar un año")
    c.execute("INSERT INTO blocks VALUES(?,?,?,?,?)", ("b" + secrets.token_hex(4), p["id"], d1.isoformat(), d2.isoformat(), why))
    n = c.execute("SELECT COUNT(*) FROM apps WHERE pid=? AND st='activo' AND date BETWEEN ? AND ?",
                  (p["id"], d1.isoformat(), d2.isoformat())).fetchone()[0]
    L(c, u, ip, "Bloqueo agregado", "%s · %s a %s%s" % (p["name"], d1, d2, " · " + why if why else ""))
    return {"ok": True, "affected": n}

def block_del(c, u, b, ip):
    x = c.execute("SELECT * FROM blocks WHERE id=?", (b.get("id"),)).fetchone()
    if not x: raise Err(404, "Bloqueo no encontrado")
    p = own_pro(c, u, x["pid"])
    c.execute("DELETE FROM blocks WHERE id=?", (x["id"],))
    L(c, u, ip, "Bloqueo quitado", "%s · %s a %s" % (p["name"], x["d1"], x["d2"])); return {"ok": True}

def spec_add(c, u, b, ip):
    need_role(u, "Administrador"); n = str(b.get("name", "")).strip()
    if not 2 <= len(n) <= 40: raise Err(400, "Nombre inválido")
    c.execute("INSERT INTO specs VALUES(?)", (n,)); L(c, u, ip, "Especialidad agregada", n); return {"ok": True}

def spec_del(c, u, b, ip):
    need_role(u, "Administrador")
    if c.execute("SELECT 1 FROM pros WHERE spec=?", (b.get("name"),)).fetchone(): raise Err(400, "Quitá antes a sus profesionales")
    if c.execute("DELETE FROM specs WHERE name=?", (b.get("name"),)).rowcount:
        L(c, u, ip, "Especialidad quitada", str(b.get("name")))
    return {"ok": True}

def user_add(c, u, b, ip):
    need_role(u, "Administrador"); uid, pw = creds(b); role, pid = b.get("role"), None
    if role not in ROLES: raise Err(400, "Perfil inválido")
    if role == "Médico":
        pid = b.get("pid")
        if not c.execute("SELECT 1 FROM pros WHERE id=?", (pid,)).fetchone(): raise Err(400, "Elegí el profesional vinculado")
    if c.execute("SELECT 1 FROM users WHERE id=?", (uid,)).fetchone(): raise Err(409, "Ese usuario ya existe")
    add_user(c, uid, pw, role, pid, 1)
    pn = c.execute("SELECT name FROM pros WHERE id=?", (pid,)).fetchone() if pid else None
    L(c, u, ip, "Usuario creado", "%s · %s%s" % (uid, role, " · " + pn["name"] if pn else "")); return {"ok": True}

def user_del(c, u, b, ip):
    need_role(u, "Administrador")
    if b.get("id") == u["id"]: raise Err(400, "No podés quitar tu propio usuario")
    c.execute("DELETE FROM sessions WHERE uid=?", (b.get("id"),))
    if c.execute("DELETE FROM users WHERE id=?", (b.get("id"),)).rowcount: L(c, u, ip, "Usuario quitado", str(b.get("id")))
    return {"ok": True}

def change_pw(c, u, b, ip):
    old, new = str(b.get("old", "")), str(b.get("new", ""))
    key, t = (ip, "pw:" + u["id"]), time.time()
    FAILS[key] = [x for x in FAILS.get(key, []) if t - x < 300]
    if len(FAILS[key]) >= 5: raise Err(429, "Demasiados intentos. Esperá 5 minutos.")
    if not hmac.compare_digest(hpw(old, u["salt"]), u["hash"]):
        FAILS[key].append(t); raise Err(400, "La contraseña actual no es correcta")
    if len(new) < 6: raise Err(400, "La contraseña nueva debe tener al menos 6 caracteres")
    if new == old: raise Err(400, "La contraseña nueva debe ser distinta de la actual")
    salt = secrets.token_hex(16)
    c.execute("UPDATE users SET salt=?, hash=?, must_change=0 WHERE id=?", (salt, hpw(new, salt), u["id"]))
    c.execute("DELETE FROM sessions WHERE uid=?", (u["id"],))  # cierra todas las sesiones anteriores
    L(c, u, ip, "Contraseña cambiada"); return session(c, u["id"])

def user_reset(c, u, b, ip):
    need_role(u, "Administrador")
    r = c.execute("SELECT id FROM users WHERE id=?", (b.get("id"),)).fetchone()
    if not r: raise Err(404, "Usuario no encontrado")
    if r["id"] == u["id"]: raise Err(400, "Tu propia contraseña se cambia desde Perfil")
    tmp = "".join(secrets.choice("abcdefghjkmnpqrstuvwxyz23456789") for _ in range(8))
    salt = secrets.token_hex(16)
    c.execute("UPDATE users SET salt=?, hash=?, must_change=1 WHERE id=?", (salt, hpw(tmp, salt), r["id"]))
    c.execute("DELETE FROM sessions WHERE uid=?", (r["id"],))
    L(c, u, ip, "Contraseña restablecida", r["id"]); return {"password": tmp}

LOG_CATS = {"ingresos": ("Ingreso", "Ingreso fallido", "Salida", "Registro", "Contraseña cambiada"),
            "turnos": ("Reserva", "Reprogramación", "Cancelación", "Atendido"),
            "admin": ("Profesional agregado", "Profesional quitado", "Especialidad agregada", "Especialidad quitada",
                      "Usuario creado", "Usuario quitado", "Contraseña restablecida", "Horarios modificados",
                      "Bloqueo agregado", "Bloqueo quitado", "Copia descargada")}

def logs(c, u, b, ip):
    need_role(u, "Administrador")
    q, cat = str(b.get("q", "")).strip()[:60], b.get("cat")
    try: off = max(0, int(b.get("offset", 0)))
    except (TypeError, ValueError): off = 0
    w, args = [], []
    if q:
        like = "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        w.append("(uid LIKE ? ESCAPE '\\' OR act LIKE ? ESCAPE '\\' OR det LIKE ? ESCAPE '\\' OR ts LIKE ? ESCAPE '\\')")
        args += [like] * 4
    if cat in LOG_CATS:
        w.append("act IN (%s)" % ",".join("?" * len(LOG_CATS[cat]))); args += LOG_CATS[cat]
    rows = c.execute("SELECT ts,uid,role,act,det,ip FROM logs %s ORDER BY id DESC LIMIT 101 OFFSET ?"
                     % ("WHERE " + " AND ".join(w) if w else ""), args + [off]).fetchall()
    return {"rows": [dict(r) for r in rows[:100]], "more": len(rows) > 100}

def backup(c, u, b, ip):
    need_role(u, "Administrador")
    fd, tmp = tempfile.mkstemp(suffix=".db"); os.close(fd)
    try:
        dst = sqlite3.connect(tmp); c.backup(dst); dst.close()  # copia consistente aunque haya uso simultáneo
        with open(tmp, "rb") as f: data = f.read()
    finally: os.remove(tmp)
    L(c, u, ip, "Copia descargada", "%d KB" % (len(data) // 1024))
    return File(data, "saluduni-%s.db" % now().strftime("%Y%m%d-%H%M"))

def guard(u, fn):  # con contraseña temporal solo se puede cambiar la clave o salir
    if u and u["must_change"] and fn not in (state, change_pw, logout):
        raise Err(403, "Tenés que cambiar tu contraseña antes de continuar")

GET_ROUTES = {"/api/state": state, "/api/backup": backup}
ROUTES = {"/api/login": (login, False), "/api/register": (register, False), "/api/logout": (logout, True),
          "/api/book": (book, True), "/api/status": (status, True), "/api/pro": (pro_add, True),
          "/api/pro/del": (pro_del, True), "/api/pro/hours": (pro_hours, True),
          "/api/block": (block_add, True), "/api/block/del": (block_del, True),
          "/api/spec": (spec_add, True), "/api/spec/del": (spec_del, True),
          "/api/user": (user_add, True), "/api/user/del": (user_del, True),
          "/api/password": (change_pw, True), "/api/user/reset": (user_reset, True), "/api/logs": (logs, True)}

SEC_HEADERS = [("Cache-Control", "no-store"), ("X-Content-Type-Options", "nosniff"),
               ("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "
                "connect-src 'self'; img-src 'self' data:")]

def handle(fn, b, need, headers, ip):
    """Ejecuta un endpoint. Devuelve (código, cuerpo_bytes, content_type, cabeceras_extra)."""
    c, extra = db(), []
    try:
        u = auth(c, headers)
        if need and not u: raise Err(401, "Iniciá sesión")
        guard(u, fn)
        res = fn(c, u, b, ip); c.commit()
        if isinstance(res, File):
            return 200, res.data, res.ctype, [("Content-Disposition", 'attachment; filename="%s"' % res.name)]
        code, body = 200, res
    except Err as x: c.commit(); code, body = x.code, {"error": x.msg}
    except sqlite3.IntegrityError: c.rollback(); code, body = 409, {"error": "Ya existe, o ese horario ya fue tomado"}
    except Exception as x:
        c.rollback(); traceback.print_exc()
        code, body = 500, {"error": "Error interno del servidor: " + type(x).__name__ + " - " + str(x)[:120]}
    finally: c.close()
    return code, json.dumps(body, ensure_ascii=False).encode(), "application/json; charset=utf-8", extra

class H(BaseHTTPRequestHandler):
    def log_message(self, f, *a): pass

    def out(self, code, body, ctype="application/json; charset=utf-8", extra=()):
        if not isinstance(body, bytes): body = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        for k, v in [("Content-Type", ctype), ("Content-Length", len(body))] + SEC_HEADERS + list(extra):
            self.send_header(k, str(v))
        self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        p = urlparse(self.path).path
        if p in ("/", "/index.html"):
            with open(os.path.join(BASE, "index.html"), "rb") as f: return self.out(200, f.read(), "text/html; charset=utf-8")
        if p in GET_ROUTES: return self.out(*handle(GET_ROUTES[p], {}, True, self.headers, self.client_address[0]))
        self.out(404, {"error": "No encontrado"})

    def do_POST(self):
        r = ROUTES.get(urlparse(self.path).path)
        if not r: return self.out(404, {"error": "No encontrado"})
        n = int(self.headers.get("Content-Length") or 0)
        if n > 20000: return self.out(413, {"error": "Solicitud demasiado grande"})
        try: b = json.loads(self.rfile.read(n) or b"{}")
        except ValueError: return self.out(400, {"error": "JSON inválido"})
        if not isinstance(b, dict): return self.out(400, {"error": "JSON inválido"})
        self.out(*handle(r[0], b, r[1], self.headers, self.client_address[0]))

if __name__ == "__main__":
    init()
    host, port = os.environ.get("HOST", "127.0.0.1"), int(os.environ.get("PORT", "8000"))
    print("SaludUni funcionando en http://%s:%d  (Ctrl+C para detener)" % (host, port))
    ThreadingHTTPServer((host, port), H).serve_forever()
