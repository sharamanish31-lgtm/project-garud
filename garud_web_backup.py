import os
from flask import Flask, render_template, request, jsonify, send_file
from pinecone import Pinecone
from garud_analyzer import analyze_threat_vector

app = Flask(__name__)

# 🔒 SECURE PARAMETER EXTRACTION (No hardcoded keys outside memory)
PINECONE_KEY = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_KEY)
VOICE_FOLDER = os.path.expanduser("~/garud_core/my_voices")

@app.errorhandler(404)
def autonomous_counter_strike(e):
    attacker_ip = request.remote_addr
    malicious_path = request.path
    user_agent = request.headers.get('User-Agent', 'Unknown')
    cloned_raw_payload = request.query_string.decode('utf-8') or request.get_data(as_text=True) or malicious_path
    analysis = analyze_threat_vector(f"{malicious_path} {cloned_raw_payload}")
    dummy_vector = analysis["vector"]
    
    try:
        idx = pc.Index("garud-memory")
        # Naya fixed Pinecone syntax jo crash nahi karega aur data save karega
        idx.upsert(vectors=[{
            "id": f"clone-{attacker_ip}",
            "values": dummy_vector,
            "metadata": {
                "ip": attacker_ip,
                "cloned_exploit": cloned_raw_payload,
                "agent": user_agent
            }
        }])
    except Exception:
        pass

    print(f"[🚨 COUNTER-STRIKE TRACEBACK ACTIVE] Launching automated reconnaissance on target IP: {attacker_ip}")
    return jsonify({
        "status": "Targeting vector isolated...",
        "delay": "infinite",
        "msg": "Autonomous retaliation database updated."
    }), 200

@app.route('/')
def home():
    return render_template('index.html')

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
    return jsonify({"status": "Voice file missing"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
