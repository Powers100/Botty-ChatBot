# botEngine.py
from flask import Flask, request, jsonify, session
import pickle, random, json, os, datetime, uuid, threading
from weather import get_weather
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from training_data import training_data  # default training data
from flask_socketio import SocketIO

# --------------------
# Get script folder
# --------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEARNED_FILE = os.path.join(BASE_DIR, "learned_data.json")
MODEL_FILE = os.path.join(BASE_DIR, "model.pkl")

# --------------------
# Flask setup
# --------------------
app = Flask(__name__)
app.secret_key = "dev-secret-key-" + str(uuid.uuid4())

# --------------------
# Initialize Socket.IO
# --------------------
socketio = SocketIO(app, cors_allowed_origins="*")

# --------------------
# Constants
# --------------------
CONFIDENCE_THRESHOLD = 0.55

# --------------------
# Utility functions
# --------------------
def get_time():
    return datetime.datetime.now().strftime("%I:%M %p")

FUNCTION_INTENTS = {
    "time": get_time,
    "weather": get_weather
}

def init_conversation():
    session["conversation_id"] = str(uuid.uuid4())
    session["learning_step"] = None
    session["pending_input"] = None
    session["pending_intent"] = None
    # print("DEBUG: init_conversation ran")

# --------------------
# Load learned data
# --------------------
if os.path.exists(LEARNED_FILE):
    with open(LEARNED_FILE, "r") as f:
        learned_data = json.load(f)
else:
    learned_data = {"training_data": [], "responses": {}}

# --------------------
# Merge default training data with learned training data
# --------------------
def get_all_training_data():
    return training_data.copy() + learned_data.get("training_data", [])

def get_texts_labels():
    all_training = get_all_training_data()
    texts = [x[0] for x in all_training]
    labels = [x[1] for x in all_training]
    return texts, labels

# --------------------
# Train or load model
# --------------------
if os.path.exists(MODEL_FILE):
    with open(MODEL_FILE, "rb") as f:
        model, vectorizer = pickle.load(f)
else:
    texts, labels = get_texts_labels()
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(texts)
    model = MultinomialNB()
    model.fit(X, labels)
    with open(MODEL_FILE, "wb") as f:
        pickle.dump((model, vectorizer), f)

# --------------------
# Base and learned responses
# --------------------
BASE_RESPONSES = {
    "greeting": ["Hi!", "Hello!", "Hey there!"],
    "farewell": ["Goodbye!", "See you later!"],
    "weather": [],
    "time": [get_time]
}

def update_responses_in_memory():
    """Merge BASE_RESPONSES with learned responses for in-memory use."""
    global responses
    responses = BASE_RESPONSES.copy()
    for k, v in learned_data.get("responses", {}).items():
        if k in responses:
            responses[k].extend(v)
        else:
            responses[k] = v

update_responses_in_memory()

# --------------------
# Retrain function
# --------------------
def retrain_model():
    global model, vectorizer
    texts, labels = get_texts_labels()
    if not texts:
        return "No training data available."

    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(texts)

    model = MultinomialNB()
    model.fit(X, labels)

    with open(MODEL_FILE, "wb") as f:
        pickle.dump((model, vectorizer), f)

    return "Model retrained successfully."

# --------------------
# Chat route
# --------------------
@app.route("/chat", methods=["POST"])
def chat():
    if "conversation_id" not in session:
        init_conversation()
        # print("DEBUG: Conversation auto-initialized")

    data = request.get_json()
    user_input = data.get("message", "").strip().lower()

    if not user_input:
        return jsonify({"reply": "Please type something."})

    if user_input == "retrain":
        msg = retrain_model()
        update_responses_in_memory()
        session.clear()
        # print("DEBUG: Everything in session set to default6")
        return jsonify({"reply": msg})
    
    # print("DEBUG: CHAT HIT:", user_input, session.get("learning_step"))

    # --------------------
    # STEP 1: Awaiting intent
    # --------------------
    if session["learning_step"] == "awaiting_intent":
        # print("DEBUG: learning step is awaiting intent")
        intent_name = user_input
        session["pending_intent"] = intent_name

        # Save new training data
        learned_data["training_data"].append([session["pending_input"], intent_name])
        with open(LEARNED_FILE, "w") as f:
            json.dump(learned_data, f, indent=2)

        # Decide if we need user-provided response
        if intent_name not in FUNCTION_INTENTS:
            session["learning_step"] = "awaiting_response"
            return jsonify({"reply": "What should I say in response?"})
        else:
            # print("DEBUG: retraining and clearing session")
            retrain_model()
            update_responses_in_memory()
            session.clear()
            # print("DEBUG: Everything in session set to default4")
            return jsonify({
                "reply": f"Got it! '{intent_name}' will use its built-in function."
            })

    # --------------------
    # STEP 2: Awaiting response text
    # --------------------
    if session["learning_step"] == "awaiting_response":
        # print("DEBUG: learning step is awaiting response")
        intent_name = session["pending_intent"]
        response_text = user_input

        # Save response to JSON
        learned_data["responses"].setdefault(intent_name, []).append(response_text)
        with open(LEARNED_FILE, "w") as f:
            json.dump(learned_data, f, indent=2)

        # Update in-memory responses and retrain
        update_responses_in_memory()
        retrain_model()

        session.clear()
        # print("DEBUG: Everything in session set to default5")
        return jsonify({"reply": "Thanks! I've saved this. The bot is now updated."})

    # --------------------
    # NORMAL PREDICTION FLOW
    # --------------------
    X = vectorizer.transform([user_input])
    probs = model.predict_proba(X)[0]
    intent_index = probs.argmax()
    intent = model.classes_[intent_index]
    confidence = probs[intent_index]

    # Low confidence → learn
    if confidence < CONFIDENCE_THRESHOLD:
        session["learning_step"] = "awaiting_intent"
        session["pending_input"] = user_input
        return jsonify({
            "reply": (
                f"I'm not confident about my intent ({confidence:.2f}). "
                f"What intent should this be?\n"
                f"Existing intents: {list(responses.keys())}"
            )
        })

    # FUNCTION INTENTS
    if intent in FUNCTION_INTENTS:
        # print(f"DEBUG: intent is in fuction intents: {intent}")
        if intent == "weather":
            def notify(msg):
                socketio.emit("bot_message", msg)
                    # Immediately notify user
            notify("Getting data...")  # <- this will show immediately
            reply = FUNCTION_INTENTS[intent](user_input)
        else:
            reply = FUNCTION_INTENTS[intent]()    
        return jsonify({"reply": reply})

    # UNKNOWN INTENT
    if intent not in responses:
        # print(f"DEBUG: intent is not in responses: {intent}")
        session["learning_step"] = "awaiting_intent"
        session["pending_input"] = user_input
        return jsonify({
            "reply": "I don't know how to respond. What intent should this be? Type the intent name (or a new one):"
        })

    # NORMAL RESPONSE
    response = random.choice(responses[intent])
    reply = response() if callable(response) else response
    return jsonify({"reply": reply})

# --------------------
# Run app
# --------------------
if __name__ == "__main__":
    socketio.run(app, debug=True)
