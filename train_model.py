import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.multiclass import OneVsRestClassifier

# Load dataset
df = pd.read_csv("intent_data_expanded.csv")

X = df["text"]
y = df["intent"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# ML Pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=5000   # LIMIT → better performance
    )),
    ("clf", OneVsRestClassifier(
        LogisticRegression(max_iter=1000)
    ))
])
# model = Pipeline([
#     ("tfidf", TfidfVectorizer(
#         stop_words="english",
#         ngram_range=(1, 2)
#     )),
#     ("clf", LogisticRegression(
#         max_iter=1000,
#         class_weight="balanced"
#     ))
# ])

# Train
model.fit(X_train, y_train)
joblib.dump(model, "intent_classifier.pkl")
print("✅ Multi-intent model saved!")

# Evaluate
print("\n📊 Model Evaluation\n")
print(classification_report(y_test, model.predict(X_test)))

# Save model
joblib.dump(model, "intent_classifier.pkl")
print("\n✅ Model saved as intent_classifier.pkl")