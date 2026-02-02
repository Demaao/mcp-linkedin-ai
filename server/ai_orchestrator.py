from server.schemas import (
    LinkedInOptimizationRequest,
    LinkedInOptimizationResponse,
    HeadlineRequest,
    SummaryRequest,
)
from server.tools.headline import optimize_headline
from server.tools.summary import rewrite_summary
from server.llm_decider import decide_profile_tools


def optimize_linkedin_profile(
    data: LinkedInOptimizationRequest,
) -> LinkedInOptimizationResponse:
    """
    Orchestrates the full LinkedIn profile optimization flow.
    Decides which tools to run and applies them conditionally.
    """

    # Decide which optimization tools are needed based on heuristic rules
    tools_to_use, decision_trace = decide_profile_tools(
        data.current_headline,
        data.current_summary,
        data.target_role,
    )

    # Default: keep original values if no optimization is applied
    optimized_headline = data.current_headline
    optimized_summary = data.current_summary
    tools_used: list[str] = []

    # Tracks whether any LLM-based tool was actually used
    llm_used = False

    # Optimize headline if decision logic requires it
    if "optimize_headline" in tools_to_use:
        headline_result = optimize_headline(
            HeadlineRequest(
                current_headline=data.current_headline,
                target_role=data.target_role,
            )
        )
        optimized_headline = headline_result.improved_headline
        tools_used.append("optimize_headline")

        # Propagate LLM usage information
        llm_used = llm_used or headline_result.llm_used

    # Rewrite summary if decision logic requires it
    if "rewrite_summary" in tools_to_use:
        summary_result = rewrite_summary(
            SummaryRequest(
                current_summary=data.current_summary,
                target_role=data.target_role,
            )
        )
        optimized_summary = summary_result.improved_summary
        tools_used.append("rewrite_summary")

        # Propagate LLM usage information
        llm_used = llm_used or summary_result.llm_used

    # Return a structured response with results and explainability data
    return LinkedInOptimizationResponse(
        optimized_headline=optimized_headline,
        optimized_summary=optimized_summary,
        tools_used=tools_used,
        decision_trace=decision_trace,
        llm_used=llm_used,
    )