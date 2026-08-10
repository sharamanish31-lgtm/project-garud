import http.server
import socketserver
import urllib.request
import urllib.parse
import os

PORT = 80
TARGET_INTERNAL_APP = os.environ.get("TARGET_INTERNAL_APP", "http://127.0.0.1:8080")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

class PerimeterHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def handle_request(self):
        client_ip = self.client_address[0]
        path = self.path

        if ".." in path or "etc" in path or "passwd" in path or "select" in path or ".env" in path or ".git" in path or "config" in path:
            self.send_response(429)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Attack Blocked by Garud Perimeter!")
            try:
                msg = f"WARNING ATTACK BLOCKED\nIP: {client_ip}\nPayload: {path}"
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={urllib.parse.quote(msg)}&parse_mode=Markdown"
                urllib.request.urlopen(url, timeout=2)
            except:
                pass
            return

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None

            req = urllib.request.Request(
                f"{TARGET_INTERNAL_APP}{path}",
                data=body,
                headers=self.headers,
                method=self.command
            )
            with urllib.request.urlopen(req) as response:
                self.send_response(response.status)
                for key, val in response.headers.items():
                    self.send_header(key, val)
                self.end_headers()
                self.wfile.write(response.read())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Internal Error connecting to Garud Shield Core.")

with socketserver.TCPServer(("", PORT), PerimeterHandler) as httpd:
    print(f"Garud Perimeter Active on Port {PORT}")
    httpd.serve_forever()
