from training_data import training_data
import json
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle

LEARNED_FILE = "learned_data.json"

print("Training start...")

all_training_data = training_data.copy()

if os.path.exists(LEARNED_FILE):
    with open(LEARNED_FILE, "r") as f:
        learned_data = json.load(f)
        all_training_data.extend(learned_data["training_data"])

texts = [x[0] for x in all_training_data]
labels = [x[1] for x in all_training_data]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(texts)

model = MultinomialNB()
model.fit(X, labels)

with open("model.pkl", "wb") as f:
    pickle.dump((model, vectorizer), f)

print("Model trained with learned data!")
