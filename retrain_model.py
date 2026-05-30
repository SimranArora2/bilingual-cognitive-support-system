import pandas as pd
import json
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.pipeline import Pipeline

# ─── Load main dataset ───────────────────────────────────────────────────────
df = pd.read_csv("intent_data_expanded.csv")
df = df.rename(columns={df.columns[0]: "user_input", df.columns[1]: "intent"})

# ─── Load feedback (fix key mismatch bug) ────────────────────────────────────
# Old entries used "user_input", newer ones use "input" — handle both
feedback_data = []
try:
    with open("feedback_data.json", "r") as f:
        feedback_data = json.load(f)
except Exception:
    pass

if feedback_data:
    df_feedback = pd.DataFrame(feedback_data)
    df_feedback = df_feedback[df_feedback["feedback"] == "yes"]

    # Normalize: use "input" if present, else "user_input"
    if "input" in df_feedback.columns and "user_input" not in df_feedback.columns:
        df_feedback = df_feedback.rename(columns={"input": "user_input"})
    elif "input" in df_feedback.columns and "user_input" in df_feedback.columns:
        df_feedback["user_input"] = df_feedback["user_input"].fillna(df_feedback["input"])

    df_feedback = df_feedback[["user_input", "intent"]].dropna()
    df_feedback = df_feedback[df_feedback["user_input"].str.strip() != ""]

    if not df_feedback.empty:
        df = pd.concat([df, df_feedback], ignore_index=True)
        print(f"✅ Merged {len(df_feedback)} positive feedback samples")

# ─── Clean ───────────────────────────────────────────────────────────────────
df = df.dropna(subset=["user_input", "intent"])
df = df[df["user_input"].str.strip() != ""]

print(f"Total training samples: {len(df)}")
print(df["intent"].value_counts())

# ─── Build pipeline ──────────────────────────────────────────────────────────
# KEY INSIGHT: char_wb n-grams (3-5 chars) outperform word n-grams for Hinglish.
# Why: "ghabra", "ghabrahat", "ghabrana" all share the char pattern "ghabr" —
# the model recognises anxiety-related Hinglish words even when spelled differently.
# CalibratedClassifierCV wraps LinearSVC to provide predict_proba (needed by app.py).
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        analyzer="char_wb",   # character-level — works natively on Hinglish
        ngram_range=(3, 5),   # 3-to-5 character windows
        sublinear_tf=True,    # log-scale TF weighting
    )),
    ("clf", CalibratedClassifierCV(
        LinearSVC(max_iter=3000, C=1),
        cv=3
    ))
])

# ─── Cross-validate ───────────────────────────────────────────────────────────
X = df["user_input"]
y = df["intent"]

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(pipeline, X, y, cv=cv, scoring="accuracy")
print(f"\n📊 Cross-validated accuracy: {scores.mean()*100:.2f}% ± {scores.std()*100:.2f}%")
print(f"   Per fold: {[round(s*100,1) for s in scores]}")

# ─── Train on full dataset ────────────────────────────────────────────────────
pipeline.fit(X, y)

# ─── Save (app.py expects separate model.pkl and vectorizer.pkl) ──────────────
vectorizer = pipeline.named_steps["tfidf"]
model      = pipeline.named_steps["clf"]

joblib.dump(model,      "model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("\n✅ Model retrained! (char n-grams 3-5 + LinearSVC)")
print("   model.pkl and vectorizer.pkl saved.")
