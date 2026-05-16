import pandas as pd
from transformers import pipeline

# Load base dataset
df = pd.read_csv("intent_data_base.csv")

# Load paraphrasing model
paraphraser = pipeline(
    "text2text-generation",
    model="ramsrigouthamg/t5_paraphraser"
)

augmented_data = []

def paraphrase(sentence):
    prompt = f"paraphrase: {sentence} </s>"
    results = paraphraser(
        prompt,
        max_length=64,
        num_return_sequences=3,
        num_beams=5
    )
    return [r["generated_text"] for r in results]

# Generate augmented data
for _, row in df.iterrows():
    text = row["text"]
    intent = row["intent"]

    augmented_data.append([text, intent])

    try:
        for p in paraphrase(text):
            augmented_data.append([p, intent])
    except:
        pass

# Save expanded dataset
aug_df = pd.DataFrame(augmented_data, columns=["text", "intent"])
aug_df.to_csv("intent_data_expanded.csv", index=False)

print("✅ Data augmentation completed!")
print("Total samples:", len(aug_df))