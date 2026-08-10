import os
import json
import time
import gzip
import io
import requests
from flask import Flask, render_template, request, jsonify, send_file, make_response
from pinecone import Pinecone
from concurrent.futures import ThreadPoolExecutor
from garud_analyzer import analyze_threat_vector

# System application explicit paths definition config
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
app = Flask(__name__, template_folder=template_dir)
bg_executor = ThreadPoolExecutor(max_workers=4)

# Dynamic runtime tracking layers
IP_RATE_TRACKER = {}
INTERACTIVE_DECISION_MAP = {}  # Dynamic telemetry control block

PINECONE_KEY = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_KEY) if PINECONE_KEY else None
VOICE_FOLDER = os.path.expanduser("~/garud_core/my_voices")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def dispatch_telegram_interactive_alert(attacker_ip, malicious_path, cloned_raw_payload):
    if not BOT_TOKEN or not CHAT_ID: return
    url = f"https://telegram.org{BOT_TOKEN}/sendMessage"
    text_payload = (
        f"🚨 *GARUD TARGET INTERCEPTED* 🚨\n\n"
        f"👤 *Source Node:* `{attacker_ip}`\n"
        f"🎯 *Target Route:* `{malicious_path}`\n"
        f"🧬 *Payload Stored:* `{cloned_raw_payload[:100]}`\n\n"
        f"⚡ *CHOOSE ACTION POSTURE WITHIN 0.01s:* \n"
        f"Otherwise, Auto-Pilot Protocol engages Sticky Tarpit."
    )
    reply_markup = {
        "inline_keyboard": [[
            {"text": "💥 LAUNCH BOMB", "callback_data": f"bomb_{attacker_ip}"},
            {"text": "🕸️ STICKY TRAP", "callback_data": f"tarpit_{attacker_ip}"}
        ]]
    }
    try:
        requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": text_payload,
            "parse_mode": "Markdown",
            "reply_markup": reply_markup
        }, timeout=3)
    except:
        pass

def async_pinecone_upsert(attacker_ip, user_agent, cloned_raw_payload, malicious_path, live_calculated_vector):
    if not pc: return
    try:
        idx = pc.Index("garud-memory")
        unique_id = f"clone-{attacker_ip}-{os.urandom(3).hex()}"
        idx.upsert(vectors=[{
            "id": unique_id,
            "values": live_calculated_vector,
            "metadata": {
                "ip": attacker_ip,
                "cloned_exploit": cloned_raw_payload,
                "agent": user_agent
            }
        }])
    except:
        pass

@app.errorhandler(404)
def autonomous_counter_strike(e):
    attacker_ip = request.remote_addr
    current_timestamp = time.time()
    
    if attacker_ip not in IP_RATE_TRACKER:
        IP_RATE_TRACKER[attacker_ip] = []
        
    IP_RATE_TRACKER[attacker_ip] = [t for t in IP_RATE_TRACKER[attacker_ip] if current_timestamp - t < 10]
    
    if len(IP_RATE_TRACKER[attacker_ip]) >= 5:
        return jsonify({
            "status": "Circuit breaker isolation triggered...",
            "error": "Rate limit exceeded. Connection throttled globally."
        }), 429

    IP_RATE_TRACKER[attacker_ip].append(current_timestamp)
    malicious_path = request.path
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    try:
        cloned_raw_payload = request.query_string.decode('utf-8', errors='ignore') or request.path
    except:
        cloned_raw_payload = "undecodable_stream"

    analysis = analyze_threat_vector(f"{malicious_path} {cloned_raw_payload}")
    live_calculated_vector = analysis["vector"]

    bg_executor.submit(dispatch_telegram_interactive_alert, attacker_ip, malicious_path, cloned_raw_payload)
    bg_executor.submit(async_pinecone_upsert, attacker_ip, user_agent, cloned_raw_payload, malicious_path, live_calculated_vector)
    
    time.sleep(0.01)
    selected_posture = INTERACTIVE_DECISION_MAP.get(attacker_ip, "tarpit")

    if selected_posture == "bomb":
        import gzip
        import io
        from flask import make_response
        raw_garbage = ("0xDEADBEEF_GARUD_CORE_SECURITY_MATRIX_" * 40000).encode('utf-8')
        out = io.BytesIO()
        with gzip.GzipFile(fileobj=out, mode="w") as f:
            f.write(raw_garbage)
        compressed_data = out.getvalue()
        response = make_response(compressed_data)
        response.headers["Content-Encoding"] = "gzip"
        response.headers["Content-Type"] = "text/plain"
        response.headers["Content-Length"] = str(len(compressed_data))
        return response, 200
    else:
        def generate_slow_stream():
            for _ in range(5):
                yield b" "  
                time.sleep(1)
        return app.response_class(generate_slow_stream(), content_type="text/plain", status=200)

@app.route('/telegram-callback', methods=['POST'])
def telegram_webhook_callback():
    data = request.get_json() or {}
    if "callback_query" in data:
        callback_data = data["callback_query"]["data"]
        action, target_ip = callback_data.split("_", 1)
        INTERACTIVE_DECISION_MAP[target_ip] = action
        callback_id = data["callback_query"]["id"]
        requests.post(f"https://telegram.org{BOT_TOKEN}/answerCallbackQuery", json={
            "callback_query_id": callback_id,
            "text": f"Garud Order Executed: {action.upper()} activated against node."
        })
    return jsonify({"status": "processed"}), 200

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/jarvis')
def jarvis_dashboard():
    return render_template('jarvis.html')

@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json() or {}
    user_text = data.get('text', '').lower()
    audio_file_name = "default.mp3"
    
    if "hello" in user_text or "hi" in user_text:
        audio_file_name = "hello.mp3"
    elif "status" in user_text or "server" in user_text:
        audio_file_name = "status.mp3"
        
    audio_path = os.path.join(VOICE_FOLDER, audio_file_name)
    if os.path.exists(audio_path):
        return send_file(audio_path, mimetype='audio/mpeg')
        return jsonify({"status": "Voice file missing"}), 404
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
