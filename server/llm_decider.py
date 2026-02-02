import logging

logger = logging.getLogger(__name__)

# Headlines that are considered too generic by themselves
GENERIC_HEADLINES = {
    "student",
    "graduate",
    "engineer",
    "software engineer",
}

# Minimal role keywords per role family
ROLE_KEYWORDS = {
    "backend": ["backend", "api", "server", "python", "java"],
    "data": ["data", "analytics", "sql", "ml"],
    "qa": ["qa", "testing", "automation"],
}


def decide_profile_tools(
    current_headline: str,
    current_summary: str,
    target_role: str,
) -> tuple[list[str], dict]:
    """
    Decide which optimization tools should be triggered for a LinkedIn profile.
    Returns:
     tools: list of tool names to execute
     decision_trace: explainable scores and reasons
    """

    tools: list[str] = []

    headline_lower = (current_headline or "").lower().strip()
    summary_lower = (current_summary or "").lower().strip()
    role_lower = (target_role or "").lower().strip()


    # Headline scoring
    headline_score = 0
    headline_reasons: list[str] = []

    # Generic headline (e.g. "Student", "Engineer")
    if headline_lower in GENERIC_HEADLINES:
        headline_score += 2
        headline_reasons.append("generic headline")

    # Missing role keyword in headline
    role_token = role_lower.split()[0] if role_lower else ""
    if role_token and role_token not in headline_lower:
        headline_score += 2
        headline_reasons.append("missing role keyword")

    # Very short headline
    if len(headline_lower) < 15:
        headline_score += 1
        headline_reasons.append("headline too short")

    # Decide headline optimization
    if headline_score >= 2:
        tools.append("optimize_headline")

    # Summary scoring
    summary_score = 0
    summary_reasons: list[str] = []

    role_key = role_lower.split()[0] if role_lower else ""
    keywords = ROLE_KEYWORDS.get(role_key, [])

    # Missing role-related keywords
    if keywords and not any(k in summary_lower for k in keywords):
        summary_score += 2
        summary_reasons.append("missing role keywords")

    # Very short summary
    if len(summary_lower) < 100:
        summary_score += 1
        summary_reasons.append("summary too short")

    # Important logic:
    # If the headline is already strong (score == 0),
    # we do NOT force a summary rewrite unless the
    # summary problem is critical (score >= 3).
    if headline_score == 0 and summary_score < 3:
        summary_score = 0
        summary_reasons.append(
            "summary acceptable given strong headline"
        )

    # Decide summary optimization
    if summary_score >= 2:
        tools.append("rewrite_summary")

    # Decision trace (for explainability / Swagger)
    decision_trace = {
        "headline": {
            "score": headline_score,
            "reasons": headline_reasons,
        },
        "summary": {
            "score": summary_score,
            "reasons": summary_reasons,
        },
    }

    logger.info("Decision trace: %s", decision_trace)
    logger.info("Final tools: %s", tools)

    return tools, decision_trace