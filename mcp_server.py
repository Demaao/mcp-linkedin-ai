"""
LinkedIn AI MCP Server – Model Context Protocol server exposing LinkedIn optimization tools.

Primary interface: MCP (stdio)
This server exposes AI tools intended for model-driven usage (e.g. Cursor, Claude),

Run with:
    python mcp_server.py
"""

import logging
import sys

# Ensure logs go to stderr so stdio is not corrupted
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(name)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("linkedin-mcp")

# MCP SDK: use FastMCP for tool registration
try:
    from mcp.server.fastmcp import FastMCP 
except ImportError:
    logger.error("MCP SDK not installed. Run: pip install mcp")
    sys.exit(1)

from server.schemas import HeadlineRequest, SummaryRequest
from server.tools.headline import optimize_headline
from server.tools.summary import rewrite_summary


# MCP Server Definition
mcp = FastMCP(
    "linkedin-ai",
    instructions=(
        "MCP tools for optimizing LinkedIn profiles. "
        "The server exposes focused tools for headline and summary rewriting, "
        "intended for AI-driven orchestration rather than direct user interaction."
    ),
)


# MCP Tools
@mcp.tool()
def optimize_linkedin_headline(current_headline: str, target_role: str) -> str:
    """
    Improve a LinkedIn headline to better match a target job role.
    Use when the model needs to make the user's role and specialization clearer
    in the LinkedIn headline.
    """
    req = HeadlineRequest(
        current_headline=current_headline,
        target_role=target_role,
    )
    result = optimize_headline(req)

    return (
        f"Improved headline: {result.improved_headline}\n"
        f"Explanation: {result.explanation}"
    )


@mcp.tool()
def rewrite_linkedin_summary(current_summary: str, target_role: str) -> str:
    """
    Rewrite a LinkedIn Summary section to align with a target job role.
    Use when the model determines that the summary does not sufficiently reflect
    the user's role, experience level, or relevant keywords.
    """
    req = SummaryRequest(
        current_summary=current_summary,
        target_role=target_role,
    )
    result = rewrite_summary(req)

    return (
        f"Improved summary: {result.improved_summary}\n"
        f"Explanation: {result.explanation}"
    )


# MCP Resources
@mcp.resource("linkedin://best-practices")
def linkedin_best_practices() -> str:
    """
    A short, static reference for LinkedIn profile best practices.
    Intended as contextual guidance for AI models.
    """
    return 

# MCP Prompt Helpers
@mcp.prompt()
def optimize_profile_for_role(
    target_role: str,
    current_headline: str = "",
    current_summary: str = "",
) -> str:
    """
    Generate a high-level prompt to guide an AI model
    through optimizing a LinkedIn profile for a specific role.
    """
    parts = [
        f"Optimize this LinkedIn profile for the role: **{target_role}**."
    ]

    if current_headline:
        parts.append(f"Current headline: {current_headline}")

    if current_summary:
        parts.append(f"Current summary (excerpt): {current_summary[:200]}...")

    parts.append(
        "Use the available tools to improve clarity, role alignment, "
        "and relevance of the headline and summary."
    )

    return "\n".join(parts)


# Entry Point
def main() -> None:
    logger.info("Starting LinkedIn AI MCP server (stdio)")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()