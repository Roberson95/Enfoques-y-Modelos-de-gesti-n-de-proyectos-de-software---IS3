"""Adaptador WSGI para PythonAnywhere (o cualquier hosting WSGI). Reutiliza server.py."""
import http, json, os
import server

server.init()
SEC = [("Cache-Control", "no-store"), ("X-Content-Type-Options", "nosniff"),
       ("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "
        "connect-src 'self'; img-src 'self' data:")]

def application(environ, start_response):
    def out(code, body, ctype="application/json; charset=utf-8"):
        if not isinstance(body, bytes): body = json.dumps(body, ensure_ascii=False).encode()
        start_response("%d %s" % (code, http.HTTPStatus(code).phrase),
                       [("Content-Type", ctype), ("Content-Length", str(len(body)))] + SEC)
        return [body]

    method, path, b = environ["REQUEST_METHOD"], environ.get("PATH_INFO", "/"), {}
    if method == "GET" and path in ("/", "/index.html"):
        with open(os.path.join(server.BASE, "index.html"), "rb") as f:
            return out(200, f.read(), "text/html; charset=utf-8")
    if method == "GET" and path == "/api/state":
        fn, need = server.state, True
    elif method == "POST" and path in server.ROUTES:
        fn, need = server.ROUTES[path]
        try: n = int(environ.get("CONTENT_LENGTH") or 0)
        except ValueError: n = 0
        if n > 20000: return out(413, {"error": "Solicitud demasiado grande"})
        try: b = json.loads(environ["wsgi.input"].read(n) or b"{}")
        except ValueError: return out(400, {"error": "JSON inválido"})
        if not isinstance(b, dict): return out(400, {"error": "JSON inválido"})
    else:
        return out(404, {"error": "No encontrado"})

    c = server.db()
    try:
        u = server.auth(c, {"X-Token": environ.get("HTTP_X_TOKEN", "")})
        if need and not u: raise server.Err(401, "Iniciá sesión")
        server.guard(u, fn)
        res = fn(c, u, b, environ.get("REMOTE_ADDR", "?")); c.commit(); return out(200, res)
    except server.Err as x:
        c.commit(); return out(x.code, {"error": x.msg})
    except server.sqlite3.IntegrityError:
        c.rollback(); return out(409, {"error": "Ya existe, o ese horario ya fue tomado"})
    except Exception as x:
        c.rollback(); server.traceback.print_exc()
        return out(500, {"error": "Error interno del servidor: " + type(x).__name__ + " - " + str(x)[:120]})
    finally:
        c.close()
