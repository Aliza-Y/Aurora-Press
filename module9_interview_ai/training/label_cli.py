# Path-robust labeling CLI: runs from any cwd.
import csv, os, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent                # ...\module9_interview_ai\training
DATA = BASE / "data"                                  # ...\training\data
SRC  = DATA / "to_label.csv"                          # input to label
DST  = DATA / "custom" / "my_transcripts_claims.csv"  # output labels

# ensure output dir exists
DST.parent.mkdir(parents=True, exist_ok=True)

if not SRC.exists():
    print("\n[ERROR] to_label.csv not found.\n"
          f"Expected at:\n  {SRC}\n\n"
          "Create it with a header 'text' and one line per segment.\n")
    sys.exit(1)

seen = set()
if DST.exists():
    with open(DST, newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            seen.add(r['text'])

with open(SRC, newline='', encoding='utf-8') as fsrc, \
     open(DST, 'a', newline='', encoding='utf-8') as fdst:
    rdr = csv.DictReader(fsrc)
    if 'text' not in rdr.fieldnames:
        print(f"[ERROR] 'text' column not found in {SRC}. Found columns: {rdr.fieldnames}")
        sys.exit(1)

    w = csv.DictWriter(fdst, fieldnames=['text','label'])
    if fdst.tell() == 0:
        w.writeheader()

    print(f"[INFO] Reading: {SRC}")
    print(f"[INFO] Writing labels to: {DST}")
    for row in rdr:
        t = (row.get('text') or '').strip()
        if not t or t in seen:
            continue
        print("\n---\n", t, "\n---")
        while True:
            ans = input("[Y] claim / [N] not / [S]kip ? ").strip().lower()
            if ans in ('y','n','s'):
                break
            print("Please type Y, N, or S.")
        if ans == 'y':
            w.writerow({'text': t, 'label': 1})
        elif ans == 'n':
            w.writerow({'text': t, 'label': 0})
        # skip otherwise
    print("\n[DONE] Labels saved at:", DST)
