"""
Optional OpenAI LLM integration for improving LinkedIn headlines and summaries.

This module is designed to be non-critical:
- If OpenAI is not installed
- If no API key is provided
- Or if any API call fails

All functions will safely fall back to returning None.
"""

import logging
import os

# Attempt to load environment variables from a .env file 
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)

# Flag indicating whether the OpenAI SDK is available
OPENAI_AVAILABLE = False
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    pass


def _client() -> "OpenAI | None":
    """
    Create and return an OpenAI client if possible.

    Conditions:
    - OPENAI_API_KEY must exist in environment variables
    - The OpenAI package must be installed

    Returns:
        OpenAI client instance, or None if unavailable.
    """
    key = os.environ.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

    # Reject empty, missing, or placeholder keys
    if not key or key.strip() in ("", "example_key"):
        return None

    if not OPENAI_AVAILABLE:
        return None

    return OpenAI(api_key=key)


def improve_headline_with_llm(
    current_headline: str,
    target_role: str
) -> tuple[str, str] | None:
    """
    Improve a LinkedIn headline using an LLM.

    The model is instructed to:
    - Emphasize the target role
    - Keep the headline concise (under 120 characters)
    - Provide a short explanation of the change

    Returns:
        (improved_headline, explanation) or None if LLM is unavailable.
    """
    client = _client()
    if not client:
        return None

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a LinkedIn profile expert. Improve the user's headline "
                        "to better match the target job role. Keep it concise (under 120 characters). "
                        "Return only the improved headline, then on a new line write "
                        "'EXPLANATION:' followed by one short sentence."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Target role: {target_role}\n"
                        f"Current headline: {current_headline}"
                    ),
                },
            ],
            max_tokens=150,
        )

        text = (response.choices[0].message.content or "").strip()

        # Parse model output into headline + explanation if formatted as requested
        if "EXPLANATION:" in text:
            headline_part, _, expl_part = text.partition("EXPLANATION:")
            improved = headline_part.strip().strip('"')
            explanation = expl_part.strip()
        else:
            # Fallback if model does not follow the exact format
            improved = text[:120]
            explanation = "Headline tailored to the target role."

        if improved:
            logger.info("OpenAI headline optimization used")
            return improved, explanation

    except Exception as e:
        # Any API or network error is logged but not raised
        logger.warning("OpenAI headline call failed: %s", e)

    return None


def improve_summary_with_llm(
    current_summary: str,
    target_role: str
) -> tuple[str, str] | None:
    """
    Improve a LinkedIn summary section using an LLM.

    The model is instructed to:
    - Preserve the user's real experience and tone
    - Add role-relevant keywords
    - Improve structure and readability
    - Produce short paragraphs
    - Provide a brief explanation of the changes

    Returns:
        (improved_summary, explanation) or None if LLM is unavailable.
    """
    client = _client()
    if not client:
        return None

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a LinkedIn profile expert. Rewrite the user's About/Summary "
                        "to align with the target job role. Keep the user's real experience "
                        "and wording where possible, while improving structure and keywords. "
                        "Write 2–4 short paragraphs. Then add a new line with "
                        "'EXPLANATION:' followed by one short sentence."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Target role: {target_role}\n"
                        f"Current summary:\n{current_summary[:2000]}"
                    ),
                },
            ],
            max_tokens=600,
        )

        text = (response.choices[0].message.content or "").strip()

        # Parse summary and explanation if formatted correctly
        if "EXPLANATION:" in text:
            summary_part, _, expl_part = text.partition("EXPLANATION:")
            improved = summary_part.strip()
            explanation = expl_part.strip()
        else:
            improved = text
            explanation = "Summary tailored to the target role."

        if improved:
            logger.info("OpenAI summary optimization used")
            return improved, explanation

    except Exception as e:
        # Fail gracefully and allow the system to continue without LLM support
        logger.warning("OpenAI summary call failed: %s", e)

    return None