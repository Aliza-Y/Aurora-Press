# module9_interview_ai/agents/summary_angles.py
from __future__ import annotations
import os
import re
from typing import List, Dict

# ---- Optional extractive summarizer (TextRank via sumy) ----
try:
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.text_rank import TextRankSummarizer
    HAVE_SUMY = True
except Exception:
    HAVE_SUMY = False

# ---- Small text utilities ----
_CLEAN_FILLERS = re.compile(r'\b(uh|um|you know|like)\b', re.I)
_CLEAN_FACT = re.compile(r'\bFact\d+\b', re.I)
_SENT_SPLIT = re.compile(r'(?<=[\.\!\?])\s+')

def _clean(t: str) -> str:
    t = _CLEAN_FACT.sub('', t)
    t = _CLEAN_FILLERS.sub('', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def _build_doc(segments: List[Dict]) -> str:
    """
    Build a single text for summarization with enhanced claim prioritization.
    High-confidence claims are weighted more heavily for better summary quality.
    """
    parts: List[str] = []
    for s in segments:
        txt = _clean(s.get("text", "") or "")
        if not txt:
            continue
        conf = float(s.get("claim_conf", 0.0))
        claim = int(s.get("claim", 0))
        
        # Always include the text once
        parts.append(txt)
        
        # Weight high-confidence claims more heavily
        if claim == 1 and conf >= 0.8:
            # High-confidence claims: include 3 times
            parts.extend([txt, txt])
        elif claim == 1 and conf >= 0.6:
            # Medium-confidence claims: include 2 times
            parts.append(txt)
        elif conf >= 0.9:
            # Very high confidence (regardless of claim/fact): include 2 times
            parts.append(txt)
    
    if not parts:
        parts = [_clean(s.get("text", "")) for s in segments if s.get("text")]
    
    return " ".join([p for p in parts if p])

def _extractive_summary(text: str, sent_count: int = 6) -> str:
    if HAVE_SUMY and text:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summ = TextRankSummarizer()
        sents = [str(s) for s in summ(parser.document, sent_count)]
        return " ".join(sents)
    # basic fallback if sumy unavailable
    return " ".join(text.split()[:200])

def _polish_english(text: str, target_words=(150, 220)) -> str:
    """
    Use Groq to create a professional, coherent summary that incorporates key claims and quotes.
    """
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        print("[Summary] GROQ_API_KEY not found. Using fallback summary generation.")
        # Enhanced fallback that tries to clean up the text
        return _create_fallback_summary(text, target_words)

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        # Clean up the input text first
        cleaned_text = _clean_transcript_for_llm(text)
        
        prompt = (
            "You are a professional journalist writing a news summary. Create a coherent, "
            f"professional summary of exactly {target_words[0]}-{target_words[1]} words from the following interview transcript. "
            "Requirements:\n"
            "1. Write in a formal, journalistic tone - NOT conversational\n"
            "2. Focus on the main topics, key statements, and important claims made\n"
            "3. Structure it as a proper news summary with clear paragraphs\n"
            "4. Remove filler words, repetitions, and conversational elements\n"
            "5. Highlight significant quotes and assertions naturally within the text\n"
            "6. Make it sound like a professional news article, not a transcript\n"
            "7. Fix any grammatical errors or unclear phrases\n"
            "8. Ensure the summary flows logically and makes sense\n\n"
            "Interview transcript:\n"
            f"{cleaned_text}"
        )
        
        resp = client.chat.completions.create(
            model=os.environ.get("M9_SUMMARY_MODEL", "llama-3.1-8b-instant"),  # Updated to current model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # Lower temperature for more consistent, professional output
            max_tokens=400,   # Ensure we don't exceed word limit
        )
        
        result = resp.choices[0].message.content.strip()
        print(f"[Summary] Groq generated {len(result)} character summary")
        return result
        
    except Exception as e:
        print(f"[Summary] Groq error: {e}")
        print("[Summary] Falling back to enhanced text processing")
        return _create_fallback_summary(text, target_words)

def _clean_transcript_for_llm(text: str) -> str:
    """Clean transcript text before sending to LLM"""
    import re
    
    # Remove repeated phrases (common in transcripts)
    words = text.split()
    cleaned_words = []
    prev_word = ""
    prev_prev_word = ""
    
    for word in words:
        # Skip if this word is the same as the previous two words (indicating repetition)
        if word.lower() == prev_word.lower() == prev_prev_word.lower():
            continue
        cleaned_words.append(word)
        prev_prev_word = prev_word
        prev_word = word
    
    # Join and clean up
    cleaned = " ".join(cleaned_words)
    
    # Remove common transcript artifacts
    cleaned = re.sub(r'\b(uh|um|you know|like)\b', '', cleaned, flags=re.I)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def _create_fallback_summary(text: str, target_words=(150, 220)) -> str:
    """Enhanced fallback summary when Groq is not available"""
    import re
    
    # Clean the text more aggressively
    cleaned = _clean_transcript_for_llm(text)
    
    # Remove repeated sentences (common in transcripts)
    sentences = re.split(r'[.!?]+', cleaned)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Filter out very short sentences and duplicates
    unique_sentences = []
    seen = set()
    for s in sentences:
        if len(s.split()) > 5:  # Only sentences with 5+ words
            # Normalize for comparison (lowercase, remove extra spaces)
            normalized = re.sub(r'\s+', ' ', s.lower().strip())
            if normalized not in seen:
                unique_sentences.append(s)
                seen.add(normalized)
    
    # If we have good unique sentences, use them
    if len(unique_sentences) >= 2:
        # Take first 2 and longest 2-3 sentences
        if len(unique_sentences) <= 4:
            selected = unique_sentences
        else:
            first_two = unique_sentences[:2]
            remaining = unique_sentences[2:]
            longest = sorted(remaining, key=len, reverse=True)[:3]
            selected = first_two + longest
    else:
        # Fallback: just take the first few sentences
        selected = sentences[:3]
    
    # Join and clean up
    summary = ". ".join(selected)
    if not summary.endswith('.'):
        summary += "."
    
    # Final cleanup - remove any remaining repetitions
    summary = _remove_sentence_repetitions(summary)
    
    # Trim to target word count
    words = summary.split()
    if len(words) > target_words[1]:
        words = words[:target_words[1]]
        summary = " ".join(words)
    
    return summary

def _remove_sentence_repetitions(text: str) -> str:
    """Remove repeated sentences from text"""
    import re
    
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    unique_sentences = []
    seen = set()
    
    for sentence in sentences:
        # Normalize for comparison
        normalized = re.sub(r'\s+', ' ', sentence.lower().strip())
        if normalized not in seen:
            unique_sentences.append(sentence)
            seen.add(normalized)
    
    return ". ".join(unique_sentences) + "."


# ---- Public function used by both orchestrator and agent ----
def summarize_and_angles(segments: List[Dict]) -> Dict:
    """
    Returns {"summary": str, "angles": List[str]}
    """
    if not segments:
        return {"summary": "", "angles": []}

    doc = _build_doc(segments)
    if not doc:
        return {"summary": "", "angles": []}

    # Extractive pass (claim-aware)
    extract = _extractive_summary(doc, sent_count=6)
    # Optional polish for cleaner English
    summary = _polish_english(extract, target_words=(150, 220))

    # Simple default angles; swap with domain-specific templates if desired
    angles = ["Policy impact", "Human-interest angle", "Data/evidence angle"]
    return {"summary": summary, "angles": angles}

# ---- Agent (kept; now delegates to summarize_and_angles above) ----
from ..orchestrator.base import BaseAgent, register
from ..db import transcripts, summaries

@register
class SummaryAnglesAgent(BaseAgent):
    name = "SummaryAnglesAgent"

    def run(self, pipeline, tools):
        iid = pipeline["interview_id"]
        tdoc = transcripts.find_one({"interview_id": iid})
        if not tdoc:
            raise RuntimeError("Transcript missing.")
        segments = tdoc.get("segments", [])
        if not segments:
            raise RuntimeError("Transcript empty.")

        sa = summarize_and_angles(segments)

        summaries.update_one(
            {"interview_id": iid},
            {"$set": {"abstract": sa.get("summary", ""), "angles": sa.get("angles", [])}},
            upsert=True
        )
        return {"summary_len": len(sa.get("summary", "")), "angles": len(sa.get("angles", []))}
