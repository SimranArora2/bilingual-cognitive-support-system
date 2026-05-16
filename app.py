from flask import Flask, request, jsonify, render_template, session
import joblib
from datetime import datetime
import json
import os
import random
# import pickle

# with open("model.pkl", "rb") as f:
#     model = pickle.load(f)

# with open("vectorizer.pkl", "rb") as f:
#     vectorizer = pickle.load(f)

app = Flask(__name__)
app.secret_key = "cognitive_support_key"

model = joblib.load("model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

# ---------------- TEXT NORMALIZATION ----------------
def normalize_text(text):
    text = text.lower()
    replacements = {
        "mujhe": "i", "main": "i", "mera": "my", "meri": "my", "mere": "my",
        "hum": "we", "hume": "we",
        "tension": "stress", "tension hai": "stress", "pareshan": "stress",
        "bojh": "burden", "darr": "fear", "ghabrahat": "anxiety",
        "ghabra raha": "anxious", "soch soch ke": "overthinking",
        "dimag kharab": "stress", "dimag phat raha": "stress",
        "thak gaya": "tired", "thak gayi": "tired",
        "dukhi": "sad", "udaas": "sad", "rona aa raha": "sad",
        "ro raha": "sad", "akela": "lonely", "akelapan": "lonely",
        "tanha": "lonely", "tanhai": "lonely", "koi nahi hai": "lonely",
        "ignore kar rahe": "ignored", "koi baat nahi karta": "lonely",
        "confuse": "confused", "confused hoon": "confused",
        "samajh nahi aa raha": "confused", "samajh nahi aa rahi": "confused",
        "kya karu": "what to do", "kya karun": "what to do",
        "kya sahi hai": "confused", "kya galat hai": "confused",
        "decision nahi le pa raha": "decision problem",
        "faisla nahi ho raha": "decision problem",
        "mann nahi lag raha": "no motivation", "mann nahi karta": "no motivation",
        "iccha nahi ho rahi": "no motivation", "himmat nahi": "low confidence",
        "give up karna": "give up", "thak chuka hoon": "burnout",
        "energy nahi hai": "low energy",
        "padhai": "study", "padhna": "study",
        "samajh nahi aata": "not understanding", "yaad nahi hota": "memory problem",
        "focus nahi": "low focus", "dhyaan nahi lag raha": "low focus",
        "job nahi mil rahi": "no job", "naukri": "job", "kaam": "work",
        "salary kam": "low salary", "promotion nahi": "no growth",
        "career ruk gaya": "career stuck", "future ka darr": "career fear",
        "paisa": "money", "paise nahi": "no money", "karz": "loan",
        "udhaar": "loan", "kharcha": "expenses", "mehenga": "expensive",
        "bacha nahi pa raha": "no savings",
        "dard": "pain", "tabiyat kharab": "sick", "kamjor": "weak",
        "thakan": "fatigue", "neend nahi": "sleep problem", "bhook nahi": "appetite loss",
        "jhagda": "fight", "ladayi": "fight", "dhokha": "betrayal",
        "ignore kar raha": "ignored", "trust nahi": "trust issue",
        "log kya kahenge": "social fear", "log judge karenge": "judgement fear",
        "baat karne mein darr": "social anxiety", "public mein darr": "stage fear",
        "logo se milne mein problem": "social anxiety", "awkward feel": "social discomfort"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

# ---------------- LANGUAGE DETECTION ----------------
def detect_language(text):
    hindi_chars = any('\u0900' <= ch <= '\u097F' for ch in text)
    if hindi_chars:
        return "hi"
    hinglish_words = ["hai", "nahi", "kya", "kaise", "mujhe", "mera", "kyun",
                      "aur", "bahut", "hoon", "raha", "rahi", "kar", "se"]
    if any(w in text.lower().split() for w in hinglish_words):
        return "hi"
    return "en"

# ---------------- MOOD DETECTION ----------------
def detect_mood(text):
    text = text.lower()
    if any(w in text for w in ["stressed", "anxious", "pressure", "overwhelmed", "tired"]):
        return "stressed"
    if any(w in text for w in ["sad", "lonely", "alone", "depressed", "empty"]):
        return "sad"
    if any(w in text for w in ["confused", "lost", "don't know", "uncertain"]):
        return "confused"
    if any(w in text for w in ["motivated", "excited", "ready", "focused"]):
        return "motivated"
    return "calm"

'''# ---------------- ACTION PLANNER ----------------
def generate_action_plan(detected_intents, confidence, mood, lang, mode="normal"):
    
    plans = {
        "Stress": {
            "en": ["Let's slow down — write your top 3 worries", "Pick just ONE to handle today", "The rest can wait — you don't need to fix everything now"],
            "hi": ["चलो थोड़ा धीरे चलते हैं — अपनी 3 सबसे बड़ी चिंताएं लिखो", "आज सिर्फ 1 चीज पर ध्यान दो", "बाकी बाद में भी हो सकता है"]
        },
        "Career": {
            "en": ["Identify one small career task for today", "Research one role or skill you're curious about", "Build a simple 30-day improvement plan"],
            "hi": ["आज एक छोटा करियर टास्क तय करो", "एक स्किल या रोल के बारे में जानो", "30 दिन की योजना बनाओ"]
        },
        "Learning": {
            "en": ["Choose ONE topic only — not five", "Use 25-minute focused study blocks", "Revise using active recall, not re-reading"],
            "hi": ["सिर्फ एक टॉपिक चुनो", "25 मिनट फोकस में पढ़ो", "एक्टिव तरीके से रिविजन करो"]
        },
        "Loneliness": {
            "en": ["Message one person you trust right now", "Do one small thing you genuinely enjoy", "Avoid self-blame — connection takes effort"],
            "hi": ["किसी एक व्यक्ति को मैसेज करो", "कुछ पसंद का काम करो", "खुद को दोष मत दो"]
        },
        "Motivation": {
            "en": ["Start with the smallest possible action", "Remind yourself why this matters to you", "Track just today — not the whole journey"],
            "hi": ["बहुत छोटे से शुरू करो", "अपना कारण याद करो", "आज पर ही ध्यान दो"]
        },
        "SelfImprovement": {
            "en": ["Pick one habit to work on — just one", "Start smaller than you think you should", "Track daily and reflect weekly"],
            "hi": ["एक आदत चुनो — सिर्फ एक", "जितना सोचो उससे छोटे से शुरू करो", "रोज़ ट्रैक करो, हफ्ते में सोचो"]
        },
        "Finance": {
            "en": ["Write down your expenses honestly", "Identify one area where you can cut back", "Set one small, realistic financial goal"],
            "hi": ["अपना खर्च ईमानदारी से लिखो", "एक जगह खर्च कम करो", "एक छोटा वित्तीय लक्ष्य बनाओ"]
        },
        "Health": {
            "en": ["Drink water right now — seriously", "Pick one health habit to improve this week", "Fix either sleep or movement first — not both"],
            "hi": ["अभी पानी पियो", "इस हफ्ते एक स्वास्थ्य आदत सुधारो", "पहले नींद या व्यायाम — एक चुनो"]
        },
        "Relationship": {
            "en": ["Reflect on what you actually need from this relationship", "Communicate one feeling clearly and calmly", "Give space if needed — for yourself too"],
            "hi": ["सोचो तुम्हें इस रिश्ते से क्या चाहिए", "एक भावना शांति से बताओ", "जगह दो — खुद को भी"]
        },
        "Confusion/DecisionMaking": {
            "en": ["Write down the decision and all your options", "For each option: what's the realistic worst case?", "Trust your gut after the analysis — decide calmly"],
            "hi": ["सभी विकल्प लिखो", "हर विकल्प का सबसे बुरा परिणाम सोचो", "शांत होकर निर्णय लो"]
        }
    }

    steps = []

    # Mood-based opening
    if mood in ["stressed", "sad"]:
        if lang == "hi":
            steps.append("पहले एक गहरी सांस लो — धीरे-धीरे आगे बढ़ते हैं")
        else:
            steps.append("Take a breath first — let's go one step at a time.")
    # Low confidence note
    if confidence < 60:
        if lang == "hi":
            steps.append("शायद मैं पूरी तरह सही न होऊं, लेकिन चलो इसे साथ में समझने की कोशिश करते हैं:")
        else:
            steps.append("I may not be fully certain, but let's figure this out together:")

    # Feedback learning — skip disliked intents
    feedback_data = []
    if os.path.exists("feedback_data.json"):
        with open("feedback_data.json", "r") as f:
            feedback_data = json.load(f)

    negative_intents = {e.get("intent") for e in feedback_data if e.get("feedback") == "no"}

    # Build steps from detected intents
    used_intents = []
    for intent, _ in detected_intents:
        if intent in negative_intents:
            continue
        intent_plan = plans.get(intent)
        if intent_plan:
            plan_steps = intent_plan["hi"] if lang == "hi" else intent_plan["en"]
            random.shuffle(plan_steps) 
            # Pick random 2–3 steps instead of all
            selected_steps = random.sample(plan_steps, min(3, len(plan_steps)))
            steps += selected_steps
            used_intents.append(intent)

    # Fallback if all intents were filtered
    if not used_intents:
        for intent, _ in detected_intents:
            intent_plan = plans.get(intent)
            if intent_plan:
                plan_steps = intent_plan["hi"] if lang == "hi" else intent_plan["en"]
                random.shuffle(plan_steps) 
                selected_steps = random.sample(plan_steps, min(3, len(plan_steps)))
                steps += selected_steps
    # Remove duplicates, limit to 5
    steps = list(dict.fromkeys(steps))
    # 🎯 Apply mode AFTER steps are built
    if mode == "simple":
        steps = steps[:2]

    elif mode == "deep":
        if lang == "hi":
            steps.append("थोड़ा रुककर सोचो — यह क्यों हो रहा है और तुम असल में क्या चाहते हो")
        else:
            steps.append("Pause and reflect — why is this happening and what do you truly want?")

    elif mode == "next":
        steps = steps[:1]
    return steps[:5]'''

# ---------------- MEMORY ----------------
def get_session_memory():
    return session.get("memory", [])

def add_to_memory(user_input, intent, mood, response_type=""):
    memory = get_session_memory()
    memory.append({
        "time": datetime.now().strftime("%H:%M"),
        "text": user_input,
        "intent": intent,
        "mood": mood,
        "response_type": response_type   # ← stores what type was used last
    })
    session["memory"] = memory[-10:]

# ---------------- EMOJIS ----------------
MOOD_EMOJI = {"stressed": "😤", "sad": "😔", "confused": "😕", "motivated": "💪", "calm": "😌"}
INTENT_EMOJI = {
    "Career": "💼", "Learning": "📘", "Stress": "🧘", "Loneliness": "💬",
    "Motivation": "🚀", "SelfImprovement": "⭐", "Finance": "💰",
    "Health": "❤️", "Relationship": "🤝", "Confusion/DecisionMaking": "🔍"
}

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    raw_input = data.get("message", "").strip()

    if not raw_input:
        return jsonify({"error": "Empty message"}), 400

    if not model or not vectorizer:
        return jsonify({"error": "Model not loaded"}), 500

    # 🔹 Detect language
    lang = detect_language(raw_input)

    # 🔹 Mode detection
    mode = "normal"
    raw_lower = raw_input.lower()
    if any(w in raw_lower for w in ["simple", "asar", "सरल", "आसान"]):
        mode = "simple"
    elif any(w in raw_lower for w in ["deep", "gehra", "गहराई", "विस्तार"]):
        mode = "deep"
    elif any(w in raw_lower for w in ["next", "agla", "अगला", "आगे"]):
        mode = "next"

    # 🔹 Normalize
    user_input = normalize_text(raw_input)

    try:
        # 🔹 Prediction
        X_vec = vectorizer.transform([user_input])
        probs = model.predict_proba(X_vec)[0]

        intents = model.classes_

        threshold = 0.15
        detected_intents = [
            (intents[i], probs[i])
            for i in range(len(probs))
            if probs[i] > threshold
        ]

        if not detected_intents:
            top_idx = probs.argmax()
            detected_intents = [(intents[top_idx], probs[top_idx])]

        detected_intents = sorted(detected_intents, key=lambda x: x[1], reverse=True)

        if len(detected_intents) < 2:
            top2 = probs.argsort()[-2:][::-1]
            detected_intents = [(intents[i], probs[i]) for i in top2]

        # 🔹 Extract info
        primary_intent = detected_intents[0][0]
        confidence = detected_intents[0][1] * 100
        mood = detect_mood(user_input)

        # 🔹 Get history BEFORE adding current message
        history = get_session_memory()

        # 🔹 Generate response (pass history for context awareness)
        from action_engine import generate_action_plan
        steps, response_type = generate_action_plan(
            detected_intents, confidence, mood, lang, mode,
            user_input=raw_input, history=history
        )

        # 🔹 Store in memory WITH response_type
        add_to_memory(raw_input, primary_intent, mood, response_type)

        return jsonify({
            "intents": [{"name": i[0], "confidence": round(i[1] * 100, 1)} for i in detected_intents],
            "intent": primary_intent,
            "intent_emoji": INTENT_EMOJI.get(primary_intent, "🧠"),
            "confidence": round(confidence, 1),
            "mood": mood,
            "mood_emoji": MOOD_EMOJI.get(mood, "😐"),
            "steps": steps,
            "returning": len(history) > 1,
            "history_count": len(history),
            "lang": lang,
        })

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({
            "intent": "Error",
            "intent_emoji": "⚠️",
            "confidence": 0,
            "mood": "unknown",
            "mood_emoji": "😐",
            "steps": ["Something broke — but you're very close. Fix incoming."],
            "intents": [],
            "lang": "en"
        })
    

@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json()
    # entry = {
    #     "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
    #     "user_input": data.get("message", ""),
    #     "intent": data.get("intent"),
    #     "mood": data.get("mood"),
    #     "confidence": data.get("confidence"),
    #     "feedback": data.get("feedback")
    # }
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "input": data.get("message"),
        "intent": data.get("intent"),
        "mood": data.get("mood"),
        "confidence": data.get("confidence"),
        "feedback": data.get("feedback")
    }   
    file_path = "feedback_data.json"
    existing = []
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            existing = json.load(f)
    existing.append(entry)
    with open(file_path, "w") as f:
        json.dump(existing, f, indent=4)
    print("\n📥 Feedback saved:", entry)
    return jsonify({"status": "saved"})

@app.route("/followup", methods=["POST"])
def followup():
    from action_engine import generate_action_plan
    data        = request.get_json()
    mode        = data.get("mode", "normal")
    lang        = data.get("lang", "en")
    mood        = data.get("mood", "calm")
    confidence  = data.get("confidence", 80)
    intents_raw = data.get("intents", [])

    detected_intents = [(i["name"], i["confidence"] / 100) for i in intents_raw]
    if not detected_intents:
        detected_intents = [(data.get("intent", "Stress"), 0.8)]

    primary_intent = detected_intents[0][0]

    # Pass full session history so follow-ups feel contextual
    history = get_session_memory()

    steps, response_type = generate_action_plan(
        detected_intents, confidence, mood, lang, mode,
        user_input="", history=history
    )

    # Store followup in memory too
    add_to_memory(f"[followup:{mode}]", primary_intent, mood, response_type)

    return jsonify({
        "intents":      [{"name": i[0], "confidence": round(i[1]*100,1)} for i in detected_intents],
        "intent":       primary_intent,
        "intent_emoji": INTENT_EMOJI.get(primary_intent, "🧠"),
        "confidence":   round(confidence, 1),
        "mood":         mood,
        "mood_emoji":   MOOD_EMOJI.get(mood, "😐"),
        "steps":        steps,
        "returning":    True,
        "lang":         lang
    })

if __name__ == "__main__":
    app.run(debug=True, port=7860)