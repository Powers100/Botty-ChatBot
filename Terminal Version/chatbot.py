import pickle
import datetime
import random
import json
import os
from weather import get_weather, extract_location


def get_time():
    return datetime.datetime.now().strftime("%I:%M %p")

CONFIDENCE_THRESHOLD = 0.55
LEARNED_FILE = "learned_data.json"
FUNCTION_INTENTS = {
    "time": get_time,
    "weather": get_weather
}

if os.path.exists(LEARNED_FILE):
    with open(LEARNED_FILE, "r") as f:
        learned_data = json.load(f)
else:
    learned_data = {
        "training_data": [],
        "responses": {}
    }

with open("model.pkl", "rb") as f:
    model, vectorizer = pickle.load(f)

BASE_RESPONSES = {
    "greeting": ["Hi!", "Hello!", "Hey there!"],
    "farewell": ["Goodbye!", "See you later!"],
    "weather": [],
    "time": [get_time]
}

responses = BASE_RESPONSES.copy()
responses.update(learned_data["responses"])

print("Chatbot is running. Type 'quit' to exit or 'retrain' to retrain model.")

while True:
    user_input = input("You: ")
    user_input = user_input.lower()

    if user_input == "quit":
        break

    elif user_input == "retrain":
        print("Bot: Retraining model...")
        os.system("python train.py")
        print("Bot: Done. Restart me!")
        break

    elif user_input in learned_data:
        print("Bot:", learned_data[user_input])
        continue

    X = vectorizer.transform([user_input])

    probs = model.predict_proba(X)[0]
    intent_index = probs.argmax()
    intent = model.classes_[intent_index]
    confidence = probs[intent_index]

    # print(f"DEBUG intent: {intent}")

    if confidence < CONFIDENCE_THRESHOLD:
        print(f"Bot: I'm not confident about my intent ({confidence:.2f}).")
        print("Bot: What intent should this be?")
        print(f"Bot: Existing intents: {list(responses.keys())}")
        print("Bot: Type an intent name (or create a new one):")

        intent_name = input("You (intent): ").strip().lower()

        # Always save training example
        learned_data["training_data"].append([user_input, intent_name])

        if intent_name in FUNCTION_INTENTS:
            print(f"Bot: Got it! '{intent_name}' will use its built-in function.")
        else:
            print("Bot: What should I say in response?")
            new_response = input("You (response): ").strip()

            if intent_name not in learned_data["responses"]:
                learned_data["responses"][intent_name] = []

            learned_data["responses"][intent_name].append(new_response)

        with open(LEARNED_FILE, "w") as f:
            json.dump(learned_data, f, indent=2)

        print("Bot: Thanks! I've saved this. Retrain me to learn it.")
        continue


    if intent not in responses:
        print("Bot: I don't know how to respond.")
        print("Bot: Is this a NEW intent or an EXISTING one?")
        print("Bot: Type the intent name (or a new one):")

        intent_name = input("You (intent): ").strip().lower()

        print("Bot: What should I say in response?")
        new_response = input("You (response): ").strip()

        # Save training example
        learned_data["training_data"].append([user_input, intent_name])

        # Save response
        if intent_name not in learned_data["responses"]:
            learned_data["responses"][intent_name] = []

        learned_data["responses"][intent_name].append(new_response)

        with open(LEARNED_FILE, "w") as f:
            json.dump(learned_data, f, indent=2)

        print("Bot: Got it! Restart me to retrain with this new knowledge.")
        continue

    if intent == "weather":
        print("Bot:", get_weather(user_input))
        continue
    
    response = random.choice(responses[intent])

    if callable(response):
        print("Bot:", response())
    else:
        print("Bot:", response)
