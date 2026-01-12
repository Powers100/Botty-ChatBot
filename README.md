# Botty-ChatBot
**Interactive Learning Chatbot**

Botty is an interactive Python chatbot that can respond to greetings, farewells, provide the current time, fetch real-time weather information, and learn new intents over time. Users can teach the bot new responses and retrain it to improve accuracy.

The project is available in two versions:

Terminal (Command-Line) Version

Web App Version (Flask-based UI)

<h2>Features</h2>

**Intent Recognition:** Uses a machine learning model to classify user inputs into intents.

**Weather Integration:** Provides real-time weather information using location extraction.

**Time Responses:** Returns the current local time.

**Interactive Learning:** Learns new intents and responses directly from user input.

**Persistent Learning:** Saves learned responses to a JSON file for future sessions.

**Retrainable:** Allows retraining the model when new intents are added.

**Web Interface (Web App Version Only):** Interactive chat UI with live responses.

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

scikit-learn (ML model)

stanza (NER / location extraction)

requests (weather API calls)

flask & flask-socketio (Web App version only)

<h2>Setup</h2>

**Clone the repository:**

git clone <repo_url>

cd <repo_folder>

**Install dependencies:**

pip install -r requirements.txt

Ensure model.pkl exists in the project directory. This should contain your trained ML model and vectorizer. (Can be created running the train.py file)

Uncomment "stanza.download('en') # run once" in the weather.py file to install. Once complete, add the comment ("#") back

<h2>Terminal (Command-Line) Version</h2>

The terminal version allows you to interact with Botty directly through the command line.

<h3>Run the Terminal Chatbot</h3>
python chatbot.py

<h3>Usage</h3>

Chat with the bot directly in the terminal

Type quit to exit

Type retrain to retrain the ML model with newly learned intents
<h2>Terminal (Command-Line) Version</h2>

The terminal version allows you to interact with Botty directly through the command line.

<h3>Run the Terminal Chatbot</h3>
python chatbot.py

<h3>Usage</h3>

Chat with the bot directly in the terminal

Type retrain to retrain the ML model with newly learned intents if needed.

<h2>Web App Version</h2>

The web app version provides a browser-based chat interface built with Flask and Socket.IO, allowing real-time interactions and a more user-friendly experience.

<h3>Run the Web App</h3>
python app.py

Then open your browser and go to:

http://127.0.0.1:5000

<h3>Web App Features</h3>

Interactive chat interface

Real-time bot responses

Session-based conversation handling

Same learning and retraining capabilities as the terminal version

<h2>Learning New Intents</h2>
If the bot does not recognize an input the bot will prompt for the intent name.
If it’s a new intent, it will ask for a response.
The bot saves this to learned_data.json.
You can retrain the bot with retrain to integrate the new knowledge. (WebApp version does this automatically)

<h2>Files:</h2>

chatbot.py – Terminal-based interactive chatbot

app.py – Flask web application entry point

weather.py – Weather API handling and location extraction

model.pkl – Trained ML model and vectorizer

learned_data.json – Stores learned intents and responses

train.py – Script to train/retrain the ML model

<h2>Notes</h2>

Weather queries require a valid OpenWeatherMap API key set in weather.py.

The bot uses Stanza for named entity recognition to extract cities and locations.

New learned intents require retraining to be fully integrated into the ML model.
