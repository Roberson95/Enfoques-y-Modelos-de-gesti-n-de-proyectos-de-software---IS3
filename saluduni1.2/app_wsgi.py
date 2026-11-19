"""Adaptador WSGI para PythonAnywhere (o cualquier hosting WSGI). Reutiliza server.py."""
import http, json, os
import server

server.init()

def application(environ, start_response):
    def out(code, body, ctype="application/json; charset=utf-8", extra=()):
        if not isinstance(body, bytes): body = json.dumps(body, ensure_ascii=False).encode()
        start_response("%d %s" % (code, http.HTTPStatus(code).phrase),
                       [("Content-Type", ctype), ("Content-Length", str(len(body)))] + server.SEC_HEADERS + list(extra))
        return [body]

    method, path, b = environ["REQUEST_METHOD"], environ.get("PATH_INFO", "/"), {}
    if method == "GET" and path in ("/", "/index.html"):
        with open(os.path.join(server.BASE, "index.html"), "rb") as f:
            return out(200, f.read(), "text/html; charset=utf-8")
    if method == "GET" and path in server.GET_ROUTES:
        fn, need = server.GET_ROUTES[path], True
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
    return out(*server.handle(fn, b, need, {"X-Token": environ.get("HTTP_X_TOKEN", "")},
                              environ.get("HTTP_X_REAL_IP") or environ.get("REMOTE_ADDR", "?")))
