"""LLM humanization rewriter (OpenAI-compatible providers).

Supports DeepSeek, OpenRouter, and any compatible endpoint via config.
Carries previous round history for context-aware rewriting.
"""

from .llm_client import chat_completions

SYSTEM_PROMPT = """You are a tired university student writing this at 2am before a deadline. Write casually, make it slightly imperfect, like a real person rushing to finish.

Rules:
1. Do not use formal transitions or bullet points. Output everything as continuous block paragraphs. If you see a list or bullet points in the input, physically dissolve them into a single rambling paragraph.
2. Vary sentence length extremely randomly.
3. Use casual contractions (it's, don't, we'll).
4. Preserve technical terms, but explain them slightly casually.
5. NEVER use words like "crucial", "leverage", "delve", "robust", "facilitate", "utilize".
6. DO NOT use preambles or explanations. Output ONLY the text.
7. YOU MUST WRAP YOUR FINAL TEXT IN <text> AND </text> TAGS."""

def llm_rewrite(
    text: str,
    target_language: str,
    api_key: str,
    base_url: str,
    model: str,
    history: dict | None = None,
    temperature: float = 1.3,
    extra_headers: dict | None = None,
    provider: str | None = None,
) -> str:
    """Rewrite text into target language with humanization."""
    user_prompt = f"Translate to {target_language} (if not already). Rewrite it casually like a tired student. ONLY output the text wrapped in <text></text> tags, with NO PREAMBLE:\n\n{text}"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.append({
            "role": "user",
            "content": f"Translate to {target_language}. Rewrite it casually like a tired student. ONLY output the text wrapped in <text></text> tags, with NO PREAMBLE:\n\n{history['input']}",
        })
        messages.append({
            "role": "assistant",
            "content": f"<text>{history['output']}</text>",
        })

    messages.append({"role": "user", "content": user_prompt})

    raw_response = chat_completions(
        messages,
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=temperature,
        extra_headers=extra_headers,
        provider=provider,
    )
    
    import re
    match = re.search(r"<text>(.*?)</text>", raw_response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Fallback cleanup just in case
    cleaned = re.sub(r"^(Here is|Here's|Sure|Okay|Certainly|Below is).*?:\s*\n", "", raw_response, flags=re.IGNORECASE).strip()
    return cleaned


def deepseek_rewrite(
    text: str,
    target_language: str,
    api_key: str,
    history: dict | None = None,
    model: str = "deepseek-chat",
    temperature: float = 1.3,
    base_url: str = "https://api.deepseek.com",
    extra_headers: dict | None = None,
) -> str:
    """Backward-compatible alias for direct DeepSeek usage."""
    return llm_rewrite(
        text=text,
        target_language=target_language,
        api_key=api_key,
        base_url=base_url,
        model=model,
        history=history,
        temperature=temperature,
        extra_headers=extra_headers,
    )
