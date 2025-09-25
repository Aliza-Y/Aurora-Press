# module9_interview_ai/training/prepare_claims_dataset.py
import os, glob, re
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(__file__))  # .. / module9_interview_ai
DATA_DIR = os.path.join(ROOT, "training", "data")
GEN_DIR  = os.path.join(DATA_DIR, "general_claim")
CUS_DIR  = os.path.join(DATA_DIR, "custom")
OUT_PATH = os.path.join(DATA_DIR, "prepared_claims_en.csv")

def read_any(path):
    # Auto-detect delimiter and be lenient with bad chars
    return pd.read_csv(path, sep=None, engine="python",
                       encoding="utf-8", on_bad_lines="skip")

def normalize_columns(df):
    # Make column names lowercase for easier matching
    df = df.rename(columns={c: c.strip().lower() for c in df.columns})

    # Candidate text columns seen in claim datasets
    text_cols = ["text", "sentence", "claim", "content", "statement"]
    text_col = next((c for c in text_cols if c in df.columns), None)

    # Candidate label columns (various naming)
    label_cols = ["label", "checkworthy", "is_claim", "target", "y"]
    label_col = next((c for c in label_cols if c in df.columns), None)

    # Language
    lang_cols = ["lang", "language", "lng"]
    lang_col = next((c for c in lang_cols if c in df.columns), None)

    if text_col is None:
        raise ValueError(f"No text-like column found in columns={list(df.columns)}")

    # Build a minimal 2-col frame
    out = pd.DataFrame()
    out["text"] = df[text_col].astype(str)

    # Map label variety to {0,1}
    if label_col is None:
        # Some sets don’t have labels (skip them)
        out["label"] = pd.NA
    else:
        x = df[label_col]
        if x.dtype == bool:
            out["label"] = x.astype(int)
        else:
            # Normalize strings like 'yes','claim','true','1'
            def to_bin(v):
                if pd.isna(v): return pd.NA
                s = str(v).strip().lower()
                if s in {"1","true","t","yes","y","claim","checkworthy"}:
                    return 1
                if s in {"0","false","f","no","n","non-claim","not_checkworthy","not-checkworthy"}:
                    return 0
                # Try numeric
                m = re.match(r"^\d+$", s)
                if m: return int(s)
                return pd.NA
            out["label"] = x.map(to_bin)

    # Keep language if present
    if lang_col:
        out["lang"] = df[lang_col].astype(str).str.lower().str.strip()
    else:
        out["lang"] = pd.NA

    return out

def load_general_claim():
    frames = []
    for path in glob.glob(os.path.join(GEN_DIR, "**", "*.*"), recursive=True):
        if not path.lower().endswith((".csv", ".tsv", ".txt")):
            continue
        try:
            df = read_any(path)
            df = normalize_columns(df)
            df["__source"] = os.path.basename(path)
            frames.append(df)
        except Exception as e:
            print(f"[skip] {path}: {e}")
    if not frames:
        print("[warn] No general-claim files loaded.")
        return pd.DataFrame(columns=["text","label","lang","__source"])
    df = pd.concat(frames, ignore_index=True)

    # English only (accept en, en-us, en_gb, empty = drop)
    df = df.dropna(subset=["text"])
    df["lang"] = df["lang"].fillna("")
    df_en = df[df["lang"].str.startswith("en")]
    # If dataset has no lang info, allow heuristic: keep lines with >70% ascii letters/spaces
    if df_en.empty:
        def is_english(s):
            s = str(s)
            if not s: return False
            letters = sum(ch.isascii() and (ch.isalpha() or ch.isspace() or ch in ".,!?;:'\"-()") for ch in s)
            return letters/ max(1,len(s)) > 0.7
        df_en = df[df["text"].map(is_english)]
    return df_en[["text","label"]]

def load_custom():
    # Your labeled file from the CLI
    path = os.path.join(CUS_DIR, "my_transcripts_claims.csv")
    if not os.path.isfile(path):
        print(f"[warn] custom file not found: {path}")
        return pd.DataFrame(columns=["text","label"])
    df = read_any(path)
    df = df.rename(columns={c: c.strip().lower() for c in df.columns})
    if not {"text","label"}.issubset(df.columns):
        # try common alternatives
        if "sentence" in df.columns: df["text"] = df["sentence"]
        if "y" in df.columns: df["label"] = df["y"]
    df = df[["text","label"]].copy()
    # Force 0/1
    df["label"] = df["label"].astype(int)
    return df

def clean_merge(df):
    df["text"] = df["text"].astype(str).str.strip()
    df = df[df["text"].str.len() > 0]
    # Drop rows without labels (some general sources might lack them)
    df = df.dropna(subset=["label"])
    # Make sure labels are integers 0/1
    df["label"] = df["label"].astype(int).clip(0,1)
    # Deduplicate
    df = df.drop_duplicates(subset=["text"])
    # Optional short/long filters
    df = df[df["text"].str.split().str.len().between(5, 120)]
    return df

def main():
    gen = load_general_claim()
    print(f"[info] general-claim loaded: {len(gen)} rows")

    cus = load_custom()
    print(f"[info] custom loaded:        {len(cus)} rows")

    merged = pd.concat([gen, cus], ignore_index=True)
    merged = clean_merge(merged)

    print(f"[info] merged/cleaned:       {len(merged)} rows")
    print("[info] label distribution:\n", merged["label"].value_counts(dropna=False))

    os.makedirs(DATA_DIR, exist_ok=True)
    merged.to_csv(OUT_PATH, index=False)
    print(f"[ok] wrote {OUT_PATH}")

if __name__ == "__main__":
    main()
