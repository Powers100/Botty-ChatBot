from training_data import training_data
import json
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle

# --------------------
# Get the folder where this script is located
# --------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEARNED_FILE = os.path.join(BASE_DIR, "learned_data.json")
MODEL_FILE = os.path.join(BASE_DIR, "model.pkl")

print("Training start...")

# --------------------
# Prepare training data
# --------------------
all_training_data = training_data.copy()

if os.path.exists(LEARNED_FILE):
    with open(LEARNED_FILE, "r") as f:
        learned_data = json.load(f)
        all_training_data.extend(learned_data.get("training_data", []))
else:
    learned_data = {"training_data": [], "responses": {}}

texts = [x[0] for x in all_training_data]
labels = [x[1] for x in all_training_data]

# --------------------
# Train the model
# --------------------
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(texts)

model = MultinomialNB()
model.fit(X, labels)

# --------------------
# Save the model in the same folder as this script
# --------------------
with open(MODEL_FILE, "wb") as f:
    pickle.dump((model, vectorizer), f)

print("Model trained with learned data!")
