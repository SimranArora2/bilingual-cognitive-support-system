# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.linear_model import LogisticRegression
# from sklearn.pipeline import Pipeline

# # Load data
# df = pd.read_csv("intent_data.csv")

# # Build pipeline
# model = Pipeline([
#     ("tfidf", TfidfVectorizer()),
#     ("clf", LogisticRegression())
# ])

# # Train
# model.fit(df["text"], df["intent"])

# # Test with user input
# user_input = input("\nTell me what's on your mind: ")
# predicted_intent = model.predict([user_input])[0]

# print("\nPredicted Intent:", predicted_intent)


import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from action_engine import generate_action_plan


# Load dataset
df = pd.read_csv("intent_data_expanded.csv")

X = df["text"]
y = df["intent"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Build ML pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 3),
    max_features=5000
    )),
    ("clf", LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    ))
])

# Train
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("\n📊 Model Evaluation:\n")
print(classification_report(y_test, y_pred))

# Save model
joblib.dump(model, "intent_classifier.pkl")
print("\n✅ Model saved as intent_classifier.pkl")

# Interactive testing
# print("\n--- Cognitive Support System ---")
# while True:
#     user_input = input("\nTell me what's on your mind (or type 'exit'): ")
#     if user_input.lower() == "exit":
#         break

#     probs = model.predict_proba([user_input])[0]
#     intents = model.classes_
#     top_idx = probs.argmax()

#     print(f"\n🧠 Predicted Intent: {intents[top_idx]}")
#     print(f"🔍 Confidence: {probs[top_idx]*100:.2f}%")
print("\n--- Cognitive Support System ---")
while True:
    user_input = input("\nTell me what's on your mind (or type 'exit'): ")
    if user_input.lower() == "exit":
        break

    probs = model.predict_proba([user_input])[0]
    intents = model.classes_
    top_idx = probs.argmax()

    intent = intents[top_idx]
    confidence = probs[top_idx] * 100

    print(f"\n🧠 Detected Intent: {intent}")
    print(f"🔍 Confidence: {confidence:.2f}%")

    action_plan = generate_action_plan(intent, user_input)
    print(action_plan)
