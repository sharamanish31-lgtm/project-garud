import json, time
from flask import request

DECOYS = ["/wp-login.php", "/wp-admin", "/admin", "/administrator",
          "/phpmyadmin", "/login.php", "/config.php", "/backup.zip"]

PAGE = ("<!doctype html><html><head><title>Admin Login</title></head>"
        "<body style='font-family:sans-serif;max-width:320px;margin:80px auto'>"
        "<h3>Administrator Login</h3><form method='post'>"
        "<input name='username' placeholder='Username'><br><br>"
        "<input name='password' type='password' placeholder='Password'><br><br>"
        "<button>Log in</button></form></body></html>")

def real_ip():
    xff = request.headers.get("X-Forwarded-For")
    if request.remote_addr in ("127.0.0.1", "::1") and xff:
        return xff.split(",")[0].strip()
    return request.remote_addr

def register(app, alert, executor):
    def trap():
        ip = real_ip()
        payload = request.path
        if request.method == "POST":
            u = request.form.get("username", "")[:40]
            payload = "login attempt user=%s pass_len=%d" % (u, len(request.form.get("password", "")))
        executor.submit(alert, ip, request.path, payload)
        print(json.dumps({"event": "honeypot_hit", "ip": ip, "path": request.path,
              "method": request.method, "ua": request.headers.get("User-Agent", "")[:120],
              "ts": int(time.time())}), flush=True)
        time.sleep(2)
        return PAGE, 200
    for i, p in enumerate(DECOYS):
        app.add_url_rule(p, endpoint="honeypot_%d" % i, view_func=trap, methods=["GET", "POST"])
