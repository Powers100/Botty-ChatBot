import requests
import stanza
from AbrvMapNames import US_STATES, COUNTRY_MAP

API_KEY = "2f13259095d6895eecc3969ccbb91d43"

GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"
ONECALL_URL = "https://api.openweathermap.org/data/2.5/weather"

# stanza.download('en') # run once
nlp = stanza.Pipeline(lang='en', processors='tokenize,ner', verbose=False)

def ner_location_tokens(text):
    doc = nlp(text)
    tokens = []
    covered_words = set()
    added = False

    for sent in doc.sentences:
        sent_words = [t.text.lower() for t in sent.tokens]

        for ent in sent.ents:
            if ent.type in ("GPE", "LOC"):
                entity_words = ent.text.lower().split()

                # Only append 'city' if next word in sentence is 'city' and it's not already in entity
                try:
                    last_index = sent_words.index(entity_words[-1])
                    if last_index + 1 < len(sent_words):
                        next_word = sent_words[last_index + 1]
                        if next_word == "city" and "city" not in entity_words and not added:
                            entity_words[0] += " city"
                            added = True
                except ValueError:
                    pass  # fallback

                token_text = " ".join(entity_words)
                tokens.append(token_text)

                # Add individual words to covered_words
                for w in entity_words:
                    covered_words.add(w)

    # print(f"DEBUG: tokens: {tokens}, covered words: {covered_words}")
    return tokens, covered_words

IGNORE_WORDS = {"the", "a", "an", "at", "on", "for", "to", "of"}

def extract_location(user_input):
    text = user_input.replace("?", "").replace(".", "").strip()
    words = text.lower().split()

    ner_tokens, covered = ner_location_tokens(text)

    city_parts = []
    state = ""
    country = ""

    # --- Use NER for city (remove any states or countries if left in) ---
    if ner_tokens:
        ner_city_words = ner_tokens[0].lower().split()

        cleaned = []
        for i, w in enumerate(ner_city_words):
            if w in COUNTRY_MAP and i + 1 < len(ner_city_words) and ner_city_words[i + 1] == "city":
                cleaned.append(w)
                continue
            if w in COUNTRY_MAP:
                continue
            if w.upper() in COUNTRY_MAP.values():
                continue
            if w in US_STATES:
                continue
            if w.upper() in US_STATES.values():
                continue
            cleaned.append(w)

        city_parts = cleaned

    # --- Scan leftover words for state / country ---
    for i, word in enumerate(words):
        # Special case for in
        if word == "in" and i > 0:
            prev_word = words[i-1]
            # print(f"DEBUG: prev_word {prev_word}")
            if prev_word in covered: # If the previous word is a city, then use "in" as indiana
                state = "IN"
                country = "US"
                break
            continue

        # Ignore prepositions / filler words
        if word in IGNORE_WORDS:
            continue

        if word in COUNTRY_MAP:
            country = COUNTRY_MAP[word]
            break

        elif word.upper() in COUNTRY_MAP.values():
            country = word.upper()
            break
            
        elif word in US_STATES:
            state = US_STATES[word]
            country = "US"
            break

        elif word.upper() in US_STATES.values():
            state = word.upper()
            country = "US"
            break

    # Virginia special case
    if state == "VA":
        state = "VA."

    LOCATION_KEYWORDS = {"in", "at", "near", "around", "for"}

    # --- Fallback (if no city is detected by NER) ---
    # Take all words before the detected state or country and after a preposition
    if not city_parts:
        # print("DEBUG: Fallback, no city detected by NER")

        LOCATION_KEYWORDS = {"in", "at", "near", "around", "for"}
        start = 0

        # Find last location keyword
        for i, word in enumerate(words):
            if word in LOCATION_KEYWORDS:
                start = i + 1

        end = len(words)

        # If US state is present
        if state:
            for i in range(start, len(words)):
                word = words[i]
                if word in US_STATES or word.upper() in US_STATES.values():
                    end = i
                    break

        # Else if country is present
        elif country:
            for i in range(start, len(words)):
                word = words[i]
                if word in COUNTRY_MAP or word.upper() in COUNTRY_MAP.values():
                    end = i
                    break

        city_parts = [
            w for w in words[start:end]
            if w not in IGNORE_WORDS
        ]

    city = " ".join(city_parts)

    # print(f"DEBUG: country: {country}")

    return city.title(), state, country

def get_coordinates(user_input):
    city, state, country = extract_location(user_input)

    # If no city, cannot proceed
    if not city:
        inputCity = input("What city should I look for the weather in? ")
        city, state, country = extract_location(inputCity)

    q = city
    if state:
        q += f",{state}"
    if country:
        q += f",{country}"

    params = {
        "q": q,
        "limit": 1,
        "appid": API_KEY
    }

    response = requests.get(GEOCODE_URL, params=params, timeout=5)

    # print("DEBUG geocode query:", q)
    # print("DEBUG status:", response.status_code)
    # print("DEBUG response:", response.text)

    if response.status_code != 200:
        return None

    data = response.json()
    if not data:
        return None

    # If we specified a state, pick the result matching that state
    if state:
        for item in data:
            if item.get("state", "").upper() == state.upper().replace(".", ""):  # remove period for comparison
                return item["lat"], item["lon"], item["name"], state,country
        # fallback: take the first one
        return data[0]["lat"], data[0]["lon"], data[0]["name"], state, country

    # No state specified: use API's state if available
    state_from_api = data[0].get("state", "")
    if not state and state_from_api:
        state = state_from_api

    # No state specified, just return first
    return data[0]["lat"], data[0]["lon"], data[0]["name"], state, country

def get_weather(user_input):
    coords = get_coordinates(user_input)

    if not coords:
        return "Sorry, I couldn't find that location."

    lat, lon, city_name, state, country = coords

    # Special Handling for VA
    if state == "VA.":
        state = "VA" 

    params = {
        "lat": lat,
        "lon": lon,
        "units": "imperial",
        "appid": API_KEY
    }

    response = requests.get(ONECALL_URL, params=params, timeout=5)

    # print("DEBUG status:", response.status_code)
    # print("DEBUG response:", response.text)

    if response.status_code != 200:
        return "Sorry, I couldn't retrieve the weather data."

    data = response.json()

    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]

    if state != "":
        return (
            f"The current weather in {city_name}, {state} is "
            f"{description} with a temperature of {temp:.0f}°F."
        )
    else:
        CODE_TO_COUNTRY = {v: k.title() for k, v in COUNTRY_MAP.items()}

        return (
            f"The current weather in {city_name}, {CODE_TO_COUNTRY.get(country, country)} is "
            f"{description} with a temperature of {temp:.0f}°F."
        )
