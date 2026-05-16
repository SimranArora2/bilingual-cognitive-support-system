# mood_engine.py
# This file detects the user's emotional state (mood)
# using simple keyword-based NLP rules.

def detect_mood(text):
    """
    Detects mood from user input text.
    Returns one of: calm, stressed, sad, confused, motivated
    """

    text = text.lower()

    if any(word in text for word in ["stressed", "anxious", "pressure", "overwhelmed", "tired"]):
        return "stressed"

    if any(word in text for word in ["sad", "lonely", "alone", "depressed", "empty"]):
        return "sad"

    if any(word in text for word in ["confused", "lost", "don't know", "uncertain"]):
        return "confused"

    if any(word in text for word in ["motivated", "excited", "ready", "focused"]):
        return "motivated"

    return "calm"