import os
import json
import argparse
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import roc_auc_score, f1_score, classification_report
from sklearn.calibration import CalibratedClassifierCV
from scipy.sparse import hstack, csr_matrix
import joblib

r"""
MIND small expected structure:

  ...\MINDsmall_train\
    news.tsv
    behaviors.tsv

  ...\MINDsmall_dev\
    news.tsv
    behaviors.tsv

news.tsv columns (tab-separated):
  news_id  category  subcategory  title  abstract  url  title_entities  abstract_entities
behaviors.tsv columns:
  impression_id  user_id  time  history  impressions
Impressions look like: "N12345-0 N67890-1 ..." (news_id + "-" + label)
"""


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train_dir", type=str, required=True, help="Path to MIND small train dir")
    ap.add_argument("--valid_dir", type=str, required=True, help="Path to MIND small validation/dev dir")
    ap.add_argument("--out_dir", type=str, default=os.path.join(".", "models"), help="Where to save artifacts")
    ap.add_argument("--calibrate", action="store_true",
                help="Wrap the SGD model with CalibratedClassifierCV (sigmoid), improves probability quality")
    # speed / memory / features
    ap.add_argument("--max_train_rows", type=int, default=300000, help="Cap training impressions (for speed)")
    ap.add_argument("--max_valid_rows", type=int, default=150000, help="Cap validation impressions (for speed)")
    ap.add_argument("--min_df", type=int, default=3, help="TF-IDF min_df")
    ap.add_argument("--max_features", type=int, default=200000, help="TF-IDF max_features")
    ap.add_argument("--ngram_max", type=int, default=2, help="1=unigrams, 2=uni+bi (bigrams)")

    # add time features
    ap.add_argument("--include_time_feats", action="store_true", help="Add one-hot hour (0-23) and day-of-week (0-6)")

    # SGD params
    ap.add_argument("--alpha", type=float, default=1e-5, help="L2 regularization (smaller = stronger fit)")
    ap.add_argument("--max_iter", type=int, default=15, help="Epochs over training data")
    ap.add_argument("--early_stopping", action="store_true", help="Enable early stopping on internal split")

    # imbalance handling
    ap.add_argument("--balance", action="store_true", help="Use sample weights to balance classes")
    ap.add_argument("--neg_pos_ratio", type=float, default=None,
                    help="Downsample negatives to this multiple of positives (e.g., 3.0 keeps <=3 negatives per positive)")

    return ap.parse_args()


def load_news(news_path: str) -> pd.DataFrame:
    cols = ["news_id","category","subcategory","title","abstract","url","title_entities","abstract_entities"]
    df = pd.read_csv(news_path, sep="\t", header=None, names=cols, quoting=3)
    df = df[["news_id","category","subcategory","title","abstract"]].fillna("")
    return df


def load_behaviors(beh_path: str) -> pd.DataFrame:
    cols = ["impression_id","user_id","time","history","impressions"]
    df = pd.read_csv(beh_path, sep="\t", header=None, names=cols, quoting=3)
    return df


def explode_impressions(beh: pd.DataFrame) -> pd.DataFrame:
    """
    Vectorized expansion of 'impressions' into one row per (news_id, label).
    """
    beh = beh[["impression_id", "user_id", "time", "impressions"]].copy()
    beh["imp_list"] = beh["impressions"].astype(str).str.strip().str.split(" ")
    df = beh.explode("imp_list", ignore_index=True)
    df = df[df["imp_list"].notna() & (df["imp_list"] != "")]
    parts = df["imp_list"].str.rsplit("-", n=1, expand=True)
    df["news_id"] = parts[0]
    df["label"] = pd.to_numeric(parts[1], errors="coerce").fillna(0).astype(int)
    df = df.drop(columns=["impressions", "imp_list"])
    return df


def build_feature_text(df_news_like: pd.DataFrame) -> pd.Series:
    # title + abstract + category + subcategory
    return (
        df_news_like["title"].astype(str) + " " +
        df_news_like["abstract"].astype(str) + " " +
        df_news_like["category"].astype(str) + " " +
        df_news_like["subcategory"].astype(str)
    ).fillna("")


def join_and_prepare(imp_df: pd.DataFrame, news_df: pd.DataFrame) -> pd.DataFrame:
    df = imp_df.merge(news_df, on="news_id", how="left")
    df["text"] = build_feature_text(df)
    df = df[["news_id","label","time","category","text"]].fillna("")
    # Parse time → hour / day-of-week (if present)
    try:
        ts = pd.to_datetime(df["time"], errors="coerce")
        df["hour"] = ts.dt.hour.fillna(0).astype(int)
        df["dow"] = ts.dt.dayofweek.fillna(0).astype(int)  # Monday=0
    except Exception:
        df["hour"] = 0
        df["dow"] = 0
    return df


def compute_priors(df: pd.DataFrame, out_json_path: str):
    """
    Compute CTR prior per (category, hour): clicks/shown for that bucket.
    Save to JSON: {"category::hour": ctr, ...}
    """
    shown = df.groupby(["category","hour"])["label"].agg(["count","sum"]).reset_index()
    shown["ctr"] = shown["sum"] / shown["count"].clip(lower=1)
    pri = {f"{row['category']}::{int(row['hour'])}": float(row["ctr"]) for _, row in shown.iterrows()}
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(pri, f, ensure_ascii=False, indent=2)


def one_hot_time_features(hours: np.ndarray, dows: np.ndarray, fit_encoder: OneHotEncoder | None = None):
    """
    One-hot encode hour (0..23) and day-of-week (0..6) and return sparse matrix + fitted encoder.
    """
    X = np.vstack([hours, dows]).T  # shape (n_samples, 2)
    if fit_encoder is None:
        enc = OneHotEncoder(categories=[np.arange(24), np.arange(7)], handle_unknown="ignore", sparse_output=True)
        X_enc = enc.fit_transform(X)
        return X_enc, enc
    else:
        X_enc = fit_encoder.transform(X)
        return X_enc, fit_encoder


def find_best_threshold(y_true: np.ndarray, proba: np.ndarray) -> float:
    """Choose threshold that maximizes F1 on the validation set."""
    best_t, best_f1 = 0.5, -1.0
    for t in np.linspace(0.05, 0.9, 18):
        f1 = f1_score(y_true, (proba >= t).astype(int))
        if f1 > best_f1:
            best_f1, best_t = f1, t
    return float(best_t)


def maybe_downsample(train_df: pd.DataFrame, neg_pos_ratio: float | None) -> pd.DataFrame:
    """
    If neg_pos_ratio is set, keep at most (ratio * #positives) negatives.
    """
    if not neg_pos_ratio or neg_pos_ratio <= 0:
        return train_df

    pos_idx = train_df.index[train_df["label"] == 1]
    neg_idx = train_df.index[train_df["label"] == 0]
    n_pos = len(pos_idx)
    n_neg_keep = int(min(len(neg_idx), neg_pos_ratio * max(1, n_pos)))

    if n_neg_keep <= 0 or n_pos == 0:
        return train_df  # nothing to do

    # sample negatives to target count (without replacement, fixed seed)
    rng = np.random.RandomState(42)
    neg_keep = rng.choice(neg_idx, size=n_neg_keep, replace=False)
    keep_idx = np.concatenate([pos_idx.values, neg_keep])
    down_df = train_df.loc[keep_idx].sample(frac=1.0, random_state=42).reset_index(drop=True)
    return down_df


def main():
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    # --- Load TRAIN ---
    train_news = load_news(os.path.join(args.train_dir, "news.tsv"))
    train_beh = load_behaviors(os.path.join(args.train_dir, "behaviors.tsv"))
    train_imp = explode_impressions(train_beh)
    if args.max_train_rows and len(train_imp) > args.max_train_rows:
        train_imp = train_imp.sample(args.max_train_rows, random_state=42)
    train_df = join_and_prepare(train_imp, train_news)

    # --- Optional: downsample negatives on TRAIN only ---
    train_df = maybe_downsample(train_df, args.neg_pos_ratio)

    # --- Load VALID (never downsample; keep true distribution) ---
    valid_news = load_news(os.path.join(args.valid_dir, "news.tsv"))
    valid_beh = load_behaviors(os.path.join(args.valid_dir, "behaviors.tsv"))
    valid_imp = explode_impressions(valid_beh)
    if args.max_valid_rows and len(valid_imp) > args.max_valid_rows:
        valid_imp = valid_imp.sample(args.max_valid_rows, random_state=42)
    valid_df = join_and_prepare(valid_imp, valid_news)

    # --- Vectorizer (with bigrams if ngram_max=2) ---
    ngram_range = (1, args.ngram_max)
    vectorizer = TfidfVectorizer(
        ngram_range=ngram_range,
        min_df=args.min_df,
        max_features=args.max_features,
        strip_accents="unicode",
        lowercase=True,
        stop_words="english"
    )

    # Text features
    Xtr_text = vectorizer.fit_transform(train_df["text"].values)
    Xva_text = vectorizer.transform(valid_df["text"].values)

    # Optional time one-hot features
    if args.include_time_feats:
        Xtr_time, time_encoder = one_hot_time_features(train_df["hour"].values, train_df["dow"].values)
        Xva_time, _ = one_hot_time_features(valid_df["hour"].values, valid_df["dow"].values, fit_encoder=time_encoder)
    else:
        Xtr_time = csr_matrix((Xtr_text.shape[0], 0))
        Xva_time = csr_matrix((Xva_text.shape[0], 0))
        time_encoder = None

    # Combine sparse: [TF-IDF | time one-hot]
    Xtr = hstack([Xtr_text, Xtr_time], format="csr")
    Xva = hstack([Xva_text, Xva_time], format="csr")

    ytr = train_df["label"].astype(int).values
    yva = valid_df["label"].astype(int).values

    # --- Class imbalance handling via sample weights (optional) ---
    sample_weight = None
    if args.balance:
        n = len(ytr)
        n_pos = max(1, ytr.sum())
        n_neg = max(1, n - n_pos)
        w_pos = n / (2.0 * n_pos)
        w_neg = n / (2.0 * n_neg)
        sample_weight = np.where(ytr == 1, w_pos, w_neg)

    # --- Base SGDClassifier (online-friendly) ---
    # --- Base SGDClassifier (online-friendly) ---
    base_clf = SGDClassifier(
        loss="log_loss",
        alpha=args.alpha,
        penalty="l2",
        max_iter=args.max_iter,
        early_stopping=args.early_stopping,
        n_iter_no_change=3,
        tol=1e-3,
        random_state=42
    )

    # Optional: wrap with calibration (sigmoid). Handle sklearn API change: estimator vs base_estimator.
    if args.calibrate:
        try:
            # Newer scikit-learn
            clf = CalibratedClassifierCV(estimator=base_clf, method="sigmoid", cv=3)
        except TypeError:
            # Older scikit-learn
            clf = CalibratedClassifierCV(base_estimator=base_clf, method="sigmoid", cv=3)
    else:
            clf = base_clf

    clf.fit(Xtr, ytr, sample_weight=sample_weight)


    # --- Evaluate ---
    proba = clf.predict_proba(Xva)[:,1]
    auc = roc_auc_score(yva, proba)

    # Pick best threshold for F1
    best_t = find_best_threshold(yva, proba)
    f1 = f1_score(yva, (proba >= best_t).astype(int))

    print(f"Validation AUC: {auc:.4f}  |  Best F1@{best_t:.2f}: {f1:.4f}")
    print(classification_report(yva, (proba>=best_t).astype(int), digits=4))

    # --- Save artifacts for Module 8 ---
    artifact = {
        "clf": clf,
        "vectorizer": vectorizer,
        "feat_cols": ["tfidf_title+abstract+category+subcategory", "onehot_hour", "onehot_dow"] if args.include_time_feats else ["tfidf_title+abstract+category+subcategory"],
        "best_threshold": best_t,
        "metrics": {"auc": float(auc), "f1_at_best_t": float(f1)},
        "time_encoder": time_encoder, # may be None if not used
        "calibrated": bool(args.calibrate),
    }
    model_path = os.path.join(args.out_dir, "module8_recs.joblib")
    joblib.dump(artifact, model_path)
    print("Saved model:", model_path)

    priors_path = os.path.join(args.out_dir, "time_priors.json")
    compute_priors(train_df, priors_path)
    print("Saved priors:", priors_path)


if __name__ == "__main__":
    main()
