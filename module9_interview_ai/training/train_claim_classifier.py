# train_claim_classifier.py  (robust to TrainingArguments kwarg differences)
import os, inspect
import pandas as pd
import numpy as np
from datasets import Dataset, DatasetDict
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support, accuracy_score

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments as HFTrainingArguments,
    DataCollatorWithPadding,
)
import transformers as tf_lib

print(f"[debug] transformers version = {tf_lib.__version__}")
from transformers import TrainingArguments
print(f"[debug] TrainingArguments module = {TrainingArguments.__module__}")

# -------- paths --------
DATA_PATH = "module9_interview_ai/training/data/prepared_claims_en.csv"
OUT_DIR   = "module9_interview_ai/models/claim_classifier_distilbert_quick"
os.makedirs(OUT_DIR, exist_ok=True)

# -------- data load & split (stratified) --------
df = pd.read_csv(DATA_PATH).dropna(subset=["text", "label"]).reset_index(drop=True)
df["label"] = df["label"].astype(int)

train_df, test_df = train_test_split(
    df[["text","label"]],
    test_size=0.2, random_state=42, stratify=df["label"]
)


def balanced_cap(frame, cap):
    parts = []
    for y, grp in frame.groupby("label"):
        parts.append(grp.sample(n=min(cap, len(grp)), random_state=42))
    return pd.concat(parts).sample(frac=1.0, random_state=42).reset_index(drop=True)


# change these two lines in the “balanced_cap” calls temporarily:
train_df = balanced_cap(train_df, 500)   # ~1,000 train
test_df = balanced_cap(test_df,  200)   # ~400 test
print(f"[info] balanced train size = {len(train_df)} {train_df['label'].value_counts().to_dict()}")
print(f"[info] balanced test  size = {len(test_df)} {test_df['label'].value_counts().to_dict()}")

train_ds = Dataset.from_pandas(train_df[["text","label"]])
test_ds = Dataset.from_pandas(test_df[["text","label"]])
ds = DatasetDict({"train": train_ds, "test": test_ds})

# -------- tokenizer/model --------
MODEL_NAME = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tok(batch): return tokenizer(batch["text"], truncation=True)
ds = ds.map(tok, batched=True, remove_columns=["text"])
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

# -------- metrics --------
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    acc = accuracy_score(labels, preds)
    p, r, f1, _ = precision_recall_fscore_support(labels, preds, average="binary", zero_division=0)
    return {"accuracy": acc, "precision": p, "recall": r, "f1": f1}


# -------- SAFE TrainingArguments (filter unknown kwargs) --------
args = HFTrainingArguments(
    output_dir=OUT_DIR,
    do_eval=True,
    learning_rate=5e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=1,
    weight_decay=0.01,
    save_total_limit=1,
    report_to=[],
    seed=42,
    no_cuda=True,                 # force CPU (removes pin_memory warning)
    dataloader_pin_memory=False,  # cleaner logs on CPU
    disable_tqdm=True,            # hide tqdm bar, rely on logging
    logging_steps=10,             # log every 10 steps
    logging_dir=os.path.join(OUT_DIR, "logs"),
)


allowed = set(inspect.signature(HFTrainingArguments.__init__).parameters.keys())
safe_kwargs = {k: v for k, v in desired_kwargs.items() if k in allowed}
missing = sorted(set(desired_kwargs) - allowed)
if missing:
    print(f"[warn] TrainingArguments does not support: {missing} — skipping them.")

args = HFTrainingArguments(**safe_kwargs)

# -------- trainer --------
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=ds["train"],
    eval_dataset=ds["test"],
    tokenizer=tokenizer,   # deprecation warning is fine
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

trainer.train()
metrics = trainer.evaluate()
print("[eval]", metrics)

trainer.save_model(OUT_DIR)
tokenizer.save_pretrained(OUT_DIR)
print(f"[ok] model saved to: {OUT_DIR}")

