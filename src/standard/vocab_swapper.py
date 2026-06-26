import re
import random
import hashlib

AI_WORDS = {
    r"\butilize\b": "use",
    r"\bleverage\b": "use",
    r"\bdemonstrate\b": "show",
    r"\bimplement\b": "build",
    r"\bfacilitate\b": "help",
    r"\bcrucial\b": "important",
    r"\bdelve\b": "look",
    r"\brobust\b": "strong",
    r"\bseamless\b": "smooth",
    r"\btapestry\b": "network",
    r"\bnavigate\b": "handle",
    r"\bmoreover\b": "additionally",
    r"\bfurthermore\b": "additionally",
    r"\bbasically\b": "essentially",
    r"\bensure\b": "make sure",
    r"\bnoting\b": "pointing out"
}

FILLER_WORDS = [
    "basically, ", "honestly, ", "pretty much, ", "kind of ", "sort of ", 
    "to be fair, ", "you know, ", "I mean, "
]

def swap_ai_vocabulary(text: str) -> str:
    """Programmatically replace common AI words and inject human noise."""
    # 1. Swap AI vocabulary
    for pattern, replacement in AI_WORDS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
    # 2. Inject human noise deterministically so it doesn't fluctuate
    seed_val = int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16)
    random.seed(seed_val)
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    noisy_sentences = []
    
    for i, sentence in enumerate(sentences):
        # 20% chance to inject a filler word at the start of a sentence
        if random.random() < 0.20 and len(sentence) > 15:
            filler = random.choice(FILLER_WORDS)
            sentence = filler + sentence[0].lower() + sentence[1:]
            
        # 10% chance to drop the ending punctuation (intentional grammar quirk)
        if random.random() < 0.10 and (sentence.endswith('.') or sentence.endswith(',')):
            sentence = sentence[:-1]
            
        noisy_sentences.append(sentence)
        
    return " ".join(noisy_sentences).strip()
