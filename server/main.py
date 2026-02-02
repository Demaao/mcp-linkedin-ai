import logging
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from server.schemas import (
    HeadlineRequest,
    HeadlineResponse,
    SummaryRequest,
    SummaryResponse,
    LinkedInOptimizationRequest,
    LinkedInOptimizationResponse,
)
from server.tools.headline import optimize_headline
from server.tools.summary import rewrite_summary
from server.ai_orchestrator import optimize_linkedin_profile

"""
Secondary HTTP interface.

This FastAPI server is provided mainly for:
- Local testing
- Swagger documentation
- Manual usage via HTTP

The primary interface of this project is the MCP server (mcp_server.py).
"""

# Basic logging configuration for HTTP usage
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# FastAPI application instance
app = FastAPI(title="MCP LinkedIn AI Server")


# Simple health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}


# Redirect root URL to Swagger UI
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


# HTTP endpoint for headline optimization
# Wraps the optimize_headline tool
@app.post("/tools/optimize-headline", response_model=HeadlineResponse)
def optimize_headline_endpoint(data: HeadlineRequest):
    return optimize_headline(data)


# HTTP endpoint for summary rewriting
# Wraps the rewrite_summary tool
@app.post("/tools/rewrite-summary", response_model=SummaryResponse)
def rewrite_summary_endpoint(data: SummaryRequest):
    return rewrite_summary(data)


# High-level AI orchestration endpoint
# Decides which tools to apply and returns a full optimization result
@app.post("/ai/optimize-linkedin", response_model=LinkedInOptimizationResponse)
def optimize_linkedin_ai(data: LinkedInOptimizationRequest):
    return optimize_linkedin_profile(data)