import http.server
import socketserver
import urllib.request
import urllib.parse
import os
import time
import re
import json

PORT = 80
TARGET_INTERNAL_APP = os.environ.get("TARGET_INTERNAL_APP", "http://127.0.0.1:8080")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

LOG_FILE = "/app/logs/perimeter_log.jsonl"

attack_history = {}
MAX_ATTACKS = 3
BLOCK_DURATION = 300  # 5 minutes ban

request_log = {}
RATE_LIMIT_COUNT = 20
RATE_LIMIT_WINDOW = 10  # seconds

BLOCKED_PATTERNS = re.compile(
    r"(\.\.|etc|passwd|select|union|drop\s+table|\.env|\.git|config|<script|javascript:|onerror\s*=|%00|eval\()",
    re.IGNORECASE
)

def log_event(ip, path, action, extra=None):
    entry = {"time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), "ip": ip, "path": path, "action": action}
    if extra:
        entry.update(extra)
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass

def is_ip_banned(ip):
    if ip in attack_history:
        count, first_seen, banned_until = attack_history[ip]
        if banned_until and time.time() < banned_until:
            return True
    return False

def record_attack(ip):
    now = time.time()
    if ip in attack_history:
        count, first_seen, banned_until = attack_history[ip]
        count += 1
        if count >= MAX_ATTACKS:
            banned_until = now + BLOCK_DURATION
        attack_history[ip] = (count, first_seen, banned_until)
    else:
        attack_history[ip] = (1, now, None)
    return attack_history[ip][0]

def is_rate_limited(ip):
    now = time.time()
    timestamps = [t for t in request_log.get(ip, []) if now - t < RATE_LIMIT_WINDOW]
    timestamps.append(now)
    request_log[ip] = timestamps
    return len(timestamps) > RATE_LIMIT_COUNT

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={urllib.parse.quote(msg)}&parse_mode=Markdown"
        urllib.request.urlopen(url, timeout=2)
    except Exception:
        pass

class PerimeterHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # default access log band, ab hum apna JSON log rakhte hain

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def handle_request(self):
        client_ip = self.client_address[0]
        path = self.path

        if is_ip_banned(client_ip):
            log_event(client_ip, path, "banned_ip_blocked")
            self.send_response(429)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"IP Temporarily Banned by Garud Perimeter due to repeated attacks.")
            return

        if is_rate_limited(client_ip):
            log_event(client_ip, path, "rate_limited")
            self.send_response(429)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Too Many Requests - Rate Limit Exceeded.")
            return

        if BLOCKED_PATTERNS.search(path):
            count = record_attack(client_ip)
            log_event(client_ip, path, "attack_blocked", {"attempt": count})
            self.send_response(429)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Attack Blocked by Garud Perimeter!")
            status_line = "IP now temporarily BANNED (5 min)" if count >= MAX_ATTACKS else f"Attempt {count}/{MAX_ATTACKS}"
            send_telegram(f"WARNING ATTACK BLOCKED\nIP: {client_ip}\nPayload: {path}\nStatus: {status_line}")
            return

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            req = urllib.request.Request(f"{TARGET_INTERNAL_APP}{path}", data=body, headers=self.headers, method=self.command)
            with urllib.request.urlopen(req) as response:
                self.send_response(response.status)
                for key, val in response.headers.items():
                    self.send_header(key, val)
                self.end_headers()
                self.wfile.write(response.read())
            log_event(client_ip, path, "allowed")
        except Exception as e:
            log_event(client_ip, path, "backend_error", {"error": str(e)})
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Internal Error connecting to Garud Shield Core.")

class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

with ThreadedServer(("", PORT), PerimeterHandler) as httpd:
    print(f"Garud Perimeter Active on Port {PORT}")
    httpd.serve_forever()
