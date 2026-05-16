import pandas as pd
import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# 🔹 Load main dataset
df = pd.read_csv("intent_data_expanded.csv")

# Ensure correct column names
df = df.rename(columns={
    "text": "user_input",
    "intent": "intent"
})

# 🔹 Load feedback (JSON)
feedback_data = []
try:
    with open("feedback_data.json", "r") as f:
        feedback_data = json.load(f)
except:
    pass

# Convert feedback to DataFrame (if exists)
if feedback_data:
    df_feedback = pd.DataFrame(feedback_data)

    # Keep only positive feedback
    df_feedback = df_feedback[df_feedback["feedback"] == "yes"]

    # Merge with main dataset
    df = pd.concat([df, df_feedback[["user_input", "intent"]]])

# 🔹 Clean data
df = df.dropna(subset=["user_input", "intent"])

print("Total training samples:", len(df))
print(df.head())

# 🔹 Train model
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df["user_input"])
y = df["intent"]

model = LogisticRegression(max_iter=1000)
model.fit(X, y)

# 🔹 Save model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("✅ Model retrained successfully!")