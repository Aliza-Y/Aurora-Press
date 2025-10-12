# classify_file.py (repo root)
import sys
from module9_interview_ai.agents.claim_classifier import ClaimClassifier

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python classify_file.py <path_to_text_file> [threshold]")
        sys.exit(1)

    path = sys.argv[1]
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 0.50

    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    clf = ClaimClassifier()
    preds = clf.predict(lines, threshold=threshold)

    for line, p in zip(lines, preds):
        print(f"{p['label']:10s} p(claim)={p['proba_claim']:.3f} — {line}")
