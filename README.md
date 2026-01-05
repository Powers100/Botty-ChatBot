# Botty-ChatBot
**Interactive Learning Chatbot**

An interactive Python chatbot that can respond to greetings, farewells, provide the current time, weather information, and learn new intents over time. Users can teach the bot new responses and retrain it for improved accuracy.

<h2>Features</h2>

**Intent Recognition:** Uses a machine learning model to classify user inputs into intents.

**Weather Integration:** Can provide real-time weather information using location extraction.

**Time Responses:** Can tell the current local time.

**Interactive Learning:** Learns new intents and responses directly from user input.

**Persistent Learning:** Saves learned responses to a JSON file for future sessions.

**Retrainable:** Users can retrain the model when new intents are added.

<h2>Requirements</h2>

Python 3.8+

Pre-trained model file: model.pkl

Learned data file: learned_data.json (created automatically if not present)

**Libraries:**

pickle

datetime

random

json

os

scikit-learn (for the ML model)

stanza (for NER/location extraction)

requests (for weather API calls)

<h2>Setup</h2>

**Clone the repository:**

git clone <repo_url>

cd <repo_folder>

**Install dependencies:**

pip install -r requirements.txt

Ensure model.pkl exists in the project directory. This should contain your trained ML model and vectorizer. (Can be created running the train.py file)

Uncomment "stanza.download('en') # run once" in the weather.py file to install. Once complete, add the comment ("#") back

<h2>Usage</h2>

**Run the chatbot:**

python chatbot.py

Chat with the bot via the command line.

Type quit to exit the chatbot.

Type retrain to retrain the ML model with new learned intents.

**Examples:**

You: hello

Bot: Hi!

You: whats the weather in Mexico City Mexico

Bot: The current weather in Mexico City, Mexico is clear sky with a temperature of 75°F.

You: what time is it

Bot: 03:25 PM

<h2>Learning New Intents</h2>
If the bot does not recognize an input the bot will prompt for the intent name.
If it’s a new intent, it will ask for a response.
The bot saves this to learned_data.json.
You can retrain the bot with retrain to integrate the new knowledge.

<h2>Files:</h2>

chatbot.py – Main interactive chatbot script.

weather.py – Handles weather API calls and location extraction.

model.pkl – Pre-trained ML model for intent classification.

learned_data.json – Stores learned user intents and responses.

train.py – Script to train/retrain the ML model.

<h2>Notes</h2>

Weather queries require a valid OpenWeatherMap API key set in weather.py.

The bot uses Stanza for named entity recognition to extract cities and locations.

New learned intents require retraining to be fully integrated into the ML model.
