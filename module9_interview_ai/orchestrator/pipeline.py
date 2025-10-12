from module9_interview_ai.agents.claim_classifier import ClaimClassifier

clf = ClaimClassifier()  # load once when your service/process starts


def annotate_transcript(lines, threshold=0.50):
    preds = clf.predict(lines, threshold=threshold)
    return [
        {"text": line,
         "is_claim": (p["label"] == "claim"),
         "proba_claim": p["proba_claim"]}
        for line, p in zip(lines, preds)
    ]
