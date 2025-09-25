# module8_engagement_analytics/services/feedback.py
from __future__ import annotations

import os
import json
import logging
from typing import List, Dict, Any

log = logging.getLogger("module8.feedback")


# ---------- helpers ----------

def _as_timeline_list(timeline: Any) -> List[Dict[str, int]]:
    if isinstance(timeline, dict):
        return [{"label": "last_window",
                 "views": int(timeline.get("view", 0)),
                 "shares": int(timeline.get("share", 0))}]
    if isinstance(timeline, list):
        norm = []
        for b in timeline:
            v = int(b.get("views", b.get("view", 0)) or 0)
            s = int(b.get("shares", b.get("share", 0)) or 0)
            norm.append({"ts": b.get("ts"), "views": v, "shares": s})
        return norm
    return []


def _totals(timeline_list: List[Dict[str, int]]) -> tuple[int, int, int]:
    views = sum(b.get("views", 0) for b in timeline_list)
    shares = sum(b.get("shares", 0) for b in timeline_list)
    total = views + shares
    return views, shares, total


def _format_hour_list(hours: List[int]) -> str:
    return ", ".join(f"{int(h):02d}:00" for h in hours)


def _provider() -> str:
    return (os.getenv("FEEDBACK_PROVIDER") or "rules").strip().lower()


# ---------- rule-based baseline ----------

def feedback_rules(article: Dict[str, Any],
                   timeline: List[Dict[str, int]],
                   suggestions: List[Dict[str, Any]]) -> str:
    title = article.get("title") or "this article"
    category = (article.get("category") or "general").lower()

    views, shares, total = _totals(timeline)

    bits: List[str] = []
    if total == 0:
        bits.append(f"\"{title}\" has not gathered engagement yet.")
    else:
        bits.append(f"\"{title}\" received about {views} views and {shares} shares so far.")

    if len(timeline) >= 2:
        first = timeline[0].get("views", 0) + timeline[0].get("shares", 0)
        later = sum(b.get("views", 0) + b.get("shares", 0) for b in timeline[1:])
        if first > 0 and later < 0.5 * first:
            bits.append("Engagement was strong in the first hours but dropped afterwards.")
        elif later > first:
            bits.append("Engagement improved after the initial period.")
        else:
            bits.append("Engagement has been steady across the window.")

    if category in {"politics", "sports", "technology", "entertainment"}:
        bits.append(f"Your audience shows consistent interest in {category} topics.")

    # ✅ Top-2 repost hours logic
    if suggestions:
        hours = [int(s.get("hour", 0)) for s in suggestions]
        hours = sorted(set(hours), reverse=True)[:2]  # dedupe + keep best 2
        if hours:
            bits.append(f"Consider reposting at {_format_hour_list(hours)} when your audience is more active.")
        else:
            bits.append("No strong repost hours detected; consider testing different times.")
    else:
        bits.append("No strong repost hours detected; consider testing different times.")

    return " ".join(bits)


# ---------- optional Groq LLM polishing ----------

def _feedback_llm_groq(structured_facts: Dict[str, Any], draft_text: str) -> str:
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        return draft_text

    try:
        from groq import Groq
    except Exception as e:
        log.warning("Groq SDK not installed: %s", e)
        return draft_text

    client = Groq(api_key=groq_key)

    tl = structured_facts.get("timeline") or []
    views = sum((b.get("views", b.get("view", 0)) or 0) for b in tl)
    shares = sum((b.get("shares", b.get("share", 0)) or 0) for b in tl)
    total = views + shares
    has_eng = total > 0

    # ✅ Add “editorial flair” nudge here
    prompt = (
        "You are a newsroom editorial analytics assistant.\n"
        "Rewrite the feedback to sound like an editor’s note: "
        "direct, professional, under 40 words.\n\n"
        "Rules:\n"
        f"- Engagement observed: views={views}, shares={shares}.\n"
        f"- If total > 0, always include \"{views} views and {shares} shares\".\n"
        "- If total == 0, say no engagement observed yet.\n"
        "- Recommend no more than two repost hours.\n\n"
        f"FACTS:\n{json.dumps(structured_facts, ensure_ascii=False)}\n\n"
        f"DRAFT:\n{draft_text}\n"
    )

    try:
        resp = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            messages=[
                {"role": "system", "content": "You write concise, professional editorial feedback."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        text = (resp.choices[0].message.content or "").strip()

        low = text.lower()
        if has_eng and ("no engagement" in low and total > 0):
            text = (
                f"{structured_facts.get('article', {}).get('title', 'This article')} "
                f"has {views} views and {shares} shares so far. "
                "Engagement is building; consider reposting at the suggested hours."
            )
        if has_eng and (str(views) not in text and str(shares) not in text):
            text = (
                f"{structured_facts.get('article', {}).get('title', 'This article')} "
                f"has {views} views and {shares} shares so far. "
            ) + text

        return text
    except Exception as e:
        log.warning("LLM polish failed: %s", e)
        return draft_text


# ---------- main entry ----------

def generate_feedback(article: Dict[str, Any],
                      timeline: Any,
                      suggestions: List[Dict[str, Any]]) -> str:
    tl_list = _as_timeline_list(timeline)
    draft = feedback_rules(article, tl_list, suggestions)
    structured = {
        "article": {
            "id": article.get("article_id"),
            "title": article.get("title"),
            "category": article.get("category"),
            "published_at": str(article.get("published_at")),
        },
        "timeline": tl_list,
        "suggestions": suggestions,
    }
    prov = _provider()
    if prov == "groq":
        return _feedback_llm_groq(structured, draft)
    return draft
