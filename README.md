# LinkedIn AI Optimization Server (MCP-based)

This project implements an **AI-first backend service** for optimizing LinkedIn profiles
(headlines and summaries) using a **Model Context Protocol (MCP)** server.

The system is designed for **AI agents and developer tools** (e.g. Cursor, Claude).

---

## Project Goals

The main goal of this project is to demonstrate how to build a **production-oriented AI system**
that goes beyond simply calling an LLM.

Key design goals:
- Deterministic, explainable decision-making
- Optional and replaceable LLM usage
- Clear separation between *decision*, *generation*, and *orchestration*
- AI-native interfaces (MCP) alongside a traditional HTTP API for testing

---

## High-Level Architecture

The system is composed of four logical layers:

### 1. Decision Layer (Deterministic)

A lightweight rule-based engine analyzes the current LinkedIn profile and the target role
and decides **which optimization tools should be invoked**.

Characteristics:
- No LLM usage
- Fully deterministic
- Produces a **decision trace** (scores + reasons)
- Easy to debug, test, and extend

This layer answers the question:
> *Should anything be optimized at all?*

---

### 2. Tool Layer (Business Logic)

Each optimization task is implemented as an isolated tool:

- Headline optimization
- Summary rewriting

Tool properties:
- Clear input/output schemas
- Can operate with or without an LLM
- Contain no orchestration logic
- Support rule-based fallbacks

LLMs are treated as **optional generators**, not required dependencies.

---

### 3. Orchestration Layer

The orchestration layer coordinates execution across tools.

Responsibilities:
- Executes only the tools selected by the decision layer
- Aggregates results into a single response
- Tracks which tools were used
- Tracks whether any LLM was actually invoked
- Preserves explainability data

This layer connects **decision logic** with **execution**.

---

### 4. Interfaces

The system exposes two interfaces:

#### MCP Server (Primary Interface)
- Communicates over `stdio`
- Designed for AI-driven usage
- Exposes tools, resources, and prompts
- Intended for orchestration by AI models (Cursor, Claude, etc.)

#### HTTP API (Secondary Interface)
- Built with FastAPI
- Used for:
  - Local testing
  - Swagger documentation
  - Manual inspection
- Contains no business logic

---

## Why MCP?

Model Context Protocol (MCP) allows AI models to:
- Discover available tools
- Decide when to use them
- Consume structured outputs
- Combine tools with reasoning

---

## Why Deterministic Decisions?

All decisions about *whether* to optimize a headline or summary are made **without an LLM**.

Benefits:
- Predictable behavior
- Full explainability
- Cost control
- Safer outputs
- Easier debugging and testing

LLMs are used **only for text generation**, never for decision-making.

---


 How to Run

### Run MCP Server (Primary Interface)

```bash
python mcp_server.py

Run HTTP API (Secondary Interface):
uvicorn server.http_api:app --reload


Project Structure:
server/
├── schemas.py              # Typed request/response contracts
├── llm_client.py           # Optional OpenAI client integration
├── llm_decider.py          # Deterministic scoring & decision logic
├── ai_orchestrator.py      # Central orchestration logic
├── tools/
│   ├── headline.py         # Headline optimization tool
│   └── summary.py          # Summary rewriting tool

├── mcp_server.py           # Primary MCP (stdio) interface
