"""Pruebas automáticas de la API de SaludUni.

Levantan el servidor con una base de datos temporal (nunca tocan saluduni.db)
y prueban los flujos principales. Ejecutar desde la raíz del repositorio:

    python -m unittest discover -s tests -v
"""
import datetime as dt, json, os, sys, tempfile, threading, unittest, urllib.error, urllib.request

TMP = tempfile.mkdtemp()
os.environ["DB_PATH"] = os.path.join(TMP, "test.db")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "saluduni1.2"))
import server  # noqa: E402


def setUpModule():
    global BASE, HTTPD
    server.init()
    HTTPD = server.ThreadingHTTPServer(("127.0.0.1", 0), server.H)
    threading.Thread(target=HTTPD.serve_forever, daemon=True).start()
    BASE = "http://127.0.0.1:%d" % HTTPD.server_address[1]


def tearDownModule():
    HTTPD.shutdown()


def call(path, body=None, tok=None):
    req = urllib.request.Request(BASE + "/api/" + path, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", **({"X-Token": tok} if tok else {})})
    try:
        with urllib.request.urlopen(req) as r:
            data = r.read()
            return r.status, (json.loads(data) if r.headers["Content-Type"].startswith("application/json") else data)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def next_slot(pid):
    """Primer horario libre del profesional a partir de mañana."""
    c = server.db()
    p = c.execute("SELECT * FROM pros WHERE id=?", (pid,)).fetchone()
    for i in range(1, 30):
        d = dt.date.today() + dt.timedelta(days=i)
        s = server.slots(c, p, d)
        if s:
            return d.isoformat(), s[0]
    raise AssertionError("sin horarios")


class SaludUniTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.admin = call("login", {"id": "admin", "password": "admin123"})[1]["token"]
        cls.alumno = call("register", {"id": "alumno.ci", "password": "clave123", "role": "Alumno"})[1]["token"]
        cls.medico = call("login", {"id": "medico1", "password": "medico123"})[1]["token"]

    def test_01_pagina_principal(self):
        with urllib.request.urlopen(BASE + "/") as r:
            self.assertEqual(r.status, 200)
            self.assertIn(b"SaludUni", r.read())

    def test_02_login_incorrecto(self):
        self.assertEqual(call("login", {"id": "admin", "password": "mala"})[0], 401)

    def test_03_reserva_y_doble_reserva(self):
        date, time = next_slot("p4")
        st, j = call("book", {"pid": "p4", "date": date, "time": time}, self.alumno)
        self.assertEqual(st, 200, j)
        self.assertTrue(j["id"].startswith("SU-"))
        self.assertEqual(call("book", {"pid": "p4", "date": date, "time": time}, self.alumno)[0], 409)

    def test_04_horario_fuera_de_atencion(self):
        date, _ = next_slot("p4")
        self.assertEqual(call("book", {"pid": "p4", "date": date, "time": "03:00"}, self.alumno)[0], 400)

    def test_05_permisos(self):
        self.assertEqual(call("backup", None, self.alumno)[0], 403)
        self.assertEqual(call("logs", {}, self.alumno)[0], 403)
        self.assertEqual(call("pro", {"name": "X", "spec": "Nutrición", "shift": "Tarde"}, self.alumno)[0], 403)
        self.assertEqual(call("state")[0], 401)

    def test_06_profesional_edita_solo_sus_horarios(self):
        h = [[0, "09:00", "12:00"], [2, "14:00", "17:00"]]
        self.assertEqual(call("pro/hours", {"pid": "p1", "dur": 30, "hours": h}, self.medico)[0], 200)
        self.assertEqual(call("pro/hours", {"pid": "p2", "dur": 30, "hours": h}, self.medico)[0], 403)
        bad = [[0, "09:00", "12:00"], [0, "11:00", "13:00"]]  # franjas superpuestas
        self.assertEqual(call("pro/hours", {"pid": "p1", "dur": 30, "hours": bad}, self.medico)[0], 400)

    def test_07_copia_de_la_base(self):
        st, data = call("backup", None, self.admin)
        self.assertEqual(st, 200)
        self.assertTrue(data.startswith(b"SQLite format 3"))

    def test_08_registro_de_actividad(self):
        st, j = call("logs", {}, self.admin)
        self.assertEqual(st, 200)
        acciones = {r["act"] for r in j["rows"]}
        self.assertTrue({"Ingreso", "Registro", "Ingreso fallido"} <= acciones, acciones)


if __name__ == "__main__":
    unittest.main()
