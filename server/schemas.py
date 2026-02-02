from pydantic import BaseModel


# Request model for headline optimization
# Contains the current headline and the desired target role
class HeadlineRequest(BaseModel):
    current_headline: str
    target_role: str


# Response model for headline optimization
# Includes the improved headline, explanation, and whether an LLM was used
class HeadlineResponse(BaseModel):
    improved_headline: str
    explanation: str
    llm_used: bool


# Request model for summary optimization
# Contains the current summary text and the desired target role
class SummaryRequest(BaseModel):
    current_summary: str
    target_role: str


# Response model for summary optimization
# Includes the improved summary, explanation, and whether an LLM was used
class SummaryResponse(BaseModel):
    improved_summary: str
    explanation: str
    llm_used: bool


# Request model for full LinkedIn profile optimization
# Used when optimizing both headline and summary together
class LinkedInOptimizationRequest(BaseModel):
    current_headline: str
    current_summary: str
    target_role: str


# Represents scoring details for a single section (headline or summary)
# Used for explainability and debugging
class DecisionTrace(BaseModel):
    score: int
    reasons: list[str]


# Response model for full LinkedIn profile optimization
# Includes final results, applied tools, decision trace, and LLM usage flag
class LinkedInOptimizationResponse(BaseModel):
    optimized_headline: str
    optimized_summary: str
    tools_used: list[str]
    decision_trace: dict[str, DecisionTrace]
    llm_used: bool