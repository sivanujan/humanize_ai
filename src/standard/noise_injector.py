import random
import re

FILLER_WORDS = ["basically, ", "honestly, ", "kind of ", "pretty much "]

def inject_noise(text: str) -> str:
    """Inject intentional programmatic noise to destroy LLM fingerprints."""
    if not text.strip():
        return text
        
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if not sentences:
        return text
        
    # 1. Random Filler Word
    if random.random() < 0.6:  # 60% chance per paragraph
        target_idx = random.randint(0, len(sentences) - 1)
        # Only inject if sentence starts with a letter
        if sentences[target_idx] and sentences[target_idx][0].isalpha():
            filler = random.choice(FILLER_WORDS)
            if filler.strip().endswith(","):
                sentences[target_idx] = filler + sentences[target_idx][0].lower() + sentences[target_idx][1:]
            else:
                sentences[target_idx] = filler + sentences[target_idx]

    # 2. Occasional Comma Splice / Quirks
    for i in range(len(sentences)):
        # Swap "which" for "that" (very common human mistake)
        if random.random() < 0.3:
            sentences[i] = re.sub(r'\bwhich\b', 'that', sentences[i])
            
        # Comma splice: join two short sentences occasionally
        if i < len(sentences) - 1 and random.random() < 0.2:
            s1 = sentences[i].strip()
            s2 = sentences[i+1].strip()
            if s1 and s2 and 20 < len(s1) < 60 and 20 < len(s2) < 60:
                if s1[-1] in '.!?':
                    s1 = s1[:-1]
                sentences[i] = s1 + ", " + s2[0].lower() + s2[1:]
                sentences[i+1] = "" # Empty the next one
                
    # Filter out empty sentences from splices
    sentences = [s for s in sentences if s.strip()]
    
    return " ".join(sentences)
