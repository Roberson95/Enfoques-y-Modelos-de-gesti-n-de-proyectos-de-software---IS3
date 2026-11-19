#!/usr/bin/env python3
"""SaludUni - servidor (API + base de datos + entrega de la interfaz).
Solo usa la biblioteca estándar de Python 3.8+. No hay nada que instalar.

Uso:      python server.py        ->  abrir http://127.0.0.1:8000
Variables opcionales: PORT, HOST (0.0.0.0 en la nube), DB_PATH,
ADMIN_PASSWORD (contraseña inicial del admin), TZ_OFFSET (horas, ej. -3)."""
import datetime as dt, hashlib, hmac, json, os, re, secrets, sqlite3, time, traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE, "saluduni.db"))
ROLES = ["Alumno", "Profesor", "Médico", "Administrador"]
def _slots(a, b): return ["%02d:%02d" % (m // 60, m % 60) for m in range(a, b + 1, 30)]
SHIFTS = {"Mañana": _slots(480, 690), "Tarde": _slots(840, 1050), "Noche": _slots(1080, 1230)}
ID_RE = re.compile(r"^[\w.@+-]{3,60}$")
SESSION_DAYS = 7
FAILS = {}

SCHEMA = """
CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, salt TEXT, hash TEXT, role TEXT, pid TEXT);
CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, uid TEXT, created REAL);
CREATE TABLE IF NOT EXISTS specs(name TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS pros(id TEXT PRIMARY KEY, name TEXT, spec TEXT, shift TEXT);
CREATE TABLE IF NOT EXISTS apps(id TEXT PRIMARY KEY, uid TEXT, pid TEXT, date TEXT, time TEXT, st TEXT, created REAL);
CREATE UNIQUE INDEX IF NOT EXISTS one_active ON apps(pid, date, time) WHERE st='activo';
"""

class Err(Exception):
    def __init__(self, code, msg): self.code, self.msg = code, msg

def db():
    c = sqlite3.connect(DB_PATH, timeout=10)
    c.row_factory = sqlite3.Row
    return c

def now():
    off = os.environ.get("TZ_OFFSET")
    if off: return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None) + dt.timedelta(hours=float(off))
    return dt.datetime.now()

def hpw(pw, salt): return hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt), 200000).hex()

def add_user(c, uid, pw, role, pid=None, must=0):
    salt = secrets.token_hex(16)
    c.execute("INSERT INTO users(id,salt,hash,role,pid,must_change) VALUES(?,?,?,?,?,?)",
              (uid, salt, hpw(pw, salt), role, pid, must))

def init():
    c = db(); c.executescript(SCHEMA)
    if "must_change" not in [r[1] for r in c.execute("PRAGMA table_info(users)")]:
        c.execute("ALTER TABLE users ADD COLUMN must_change INTEGER DEFAULT 0")  # migración automática
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
                i += 1; c.execute("INSERT INTO pros VALUES(?,?,?,?)", ("p%d" % i, n, s, list(SHIFTS)[k]))
        add_user(c, "admin", os.environ.get("ADMIN_PASSWORD", "admin123"), "Administrador")
        add_user(c, "medico1", "medico123", "Médico", "p1")
        print("Datos iniciales creados. Admin: admin / admin123 (cambiala). Médico demo: medico1 / medico123")
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

# ---------- endpoints ----------
def state(c, u, b, ip):
    r, today = u["role"], now().date().isoformat()
    out = {"user": {"id": u["id"], "role": r, "pid": u["pid"], "must_change": bool(u["must_change"])},
           "specs": [x[0] for x in c.execute("SELECT name FROM specs ORDER BY rowid")],
           "pros": [dict(x) for x in c.execute("SELECT id,name,spec,shift FROM pros ORDER BY rowid")], "apps": []}
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
    add_user(c, uid, pw, b["role"]); return session(c, uid)

def login(c, u, b, ip):
    uid, key, t = str(b.get("id", "")).strip().lower(), None, time.time()
    key = (ip, uid); FAILS[key] = [x for x in FAILS.get(key, []) if t - x < 300]
    if len(FAILS[key]) >= 5: raise Err(429, "Demasiados intentos. Esperá 5 minutos.")
    r = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if not r or not hmac.compare_digest(hpw(str(b.get("password", "")), r["salt"]), r["hash"]):
        FAILS[key].append(t); raise Err(401, "Usuario o contraseña incorrectos")
    return session(c, uid)

def logout(c, u, b, ip):
    c.execute("DELETE FROM sessions WHERE uid=?", (u["id"],)); return {"ok": True}

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
    t, n = b.get("time"), now()
    if t not in SHIFTS[p["shift"]]: raise Err(400, "Horario fuera del turno del profesional")
    if d.weekday() == 6 or d < n.date() or d > n.date() + dt.timedelta(days=60): raise Err(400, "Fecha no disponible")
    if dt.datetime.combine(d, dt.time.fromisoformat(t)) <= n: raise Err(400, "Ese horario ya pasó")
    if a:
        c.execute("UPDATE apps SET date=?, time=? WHERE id=?", (d.isoformat(), t, a["id"])); return {"id": a["id"]}
    if c.execute("SELECT COUNT(*) FROM apps WHERE uid=? AND st='activo'", (u["id"],)).fetchone()[0] >= 5:
        raise Err(400, "Ya tenés 5 turnos activos")
    i = "SU-" + secrets.token_hex(3).upper()
    c.execute("INSERT INTO apps VALUES(?,?,?,?,?,?,?)", (i, u["id"], p["id"], d.isoformat(), t, "activo", time.time()))
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
    c.execute("UPDATE apps SET st=? WHERE id=?", (st, a["id"])); return {"ok": True}

def pro_add(c, u, b, ip):
    need_role(u, "Administrador"); n = str(b.get("name", "")).strip()
    if not 2 <= len(n) <= 80: raise Err(400, "Nombre inválido")
    if not c.execute("SELECT 1 FROM specs WHERE name=?", (b.get("spec"),)).fetchone(): raise Err(400, "Especialidad inválida")
    if b.get("shift") not in SHIFTS: raise Err(400, "Turno inválido")
    c.execute("INSERT INTO pros VALUES(?,?,?,?)", ("p" + secrets.token_hex(4), n, b["spec"], b["shift"])); return {"ok": True}

def pro_del(c, u, b, ip):
    need_role(u, "Administrador")
    if c.execute("SELECT 1 FROM apps WHERE pid=? AND st='activo'", (b.get("id"),)).fetchone():
        raise Err(400, "Tiene turnos activos: cancelalos primero")
    c.execute("DELETE FROM pros WHERE id=?", (b.get("id"),)); return {"ok": True}

def spec_add(c, u, b, ip):
    need_role(u, "Administrador"); n = str(b.get("name", "")).strip()
    if not 2 <= len(n) <= 40: raise Err(400, "Nombre inválido")
    c.execute("INSERT INTO specs VALUES(?)", (n,)); return {"ok": True}

def spec_del(c, u, b, ip):
    need_role(u, "Administrador")
    if c.execute("SELECT 1 FROM pros WHERE spec=?", (b.get("name"),)).fetchone(): raise Err(400, "Quitá antes a sus profesionales")
    c.execute("DELETE FROM specs WHERE name=?", (b.get("name"),)); return {"ok": True}

def user_add(c, u, b, ip):
    need_role(u, "Administrador"); uid, pw = creds(b); role, pid = b.get("role"), None
    if role not in ROLES: raise Err(400, "Perfil inválido")
    if role == "Médico":
        pid = b.get("pid")
        if not c.execute("SELECT 1 FROM pros WHERE id=?", (pid,)).fetchone(): raise Err(400, "Elegí el profesional del médico")
    if c.execute("SELECT 1 FROM users WHERE id=?", (uid,)).fetchone(): raise Err(409, "Ese usuario ya existe")
    add_user(c, uid, pw, role, pid, 1); return {"ok": True}

def user_del(c, u, b, ip):
    need_role(u, "Administrador")
    if b.get("id") == u["id"]: raise Err(400, "No podés quitar tu propio usuario")
    c.execute("DELETE FROM sessions WHERE uid=?", (b.get("id"),)); c.execute("DELETE FROM users WHERE id=?", (b.get("id"),))
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
    return session(c, u["id"])

def user_reset(c, u, b, ip):
    need_role(u, "Administrador")
    r = c.execute("SELECT id FROM users WHERE id=?", (b.get("id"),)).fetchone()
    if not r: raise Err(404, "Usuario no encontrado")
    if r["id"] == u["id"]: raise Err(400, "Tu propia contraseña se cambia desde Perfil")
    tmp = "".join(secrets.choice("abcdefghjkmnpqrstuvwxyz23456789") for _ in range(8))
    salt = secrets.token_hex(16)
    c.execute("UPDATE users SET salt=?, hash=?, must_change=1 WHERE id=?", (salt, hpw(tmp, salt), r["id"]))
    c.execute("DELETE FROM sessions WHERE uid=?", (r["id"],))
    return {"password": tmp}

def guard(u, fn):  # con contraseña temporal solo se puede cambiar la clave o salir
    if u and u["must_change"] and fn not in (state, change_pw, logout):
        raise Err(403, "Tenés que cambiar tu contraseña antes de continuar")

ROUTES = {"/api/login": (login, False), "/api/register": (register, False), "/api/logout": (logout, True),
          "/api/book": (book, True), "/api/status": (status, True), "/api/pro": (pro_add, True),
          "/api/pro/del": (pro_del, True), "/api/spec": (spec_add, True), "/api/spec/del": (spec_del, True),
          "/api/user": (user_add, True), "/api/user/del": (user_del, True),
          "/api/password": (change_pw, True), "/api/user/reset": (user_reset, True)}

class H(BaseHTTPRequestHandler):
    def log_message(self, f, *a): pass

    def out(self, code, body, ctype="application/json; charset=utf-8"):
        if not isinstance(body, bytes): body = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        for k, v in (("Content-Type", ctype), ("Content-Length", len(body)), ("Cache-Control", "no-store"),
                     ("X-Content-Type-Options", "nosniff"),
                     ("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; "
                      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "
                      "connect-src 'self'; img-src 'self' data:")):
            self.send_header(k, str(v))
        self.end_headers(); self.wfile.write(body)

    def run(self, fn, b, need):
        c = db()
        try:
            u = auth(c, self.headers)
            if need and not u: raise Err(401, "Iniciá sesión")
            guard(u, fn)
            res = fn(c, u, b, self.client_address[0]); c.commit(); self.out(200, res)
        except Err as x: c.commit(); self.out(x.code, {"error": x.msg})
        except sqlite3.IntegrityError: c.rollback(); self.out(409, {"error": "Ya existe, o ese horario ya fue tomado"})
        except Exception as x:
            c.rollback(); traceback.print_exc()
            self.out(500, {"error": "Error interno del servidor: " + type(x).__name__ + " - " + str(x)[:120]})
        finally: c.close()

    def do_GET(self):
        p = urlparse(self.path).path
        if p in ("/", "/index.html"):
            with open(os.path.join(BASE, "index.html"), "rb") as f: return self.out(200, f.read(), "text/html; charset=utf-8")
        if p == "/api/state": return self.run(state, {}, True)
        self.out(404, {"error": "No encontrado"})

    def do_POST(self):
        r = ROUTES.get(urlparse(self.path).path)
        if not r: return self.out(404, {"error": "No encontrado"})
        n = int(self.headers.get("Content-Length") or 0)
        if n > 20000: return self.out(413, {"error": "Solicitud demasiado grande"})
        try: b = json.loads(self.rfile.read(n) or b"{}")
        except ValueError: return self.out(400, {"error": "JSON inválido"})
        if not isinstance(b, dict): return self.out(400, {"error": "JSON inválido"})
        self.run(r[0], b, r[1])

if __name__ == "__main__":
    init()
    host, port = os.environ.get("HOST", "127.0.0.1"), int(os.environ.get("PORT", "8000"))
    print("SaludUni funcionando en http://%s:%d  (Ctrl+C para detener)" % (host, port))
    ThreadingHTTPServer((host, port), H).serve_forever()
