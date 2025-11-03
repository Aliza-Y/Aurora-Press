# ================================
#  AuroraPress Module 5 – SEO Optimizer (Offline, CPU-Only)
# ================================
import re, time, json, logging, nltk, textstat, yake, difflib
from typing import List, Dict, Any, Optional
from collections import Counter
from datetime import datetime
from bs4 import BeautifulSoup
from slugify import slugify
from keybert import KeyBERT
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline
import language_tool_python

# -------------------- Logging --------------------
logger = logging.getLogger("seo_optimizer_offline")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

# -------------------- NLP Setup --------------------
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)
try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords", quiet=True)
from nltk.corpus import stopwords
STOPWORDS = set(stopwords.words("english"))

# -------------------- Model Initialization --------------------
logger.info("Loading models... (may take 1–2 minutes on first run)")
t5_model = pipeline("text2text-generation", model="google/flan-t5-large", device_map="cpu")
intent_model = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device_map="cpu")
kw_model = KeyBERT(model="sentence-transformers/all-MiniLM-L6-v2")

# Try to initialize LanguageTool, but make it optional
try:
    lang_tool = language_tool_python.LanguageTool('en-US')
    LANG_TOOL_AVAILABLE = True
    logger.info("✅ LanguageTool initialized successfully")
except Exception as e:
    logger.warning(f"⚠️ LanguageTool not available: {e}")
    logger.warning("⚠️ Grammar checking will be disabled")
    lang_tool = None
    LANG_TOOL_AVAILABLE = False

logger.info("✅ All local models loaded successfully.")

# -------------------- Utilities --------------------
def clean_html(text:str)->str:
    soup = BeautifulSoup(text, "html.parser")
    return re.sub(r"\s+\n", "\n", soup.get_text(separator="\n")).strip()

def sentences(txt:str)->List[str]:
    return [s.strip() for s in nltk.sent_tokenize(txt) if s.strip()]

def generate_slug(title:str)->str:
    return slugify(title, max_length=70, word_boundary=True)

# -------------------- Keyword Extraction --------------------
def extract_keywords(text:str)->Dict[str, List[str]]:
    """Return primary, secondary and long-tail keywords."""
    yake_ex = yake.KeywordExtractor(lan="en", n=3, top=40)
    yake_kws = [kw for kw, _ in yake_ex.extract_keywords(text)]
    keybert_kws = [kw for kw, _ in kw_model.extract_keywords(text, top_n=25, use_mmr=True)]
    tfidf_vec = TfidfVectorizer(stop_words='english', ngram_range=(1,2))
    feats = tfidf_vec.fit_transform(sentences(text))
    tfidf_kws = tfidf_vec.get_feature_names_out()
    combined = list(dict.fromkeys(yake_kws + keybert_kws + list(tfidf_kws)))[:30]
    # Filter
    combined = [k.lower() for k in combined if len(k.split())<=4 and k.isalpha()==False or True]
    return {
        "primary": combined[:3],
        "secondary": combined[3:10],
        "long_tail": combined[10:20]
    }

# -------------------- Intent Detection --------------------
def detect_intent(text:str)->str:
    labels = ["informational","commercial","transactional"]
    res = intent_model(text[:512], candidate_labels=labels)
    return res['labels'][0]

# -------------------- Grammar Cleanup --------------------
def grammar_cleanup(text:str)->str:
    if not LANG_TOOL_AVAILABLE or lang_tool is None:
        return text  # Return original text if LanguageTool is not available
    
    try:
        return language_tool_python.utils.correct(text, lang_tool.check(text))
    except Exception as e:
        logger.warning(f"Grammar cleanup failed: {e}")
        return text

# -------------------- Content Enhancement --------------------
def enhance_content(text:str, primary_kws:List[str], intent:str)->str:
    """Enhance content structure for SEO without relying on T5 model."""
    primary = primary_kws[0] if primary_kws else ""
    
    # Split text into sentences
    sentences = text.split('. ')
    if len(sentences) <= 1:
        return text
    
    # Create a well-structured article
    structured_content = ""
    
    # Introduction paragraph
    intro_sentences = sentences[:2] if len(sentences) >= 2 else sentences
    structured_content += '. '.join(intro_sentences) + '.\n\n'
    
    # Add first heading if we have enough content
    if len(sentences) > 3:
        structured_content += "## Key Developments\n\n"
        
        # Add more sentences under this heading
        remaining_sentences = sentences[2:]
        mid_point = len(remaining_sentences) // 2
        
        for i, sentence in enumerate(remaining_sentences[:mid_point]):
            if sentence.strip():
                structured_content += sentence + '.\n\n'
        
        # Add second heading if we have enough content
        if len(remaining_sentences) > mid_point:
            structured_content += "## Impact and Response\n\n"
            
            for sentence in remaining_sentences[mid_point:]:
                if sentence.strip():
                    structured_content += sentence + '.\n\n'
    
    # If we don't have enough content for headings, just add paragraphs
    else:
        for sentence in sentences[2:]:
            if sentence.strip():
                structured_content += sentence + '.\n\n'
    
    # Add some SEO-friendly elements
    if primary and primary.lower() not in structured_content.lower():
        # Add primary keyword naturally
        structured_content = structured_content.replace(
            sentences[0], 
            sentences[0] + f" This development regarding {primary} has significant implications."
        )
    
    # Add transition words
    structured_content = structured_content.replace(
        "However,", "Furthermore,"
    ).replace(
        "According to sources,", "Additionally,"
    )
    
    return grammar_cleanup(structured_content)

# -------------------- Title & Meta Generation --------------------
def optimize_title_meta(title:str, content:str, primary_kw:str, intent:str)->Dict[str,str]:
    title_prompt = f"""Rewrite the title to 30–60 chars, compelling and {intent}-intent optimized.
Primary keyword: {primary_kw}
Title: {title}"""
    meta_prompt = f"""Write a meta description (150–160 chars) summarizing content attractively.
Primary keyword: {primary_kw}
Content: {content[:500]}"""
    new_title = t5_model(title_prompt, max_new_tokens=50, do_sample=True)[0]['generated_text']
    new_meta = t5_model(meta_prompt, max_new_tokens=80, do_sample=True)[0]['generated_text']
    return {"title": new_title.strip(), "meta": new_meta.strip()}

# -------------------- Readability & Structure --------------------
def analyze_readability(text:str)->Dict[str,float]:
    return {
        "flesch": textstat.flesch_reading_ease(text),
        "grade": textstat.flesch_kincaid_grade(text),
        "gunning_fog": textstat.gunning_fog(text)
    }

def analyze_structure(text:str)->Dict[str,float]:
    paras = [p for p in text.split('\n\n') if p.strip()]
    sent_counts = [len(sentences(p)) for p in paras]
    avg_sent_len = sum(len(s.split()) for s in sentences(text))/max(len(sentences(text)),1)
    return {
        "paragraphs": len(paras),
        "avg_sentences_per_para": sum(sent_counts)/max(len(sent_counts),1),
        "avg_sentence_length": avg_sent_len
    }

# -------------------- SEO Scoring --------------------
def seo_score(text:str, title:str, meta:str, kws:Dict[str,List[str]], read:Dict[str,float])->float:
    score = 0
    wc = len(text.split())
    
    # Word count scoring (more lenient)
    if wc >= 300: score += 15  # Minimum content
    if wc >= 500: score += 10  # Good length
    if wc >= 800: score += 10  # Excellent length
    
    # Readability scoring (more lenient)
    if read["flesch"] >= 30: score += 10  # Not too difficult
    if read["flesch"] >= 50: score += 10  # Good readability
    if read["flesch"] >= 70: score += 5   # Excellent readability
    
    # Keyword presence
    if any(k in text.lower() for k in kws["primary"]): score += 15
    if len(kws["primary"]) >= 2: score += 5  # Multiple primary keywords
    
    # Meta description
    if 120 <= len(meta) <= 160: score += 10
    elif 100 <= len(meta) <= 180: score += 5  # Acceptable range
    
    # Structure scoring
    if re.search(r'^#{1,6}\s', text, re.M): score += 10  # Has headings
    paragraphs = len([p for p in text.split('\n\n') if p.strip()])
    if paragraphs >= 3: score += 10  # Multiple paragraphs
    if paragraphs >= 5: score += 5   # Well-structured
    
    # Title scoring
    if 20 <= len(title) <= 70: score += 10
    elif 15 <= len(title) <= 80: score += 5  # Acceptable range
    
    # Content quality indicators
    if any(word in text.lower() for word in ['however', 'therefore', 'moreover', 'furthermore']): score += 5
    if re.search(r'\d{4}', text): score += 5  # Has year/date
    
    return round(min(score,100.0),1)

# -------------------- Main Optimization Pipeline --------------------
def optimize_article(title:str, content:str)->Dict[str,Any]:
    logger.info("Running SEO optimization pipeline...")
    cleaned = clean_html(content)
    kws = extract_keywords(cleaned)
    intent = detect_intent(cleaned)
    enhanced = enhance_content(cleaned, kws["primary"], intent)
    title_meta = optimize_title_meta(title, enhanced, kws["primary"][0] if kws["primary"] else "", intent)
    read = analyze_readability(enhanced)
    struct = analyze_structure(enhanced)
    score = seo_score(enhanced, title_meta["title"], title_meta["meta"], kws, read)

    return {
        "original_title": title,
        "optimized_title": title_meta["title"],
        "meta_description": title_meta["meta"],
        "optimized_content": enhanced,
        "keywords": kws,
        "intent": intent,
        "readability": read,
        "structure": struct,
        "seo_score": score,
        "slug": generate_slug(title_meta["title"]),
        "optimized_at": datetime.now().isoformat()
    }
