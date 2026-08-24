# Agent Project Context

## Goal

Learn and understand the core concepts behind AI agents by implementing them from scratch.

The current research agent is a **learning vehicle, not the end product**. Do not optimize it into a production-quality research agent or keep adding features simply to make the application more capable.

The primary goal is to develop a mental model of:

* how agents interact with LLMs
* how agents maintain and manipulate state
* how decisions are made across multiple steps
* how tools and environments interact with the agent
* why different agent architectures exist
* where agent systems fail and how those failures are handled
* the trade-offs behind different agent designs

The progression should be:

```text
Understand a concept
        ↓
Implement the mechanism from scratch
        ↓
Experiment / debug it
        ↓
Understand its limitations and failure modes
        ↓
Move one layer up
        ↓
Eventually rebuild the concepts using LangGraph
```

The priority is **deep understanding of agent architecture and reasoning patterns**, not completing one polished application.

---

## Current Learning Principle

Do not think primarily in terms of:

> "What feature should I add to the research agent?"

Instead ask:

> "What agent concept should I understand next, and what is the smallest change or experiment that lets me understand it?"

The research agent should only be modified when doing so helps demonstrate or investigate the concept currently being learned.

Avoid unnecessary refactoring, abstraction, UI work, production optimization, or feature expansion unless they directly contribute to understanding an agent concept.

---

## Current Stack

* Python
* Gemini API (`google-genai`)
* Tavily for real web search
* `python-dotenv`

---

## What I Already Understand

### LLM / API fundamentals

* Gemini API basics
* Basic RAG
* Function/tool calling
* Structured JSON responses

### Tool-calling agents

* An LLM generates a `function_call`
* Python detects and executes the requested function
* Tool results are returned to the model
* The model can request another tool
* The loop continues until the model produces a response without a tool call
* Multiple tools can be exposed to the same model
* Multiple tool calls can occur within a model response
* Tool execution can be centralized through `execute_function()`
* Tool exceptions can be converted into tool results so the model can potentially recover
* `max_steps` can prevent an infinite agent loop

### Search-enabled agents

* Gemini does not directly execute the Python `search()` function
* Gemini requests `search(query)` through a function call
* Python executes the function
* `search()` calls Tavily
* Tavily returns search results
* Python assigns local result IDs
* Search results are returned to Gemini as tool results
* Gemini can select which sources support its answer
* Python maps those IDs back to the original search results
* Python generates the final source links

### Important implementation understanding

* A model response can contain multiple parts
* Tool-call detection must inspect the entire response before deciding that the agent has finished
* Returning from inside the per-part loop can incorrectly terminate the agent
* `response.text` should not be assumed to contain normal text when the response contains function-call parts
* Structured output requires the appropriate Gemini response configuration rather than relying only on a prompt requesting JSON

---

## Current Agent

The agent currently has three tools:

* `calculator(expression)`
* `search(query)` → Tavily
* `save_notes(note)`

Current architecture:

```text
User
  ↓
Gemini
  ↓
Tool decision
  ↓
Python executes tool
  ↓
Tool result
  ↓
Gemini
  ↓
repeat
  ↓
Final answer
```

The agent currently uses `client.models.generate_content()` with a manually managed tool-calling loop.

The implementation should remain relatively transparent and simple while learning the underlying mechanisms.

---

## Current Search

Tavily is the real web-search backend.

Search results are normalized to:

```python
{
    "id": int,
    "title": str,
    "url": str,
    "content": str
}
```

Search results are tracked so the model can return `sources_used`.

Python then converts the selected source IDs into final source links.

A known deferred issue is **source-ID collisions across multiple searches in the same agent run**. This should be addressed when multi-search/state behavior becomes the relevant learning topic rather than as unrelated cleanup.

---

# Learning Roadmap

The roadmap is concept-driven rather than feature-driven.

## 1. Tool Calling and Execution

**Status: understood enough**

Understand:

* tool definitions
* function calls
* arguments
* dispatch
* execution
* tool results
* multiple tools
* multiple tool calls

Do not keep expanding this layer unnecessarily.

---

## 2. Agent Loops and Control Flow

**Status: understood enough**

Understand:

* model → tool → result → model loops
* termination conditions
* step limits
* multiple tool calls
* tool failures
* control flow owned by Python versus decisions made by the model

The current manual loop should remain available as the reference implementation.

---

## 3. State and Context

**Next major topic**

Understand what information an agent carries between steps.

Questions to investigate:

* What exactly does the model see on each iteration?
* What is conversation history?
* What is agent state?
* What information is generated by the model?
* What information is generated by tools?
* What information is maintained by Python?
* How are previous tool calls represented?
* How does information from an earlier tool call influence a later decision?
* What state should persist during one run?
* What state should not persist?

Implement small experiments around these questions rather than immediately introducing a framework.

---

## 4. Memory

After understanding state and context, investigate memory.

First understand the conceptual distinction between:

```text
Context
→ information currently provided to the model

State
→ information the agent tracks while executing

Memory
→ information retained beyond the current execution
```

Explore short-term and long-term memory conceptually before implementing sophisticated memory systems.

Do not jump directly to vector databases or complex memory frameworks.

---

## 5. Planning and Decomposition

Investigate how an agent handles tasks that require multiple actions.

Questions:

* Does the model explicitly create a plan?
* Can a task be decomposed into subtasks?
* Is planning performed once or repeatedly?
* What happens when a plan becomes invalid?
* Can the agent revise its plan?
* What is the difference between planning and simply choosing the next tool?

Implement small experiments rather than building a full planner.

---

## 6. Observation → Action → Feedback

Study the agent as an interaction loop:

```text
Observe
  ↓
Reason / decide
  ↓
Act
  ↓
Observe result
  ↓
Update context/state
  ↓
Act again
```

Understand how tool results act as environmental feedback and how that feedback changes subsequent decisions.

This should connect naturally to the ideas behind ReAct.

---

## 7. ReAct and Reasoning Patterns

Read relevant papers when the implementation provides enough context to understand them.

The goal is not to memorize papers but to map their ideas onto mechanisms already implemented manually.

For example:

```text
Paper concept
     ↓
Where does this appear in my implementation?
     ↓
What does my implementation simplify?
     ↓
What limitation does the paper address?
```

Use papers to deepen the implementation-based understanding rather than replacing implementation with paper reading.

---

## 8. Reliability and Failure Handling

Investigate how agents fail.

Examples:

* incorrect tool selection
* invalid tool arguments
* tool failures
* hallucinated tool results
* repeated tool calls
* infinite loops
* bad search queries
* stale or irrelevant information
* context growth
* malformed structured output
* incorrect final answers despite successful tool execution

Study both failure prevention and recovery.

---

## 9. Evaluation

Once the agent has enough behavior to evaluate, learn how to measure it.

Investigate:

* what makes an agent successful
* task success versus answer quality
* tool-selection accuracy
* unnecessary tool calls
* failure recovery
* latency
* cost
* robustness
* reproducibility

Build small evaluations rather than immediately adopting a large evaluation framework.

---

## 10. Multi-Agent Patterns

Only after understanding single-agent architecture well.

Study:

* when multiple agents are useful
* specialization
* delegation
* communication
* shared versus isolated state
* orchestration
* coordination failures
* whether multi-agent systems actually improve the task

Do not assume multi-agent automatically means better.

---

## 11. Agent Architecture and Trade-offs

Step back and compare different architectures.

Understand trade-offs between:

* simple loops
* tool-calling agents
* planners
* state machines
* graph-based agents
* reactive systems
* hierarchical agents
* multi-agent systems

The goal is to understand **why an architecture is chosen**, not just how to implement it.

---

## 12. LangGraph

Only after the underlying mechanisms are understood.

Rebuild selected concepts using LangGraph and map:

```text
Manual implementation
        ↕
LangGraph abstraction
```

The goal is to recognize what the framework is abstracting:

* state
* nodes
* transitions
* conditional routing
* tool execution
* persistence
* checkpoints
* control flow

LangGraph should feel like an abstraction over mechanisms already understood, not the source of that understanding.

---

# How to Learn

Assume basic Python, RAG, and LLM API knowledge.

For each new concept:

1. Understand the intuition.
2. Understand the underlying mechanism.
3. Implement the smallest useful version manually.
4. Run experiments.
5. Intentionally break it where useful.
6. Debug and explain the behavior.
7. Identify limitations and trade-offs.
8. Only then move to the next concept.

Prefer incremental changes to the existing project.

Do not add features merely because they are common in agent tutorials.

The project should remain small enough that the entire agent architecture can still be understood by reading the code.

---

# What Not To Optimize For

Do not prioritize:

* production readiness
* polished architecture
* UI
* deployment
* excessive abstraction
* framework usage
* adding many tools
* making the research agent "smart"
* building a feature-complete research assistant

These may become relevant later, but they are secondary to understanding the underlying concepts.

---

# Current Project Status

The first major layer—manual multi-tool agent execution—is working.

The agent can:

* call multiple tools
* execute tools through a dispatcher
* handle tool errors
* enforce a maximum step count
* perform real Tavily searches
* track search results
* produce structured final output
* select sources
* generate source links

The next learning focus is:

> **State and context: understanding exactly what information flows through the agent across multiple model/tool iterations.**

The immediate next implementation should be the smallest experiment that makes state/context visible and understandable.

Only after that should the project move toward memory, planning, reasoning patterns, reliability, evaluation, multi-agent systems, and eventually LangGraph.
