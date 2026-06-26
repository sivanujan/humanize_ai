import re

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

def swap_ai_vocabulary(text: str) -> str:
    """Programmatically replace common AI words with human synonyms."""
    for pattern, replacement in AI_WORDS.items():
        # Case insensitive replacement
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text
