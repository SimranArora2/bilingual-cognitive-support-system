# 🧠 Bilingual Cognitive Support System

An NLP-based bilingual cognitive support web application that detects user intent, mood, and emotional state to generate adaptive guidance responses in English and Hindi.

---

## 🚀 Features

- Multi-intent detection
- Mood analysis
- Bilingual support (English + Hindi)
- Adaptive response generation
- Follow-up guidance modes:
  - Simplify
  - Go deeper
  - Next step
- Feedback learning system
- Memory/session tracking
- Responsive modern UI
- TF-IDF + Logistic Regression NLP pipeline

---

## 🛠 Tech Stack

- Python
- Flask
- Scikit-learn
- HTML/CSS/JavaScript
- NLP
- TF-IDF Vectorization
- Logistic Regression

---

## 📂 Project Structure

```bash
app.py                  # Main Flask app
action_engine.py        # Response generation logic
intent_engine.py        # Intent detection
mood_engine.py          # Mood analysis
memory_engine.py        # Session memory
retrain_model.py        # Adaptive retraining
templates/index.html    # Frontend UI
```

---

## 🧠 Supported Intents

- Stress
- Loneliness
- Career
- Self Improvement
- Confusion / Decision Making

---

## 🌐 Example Inputs

```text
mujhe bahut tension hai
samajh nahi aa raha kya karun
I feel lonely lately
I am stressed about exams
```

---

## 🔄 Adaptive Learning

The system stores feedback data and retrains the model over time using positively rated interactions.

---

## ▶️ Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:7860
```

---

## 📌 Future Scope

- Voice interaction
- LLM integration
- Emotion-aware recommendations
- Real-time conversational memory
- Mental wellness analytics dashboard

---

## 👩‍💻 Author

Simran Arora
M.Tech CSE (AI)