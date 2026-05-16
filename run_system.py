# import joblib
# from intent_engine import generate_action_plan

# # Load trained model
# model = joblib.load("intent_classifier.pkl")

# print("\n--- Cognitive Support System ---")

# while True:
#     user_input = input("\nTell me what's on your mind (or type 'exit'): ")

#     if user_input.lower() == "exit":
#         print("👋 Exiting system. Take care!")
#         break

#     probs = model.predict_proba([user_input])[0]
#     intents = model.classes_

#     top_idx = probs.argmax()
#     intent = intents[top_idx]
#     confidence = probs[top_idx] * 100

#     print(f"\n🧠 Detected Intent: {intent}")
#     print(f"🔍 Confidence: {confidence:.2f}%")

#     action_plan = generate_action_plan(intent, user_input)
#     print(action_plan)

# run_system.py
# Main entry point of the Cognitive Support System

import joblib
from mood_engine import detect_mood
from memory_engine import add_to_memory
from action_engine import generate_action_plan

# Load trained ML model
model = joblib.load("intent_classifier.pkl")

print("\n--- Cognitive Support System ---")

while True:
    user_input = input("\nTell me what's on your mind (or type 'exit'): ")

    if user_input.lower() == "exit":
        print("Goodbye. Take care 🌱")
        break

    # Predict intent and confidence
    probs = model.predict_proba([user_input])[0]
    intents = model.classes_
    top_idx = probs.argmax()

    intent = intents[top_idx]
    confidence = probs[top_idx] * 100

    # Detect mood
    mood = detect_mood(user_input)

    # Store interaction in memory
    add_to_memory(user_input, intent, mood)

    # Generate action plan
    action_plan = generate_action_plan(
        intent=intent,
        confidence=confidence,
        mood=mood,
        user_input=user_input
    )

    print(f"\n🧠 Intent: {intent}")
    print(f"🔍 Confidence: {confidence:.2f}%")
    print(f"💭 Mood: {mood}")
    print(action_plan)