import spacy
from typing import Tuple
from backend.app.logging.logger import logger

# Lexicons for sentiment mapping based on lemmatized terms
POSITIVE_WORDS = {
    "good", "great", "awesome", "excellent", "happy", "love", "like", "best",
    "wonderful", "amazing", "beautiful", "perfect", "fantastic", "satisfy",
    "satisfied", "helpful", "useful", "easy", "fast", "nice", "enjoy", "superb",
    "outstanding", "impressed", "impressive", "smooth", "recommend",
    "well", "cool", "favorite", "efficient", "quality", "clean", "stable",
    "perfectly", "glad", "pleased", "worth"
}

NEGATIVE_WORDS = {
    "bad", "worst", "terrible", "awful", "hate", "dislike", "sad", "annoy",
    "annoyed", "useless", "broken", "fail", "failed", "slow", "difficult",
    "hard", "poor", "expensive", "defect", "defective", "error", "bug", "waste",
    "horrible", "frustrate", "frustrated", "disappoint", "disappointed", "problem",
    "issue", "worse", "annoyance", "regret", "faulty", "poorly", "junk", "garbage",
    "trash", "slowly", "crash", "crashed", "overpriced", "dislike"
}

NEGATIONS = {
    "not", "no", "never", "cannot", "n't", "neither", "nor", "none",
    "without", "lack", "rarely", "seldom"
}

# Safely load the spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    logger.warning("spaCy model 'en_core_web_sm' not found. Installing inline...")
    import subprocess
    import sys
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
    nlp = spacy.load("en_core_web_sm")

def analyze_sentiment(text: str) -> Tuple[str, float]:
    """
    Analyzes input text and outputs a sentiment label and confidence score.
    Returns:
        sentiment: 'positive', 'negative', or 'neutral'
        confidence: float in range [0.0, 1.0]
    """
    cleaned_text = text.strip() if text else ""
    if not cleaned_text:
        return "neutral", 1.0

    doc = nlp(cleaned_text)
    pos_score = 0.0
    neg_score = 0.0
    tokens = list(doc)

    for i, token in enumerate(tokens):
        lemma = token.lemma_.lower()
        word = token.text.lower()

        is_pos = (lemma in POSITIVE_WORDS) or (word in POSITIVE_WORDS)
        is_neg = (lemma in NEGATIVE_WORDS) or (word in NEGATIVE_WORDS)

        if not (is_pos or is_neg):
            continue

        # Look back up to 3 tokens for negation context
        negated = False
        start_idx = max(0, i - 3)
        for prev_token in tokens[start_idx:i]:
            prev_word = prev_token.text.lower()
            prev_lemma = prev_token.lemma_.lower()
            if (prev_word in NEGATIONS) or (prev_lemma in NEGATIONS):
                negated = True
                break

        # Accumulate valence scores with negation inversion
        if is_pos:
            if negated:
                neg_score += 1.0
            else:
                pos_score += 1.0
        elif is_neg:
            if negated:
                pos_score += 1.0
            else:
                neg_score += 1.0

    total_matches = pos_score + neg_score
    if total_matches == 0:
        # Default fallback for text with no explicit positive/negative words
        return "neutral", 0.75

    diff = pos_score - neg_score
    ratio = diff / total_matches

    if ratio > 0.15:
        sentiment = "positive"
        confidence = 0.5 + (abs(ratio) * 0.5)
    elif ratio < -0.15:
        sentiment = "negative"
        confidence = 0.5 + (abs(ratio) * 0.5)
    else:
        sentiment = "neutral"
        # For neutrality, closer ratio to zero indicates higher neutral confidence
        confidence = 1.0 - abs(ratio)

    return sentiment, round(min(confidence, 1.0), 4)
