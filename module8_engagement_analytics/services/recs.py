# module8_engagement_analytics/services/recs.py
import os, json, joblib
from typing import Dict, Any
from scipy.sparse import hstack
import numpy as np


_ARTIFACT = None
_PRIORS = None


def _load():
    global _ARTIFACT, _PRIORS
    if _ARTIFACT is None:
        path = os.path.join(os.path.dirname(__file__), "..", "models", "module8_recs.joblib")
        _ARTIFACT = joblib.load(os.path.abspath(path))
    if _PRIORS is None:
        p = os.path.join(os.path.dirname(__file__), "..", "models", "time_priors.json")
        with open(os.path.abspath(p), "r", encoding="utf-8") as f:
            _PRIORS = json.load(f)


def _build_text(title: str, abstract: str, category: str, subcategory: str="") -> str:
    return f"{title or ''} {abstract or ''} {category or ''} {subcategory or ''}".strip()


def _one_hot_time(time_encoder, hour: int, dow: int):
    from scipy.sparse import csr_matrix
    if time_encoder is None:
        return csr_matrix((1, 0))
    import numpy as np
    X = np.array([[int(hour), int(dow)]])
    return time_encoder.transform(X)


def _get_time_prior(category: str, hour: int) -> float:
    # try exact match, else category average, else global average
    key = f"{category}::{int(hour)}"
    if key in _PRIORS:
        return float(_PRIORS[key])
    cat_vals = [float(v) for k, v in _PRIORS.items() if k.startswith(f"{category}::")]
    if cat_vals:
        return float(sum(cat_vals)/len(cat_vals))
    all_vals = [float(v) for v in _PRIORS.values()]
    return float(sum(all_vals)/len(all_vals)) if all_vals else 0.1


def score_article(payload: Dict[str, Any], w_model: float = 0.7) -> Dict[str, Any]:
    """
    Blend model probability with time prior for a given article context.
    payload keys: { title, abstract, category, subcategory (opt), hour, dow }
    """
    _load()  # loads _ARTIFACT and _PRIORS

    clf = _ARTIFACT["clf"]
    vectorizer = _ARTIFACT["vectorizer"]
    time_encoder = _ARTIFACT.get("time_encoder")
    best_t = float(_ARTIFACT.get("best_threshold", 0.5))

    # Normalize category/subcategory to match priors/training convention (lowercase)
    cat = (payload.get("category", "") or "").strip().lower()
    subc = (payload.get("subcategory", "") or "").strip().lower()

    title = payload.get("title", "") or ""
    abstract = payload.get("abstract", "") or ""
    hour = int(payload.get("hour", 12))
    dow = int(payload.get("dow", 2))

    # Build text features (include normalized cat/subcat for consistency)
    text = _build_text(title, abstract, cat, subc)
    X_text = vectorizer.transform([text])

    # Optional time one-hot
    X_time = _one_hot_time(time_encoder, hour, dow)  # should return empty CSR if encoder is None

    # Final feature matrix
    X = hstack([X_text, X_time], format="csr")

    # Model probability (calibrated SGD if you trained with --calibrate; otherwise raw predict_proba)
    proba = float(clf.predict_proba(X)[0, 1])

    # Time prior uses normalized category
    time_prior = float(_get_time_prior(cat, hour))

    # Blend model + prior
    final_score = float(w_model * proba + (1.0 - w_model) * time_prior)

    return {
        "model_prob": round(proba, 4),
        "time_prior": round(time_prior, 4),
        "final_score": round(final_score, 4),
        "best_threshold": round(best_t, 2),
        "explanation": (
            f"Content score {proba:.2f} blended with {cat or '?'}@{hour:02d}h prior {time_prior:.2f} "
            f"(w={w_model})."
        ),
    }


def suggest_best_hours(category: str, top_k: int = 3):
    """
    Return top-k hours (0..23) with the highest time prior for the given category.
    Category is normalized to lowercase to match keys in time_priors.json (e.g., "sports::21").
    """
    _load()  # ensures _PRIORS is populated
    cat = (category or "").strip().lower()

    candidates = []
    for h in range(24):
        key = f"{cat}::{h}"
        if key in _PRIORS:
            candidates.append({"hour": h, "time_prior": float(_PRIORS[key])})

    # sort descending by prior and take top_k
    candidates.sort(key=lambda x: x["time_prior"], reverse=True)
    return candidates[:top_k]
