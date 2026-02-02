from server.schemas import HeadlineRequest, HeadlineResponse

# Try to import the optional LLM-based headline improver.
# If unavailable, the system will fall back to rule-based logic.
try:
    from server.llm_client import improve_headline_with_llm
except ImportError:
    improve_headline_with_llm = None


# Short role-specific taglines to enrich LinkedIn headlines
# These help make headlines more specific and ATS-friendly
ROLE_TAGLINES: dict[str, str] = {
    "backend developer": "APIs & Server-Side Systems",
    "frontend developer": "React & Modern Web",
    "data analyst": "Data & Analytics",
    "data scientist": "ML & Data-Driven Insights",
    "qa engineer": "Testing & Quality Assurance",
    "devops engineer": "CI/CD & Cloud",
    "full stack developer": "End-to-End Development",
    "software engineer": "Software Development",
    "mobile developer": "iOS & Android",
    "ml engineer": "Machine Learning & Production ML",
    "cloud engineer": "Cloud & Infrastructure",
    "security engineer": "Application & Cloud Security",
    "product manager": "Product & Roadmap",
    "technical lead": "Architecture & Team Leadership",
}


def _normalize_role(role: str) -> str:
    """
    Normalize the target role to match known role taglines.
    Allows partial or approximate role names.
    """
    r = role.lower().strip()

    # Exact match
    if r in ROLE_TAGLINES:
        return r

    # Fallback: match by first token (for example:"backend" - "backend developer")
    first = (r.split() or [r])[0]
    for key in ROLE_TAGLINES:
        if key.startswith(first) or first in key:
            return key

    return ""


def optimize_headline(data: HeadlineRequest) -> HeadlineResponse:
    """
    Optimize a LinkedIn headline using either:
    - An optional LLM (if available), or
    - A deterministic rule-based fallback.
    """
    target = data.target_role.strip()
    current = (data.current_headline or "").strip()

    # Attempt LLM-based optimization first (if enabled)
    if improve_headline_with_llm:
        llm_result = improve_headline_with_llm(current, target)
        if llm_result:
            return HeadlineResponse(
                improved_headline=llm_result[0],
                explanation=llm_result[1],
                llm_used=True,
            )

    # Fallback: rule-based headline construction
    role_key = _normalize_role(target)

    if role_key and role_key in ROLE_TAGLINES:
        tagline = ROLE_TAGLINES[role_key]
        optimized = f"{target} | {tagline}"
    else:
        optimized = target

    # Generate an explanation based on the quality of the original headline
    if current and current.lower() not in (
        "student",
        "graduate",
        "engineer",
        "software engineer",
    ):
        explanation = (
            f"Headline focused on target role '{target}' with a clear specialization. "
            "Your existing headline was considered; you can manually merge in specific details "
            "(e.g. years of experience) if needed."
        )
    else:
        explanation = (
            "Headline rewritten to clearly reflect the target role and a relevant focus area."
        )

    return HeadlineResponse(
        improved_headline=optimized,
        explanation=explanation,
        llm_used=False,
    )