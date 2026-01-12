# app.py
from flask import render_template, session, jsonify
import time
from botEngine import app, socketio, init_conversation  # Import Flask app and Socket.IO instance


# Idle timeout etc.
IDLE_TIMEOUT = 5 * 60

def check_idle_timeout():
    last_active = session.get("last_active", time.time())
    now = time.time()
    if now - last_active > IDLE_TIMEOUT:
        session.clear()
    session["last_active"] = now
    session.modified = True
    print("Client timedout - reset")

@app.route("/")
def index():
    check_idle_timeout()
    return render_template("index.html")

@socketio.on("connect")
def handle_connect():
    session.clear()
    session["learning_step"] = None
    session["pending_input"] = None
    session["pending_intent"] = None
    session["last_active"] = time.time()
    session.modified = True
    print("Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    session.clear()
    session["learning_step"] = None
    session["pending_input"] = None
    session["pending_intent"] = None
    session.modified = True
    print("Client disconnected")

@app.route("/start", methods=["GET"])
def start_chat():
    init_conversation()
    print("New conversation started:", session["conversation_id"])
    return jsonify({"reply": "Chatbot is ready! Say hi to start."})

if __name__ == "__main__":
    socketio.run(app, debug=True)