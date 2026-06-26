"""
Standard Pipeline v1.5.1 — Multi-language translation chain with LLM humanization.

Pipeline (4 steps):
  Step 1: Input (EN) → Chinese — DeepSeek humanization rewrite
  Step 2: Chinese → Japanese — DeepSeek humanization rewrite (with history)
  Step 3: Japanese → Finnish — Google Translate (first translation hop)
  Step 4: Finnish → Target (EN) — Niutrans (second translation hop)

This chain was selected after empirical testing against AI detectors on
50+ sample texts. See `examples/showcase/` for input/output traces of all
4 intermediate steps on 5 real samples.
"""

import time
import click
import toml

from .llm_client import resolve_llm_config
from .translators import google_translate, niutrans_translate
from .llm_rewriter import llm_rewrite
from .vocab_swapper import swap_ai_vocabulary

def run_standard_pipeline(text: str, config: dict, target_lang: str = "en") -> dict:
    """Run the Standard humanization pipeline.

    Args:
        text: Input text to humanize.
        config: Configuration dict loaded from config.toml.
        target_lang: Target language code for final output (default: "en").

    Returns:
        dict with keys:
            - 'result': final humanized text
            - 'steps': list of {step, engine, direction, output, length}
            - 'processing_time_ms': total elapsed time in milliseconds
    """
    llm = resolve_llm_config(config)
    niutrans_key = config["api_keys"]["niutrans_api_key"]
    intermediate_lang = config.get("pipeline", {}).get("intermediate_lang", "fi")
    engine_name = llm["display_name"]

    steps = []
    start = time.time()

    # Split into paragraphs
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    processed_paragraphs = []
    
    from collections import defaultdict
    # We will aggregate step outputs for the UI
    aggregated_steps = defaultdict(str)
    
    # 3 distinct language families to maximize structural scrambling
    languages = [
        ("ja", "Japanese"),
        ("ta", "Tamil"),
        ("ru", "Russian")
    ]
    
    for i, para in enumerate(paragraphs):
        # Step 1: LLM Rewrite (Software Engineering Student Persona)
        target_name = "English" if target_lang.lower() == "en" else target_lang
        step1 = llm_rewrite(
            text=para,
            target_language=target_name,
            api_key=llm["api_key"],
            base_url=llm["base_url"],
            model=llm["model"],
            history=None,
            temperature=llm["temperature"],
            extra_headers=llm["extra_headers"],
            provider=llm["provider"],
        )
        # Strip potential markdown formatting
        step1 = step1.replace("**", "").replace("### ", "").replace("## ", "").replace("# ", "")
        aggregated_steps[1] += step1 + "\n\n"
        
        current_text = step1
        
        # Iteratively scramble through languages
        for idx, (lang_code, _) in enumerate(languages):
            backup_text = current_text
            try:
                translated_fwd = google_translate(current_text, source="en", target=lang_code)
                time.sleep(1)
                current_text = google_translate(translated_fwd, source=lang_code, target="en")
                time.sleep(1)
            except Exception as e:
                print(f"Skipping {lang_code} hop due to translation error: {e}")
                current_text = backup_text # Rollback so we don't leave text in a foreign language
                
            aggregated_steps[idx + 2] += current_text + "\n\n"
        
        # Programmatic Vocabulary Swap (replaces AI words like 'basically', 'utilize')
        final_para = swap_ai_vocabulary(current_text)
        
        processed_paragraphs.append(final_para)

    # Add Step 1 (LLM) to UI steps
    steps.append({
        "step": 1, "engine": engine_name,
        "direction": f"Input → {target_lang.upper()} (Student Persona)",
        "output": aggregated_steps[1].strip(), "length": len(aggregated_steps[1]),
    })
    
    # Add Translation hops to UI steps
    for idx, (_, lang_name) in enumerate(languages):
        steps.append({
            "step": idx + 2, "engine": "Google",
            "direction": f"English → {lang_name} → English",
            "output": aggregated_steps[idx + 2].strip(), "length": len(aggregated_steps[idx + 2]),
        })
    
    # Add Final Output to UI steps
    final_output = "\n\n".join(processed_paragraphs)
    steps.append({
        "step": len(languages) + 2, "engine": "Google + Python",
        "direction": "Final Scramble & Vocab Swap",
        "output": final_output, "length": len(final_output),
    })

    elapsed_ms = int((time.time() - start) * 1000)

    return {
        "result": final_output,
        "steps": steps,
        "processing_time_ms": elapsed_ms,
    }


def _lang_code_to_niutrans(code: str) -> str:
    """Map common language codes to Niutrans format."""
    mapping = {
        "en": "en", "zh": "zh", "ja": "ja", "ko": "ko",
        "fr": "fr", "de": "de", "es": "es", "pt": "pt",
        "ru": "ru", "ar": "ar", "it": "it", "nl": "nl",
        "fi": "fi",
    }
    return mapping.get(code, code)


@click.command()
@click.option("--input", "input_text", required=True, help="Input text or path to text file")
@click.option("--target", default="en", help="Target language code (default: en)")
@click.option("--config", default="config/config.toml", help="Config file path")
@click.option("--output", default=None, help="Output file path")
@click.option("--verbose", is_flag=True, help="Show step-by-step progress")
def main(input_text, target, config, output, verbose):
    """Run the Standard humanization pipeline."""
    import os

    if os.path.isfile(input_text):
        with open(input_text, "r", encoding="utf-8") as f:
            input_text = f.read()

    cfg = toml.load(config)
    result = run_standard_pipeline(input_text, cfg, target_lang=target)

    if verbose:
        click.echo("\n--- Pipeline Steps ---")
        for s in result["steps"]:
            click.echo(f"  Step {s['step']}: {s['engine']} | {s['direction']} | {s['length']} chars")
        click.echo(f"  Total: {result['processing_time_ms']}ms\n")

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(result["result"])
        click.echo(f"Written to {output}")
    else:
        click.echo(result["result"])


if __name__ == "__main__":
    main()
