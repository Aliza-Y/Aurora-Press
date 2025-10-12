from module9_interview_ai.agents.claim_classifier import ClaimClassifier

# Pick ONE of these:
clf = ClaimClassifier()
# clf = ClaimClassifier(model_dir=r"D:\Final Year Project\aurorapress\module9_interview_ai\models\claim_classifier_distilbert")

lines = [
    "He promised to reduce prices by 12% next quarter.",
    "Thank you for watching our show."
]
for text, r in zip(lines, clf.predict(lines, threshold=0.50)):
    print(f"{r['label']:10s}  p(claim)={r['proba_claim']:.3f}  —  {text}")
