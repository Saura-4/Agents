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

### Important pacing rule

Do not spend excessive time implementing infrastructure after the underlying concept is already understood.

Once a mechanism has been understood sufficiently, use the appropriate library when that is the practical implementation and move to the next agent concept.

The project should not become primarily a retrieval-engineering project.

---

## Current Stack

* Python
* Gemini API (`google-genai`)
* Tavily for real web search
* `python-dotenv`
* `rank_bm25` for practical BM25 retrieval

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

### State and Context

* Context is the information made available to the model for a particular model call.
* `contents` is the model-facing context/history that is built across model/tool iterations.
* Agent state is information maintained by Python during agent execution and is not automatically visible to the model.
* Python state becomes model context only when the agent explicitly exposes it, such as through a tool result.
* `search_results` is run-scoped state because it is initialized inside `run_agent()`.
* `notes` is in-process persistent state because it exists outside `run_agent()` and survives across multiple runs while the Python process remains alive.
* A retrieval tool such as `retrieve_notes()` can expose Python-maintained state to the model through the normal tool-calling mechanism.
* State and context are distinct: state is information the agent has; context is information the model receives.
* Short-term memory can overlap heavily with conversation history, but memory and context are conceptually different: memory is retained information, while context is the subset currently supplied to a particular model call.
* Long-term memory can be retrieved selectively and injected into context; not all persisted memory needs to be present in every model call.

---

## Current Agent

The agent currently has tools for:

* `calculator(expression)`
* `search(query)` → Tavily
* `save_notes(note)`
* persistent memory writing and retrieval
* vector-based memory retrieval
* lexical/BM25 memory retrieval work

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

**Status: understood enough**

Understand:

* What context is for a particular model call
* How `contents` accumulates model and tool messages
* The distinction between model-visible context and Python-side state
* Run-scoped versus in-process persistent state
* How tools expose agent state to the model
* What information should and should not be placed into model context

---

## 4. Memory

**Status: foundational memory understood; vector retrieval implemented; BM25 understood; hybrid retrieval is next**

Understand the distinction between:

```text
Context
→ information currently provided to the model

State
→ information the agent tracks during execution

Memory
→ information intentionally retained beyond the current execution
  so it can be retrieved and used by future executions
```

### Memory concepts understood

* Long-term memory must persist beyond the current agent execution and survive process restarts.
* A persistent file is sufficient to demonstrate long-term memory; a database or vector database is not inherently required.
* Short-term memory concerns information retained during the current task or conversation.
* Conversation history can serve as short-term memory, but short-term memory and model context are conceptually distinct.
* Context is the model-facing information for a particular model call.
* Memory is a source of information that can be selected and injected into context.
* Python can maintain memory state, but information only becomes persistent long-term memory when it is stored beyond the process lifetime.
* The LLM can decide when information should be remembered and request a memory-writing tool; the Python memory layer performs the actual persistence.
* User-explicit memory requests can also cause the model to request a memory write.
* Memory storage and memory retrieval are separate problems.

### Memory implementation completed

The agent has demonstrated:

```text
Run 1
  ↓
LLM requests save_memory()
  ↓
Python writes memory.json
  ↓
process terminates

Run 2
  ↓
LLM requests retrieve_memories()
  ↓
Python reads memory.json
  ↓
memory result enters model context
  ↓
LLM uses the memory
```

The initial implementation deliberately retrieves all stored memories.

### Memory retrieval progression

The retrieval problem is being developed progressively:

```text
All memories
    ↓
metadata / lexical baselines
    ↓
vector retrieval
    ↓
hybrid retrieval
    ↓
reranking
```

Understand each retrieval mechanism independently before combining them.

Current progression:

1. Vector retrieval — implemented and understood
2. BM25 lexical retrieval — mechanism understood; practical library selected
3. Hybrid retrieval — **next**
4. Reranking — after hybrid retrieval

Query rewriting using an LLM may be investigated later as an optimization rather than assumed to be necessary.

Do not introduce a production memory framework before the underlying retrieval mechanisms are understood manually.

### Memory implementation pacing decision

The core retrieval concepts are now sufficiently understood that the project should not spend multiple additional sessions reproducing retrieval infrastructure.

The goal of hybrid retrieval is to understand:

* why lexical and semantic retrieval complement each other
* how their result sets differ
* why raw BM25 and vector scores should not simply be added
* how ranking fusion works
* how a hybrid retriever fits into the agent architecture

The implementation should therefore be kept minimal and understandable.

---

## Vector Retrieval

**Status: implemented and verified**

Vector retrieval was implemented manually over the existing persistent memory store rather than introducing Chroma or another vector database.

Current mechanism:

```text
Stored memory
    ↓
Gemini embedding model
    ↓
memory vector
    ↓
persistent embedding storage

Query
    ↓
Gemini query embedding
    ↓
cosine similarity against memory vectors
    ↓
sort by similarity
    ↓
similarity threshold
    ↓
top-k
    ↓
retrieved memories
```

The implementation uses Gemini embeddings with retrieval-oriented task types:

* `RETRIEVAL_DOCUMENT` for stored memories
* `RETRIEVAL_QUERY` for user queries

Memory embeddings are stored separately from `memory.json` in `memory_embeddings.json`.

The current implementation uses explicit Python cosine-similarity calculation rather than delegating vector search to a vector database.

### Vector retrieval design decisions

* `top_k` and `threshold` are Python-side retrieval configuration rather than Gemini-controlled tool arguments.
* The model-facing vector retrieval tool only needs the query.
* A separate `save_memory_vector` model-facing tool is not required because embedding/indexing is an internal implementation detail of the memory system.
* The memory store and vector representation are separate concerns.
* Vector database systems such as Chroma can abstract storage, indexing, embedding integration, and similarity retrieval, but those responsibilities are being implemented explicitly first for learning.

### Vector retrieval behavior observed

With 20 memories and threshold `0.0`, the query:

```text
What am I building?
```

returned:

```text
0.679  I am learning agent architecture progressively rather than trying to build a production-ready agent immediately.
0.661  I am building a research agent in Python using Gemini and Tavily.
0.652  I am learning how AI agents work, especially tool calling, agent loops, state, context, and memory.
```

The explicitly relevant memory about building a research agent ranked second rather than first. This demonstrated that semantic similarity does not necessarily equal task-specific relevance.

With a threshold of `0.75`, the same query returned no memories because the highest observed similarity was approximately `0.679`.

This demonstrated that:

* a relevant memory can exist but fail the similarity threshold
* similarity scores should not be interpreted as universal relevance probabilities
* a fixed threshold depends on the embedding model and retrieval data
* vector retrieval can produce false negatives
* vector retrieval can rank semantically related but less useful memories above the most directly useful memory

### Vector retrieval failure observed

When vector retrieval returned an empty list, the agent sometimes repeatedly called retrieval tools and eventually reached the configured `max_steps`.

This demonstrated that:

```text
empty retrieval result
```

does not automatically tell the model whether:

* no memory exists
* memories exist but none crossed the threshold
* retrieval failed
* the threshold was too strict

The current agent therefore has a separate reliability/control-flow issue around handling empty retrieval results. This is not being fixed yet because retrieval reliability is a later learning topic.

---

## BM25 / Lexical Retrieval

**Status: core mechanism understood; library implementation selected; eager indexing architecture still to implement**

BM25 was studied manually before moving to the library implementation.

The following concepts are understood:

* Tokenization converts text into terms used by lexical retrieval.
* Term frequency measures how often a query term appears in one memory.
* Document frequency measures how many distinct memories contain a term.
* IDF gives greater weight to terms that occur in fewer documents.
* BM25 applies TF saturation rather than treating repeated occurrences as linearly valuable.
* BM25 incorporates document-length normalization.
* A memory's BM25 score for a query is the sum of the contributions of the query's individual terms.
* BM25 retrieval scores all candidate memories, ranks them, and returns the highest-scoring memories.

The manual implementation established the conceptual mechanism without needing to become the permanent retrieval implementation.

### Practical implementation

`rank_bm25` is the selected library for the practical BM25 implementation.

The intended flow is:

```text
Stored memories
    ↓
tokenized corpus
    ↓
BM25Okapi
    ↓
query tokens
    ↓
BM25 scores
    ↓
ranked memories
```

### Important architecture decision

BM25 should **not** be lazily constructed inside every retrieval call.

The intended architecture is eager indexing:

```text
save_memory()
    ↓
persist memory
    ↓
update embedding/vector representation
    ↓
update Chroma/vector index where applicable
    ↓
update BM25 index
```

Then retrieval uses the already-maintained indexes:

```text
query
  ↓
BM25 retrieval
  +
vector retrieval
```

However, the final hybrid score itself cannot be calculated when a memory is inserted because the hybrid score depends on the future query.

The distinction is:

```text
Insertion time:
    build/update retrieval indexes

Query time:
    calculate query-dependent retrieval scores
    combine rankings
    produce hybrid ranking
```

BM25 corpus statistics also depend on the collection as a whole, so adding a memory can change BM25 statistics such as document frequency and total document count. The index lifecycle therefore needs to be handled explicitly rather than rebuilding it invisibly on every query.

---

## 5. Hybrid Retrieval

**Status: next implementation topic**

Hybrid retrieval should combine:

```text
Lexical retrieval
      +
Semantic retrieval
      ↓
Hybrid ranking
```

The purpose is not simply to make retrieval "better", but to understand the complementary failure modes.

Lexical retrieval is strong when exact terms matter:

```text
Tavily
Chroma
specific names
identifiers
technical terminology
```

Semantic retrieval is strong when the query and memory express similar meaning using different words.

The first hybrid implementation should keep both result sets observable.

Do not initially combine raw BM25 and vector similarity scores directly because the two scoring systems have different scales and meanings.

The preferred initial fusion mechanism is rank-based fusion, such as Reciprocal Rank Fusion:

```text
RRF score = 1 / (k + rank)
```

The goal is to understand:

* how each retriever produces its ranking
* how a memory appearing in both rankings is rewarded
* how a memory appearing only near the top of one ranking can still survive
* why rank fusion is useful when score scales are incompatible

The implementation should remain minimal.

---

## 6. Planning and Decomposition

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

## 7. Observation → Action → Feedback

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

## 8. ReAct and Reasoning Patterns

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

## 9. Reliability and Failure Handling

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

## 10. Evaluation

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

## 11. Multi-Agent Patterns

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

## 12. Agent Architecture and Trade-offs

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

## 13. LangGraph

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
4. Run experiments where they provide learning value.
5. Intentionally break it where useful.
6. Debug and explain the behavior.
7. Identify limitations and trade-offs.
8. Use a library when the underlying mechanism is already understood and further manual reproduction would not add meaningful learning.
9. Move to the next concept rather than over-polishing the current one.

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
* spending multiple sessions reproducing standard retrieval algorithms after their mechanisms are understood

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

The state/context layer is now understood well enough to move forward.

The agent has demonstrated:

* context accumulating across model/tool iterations
* Python-maintained agent state
* run-scoped state versus in-process persistent state
* explicit exposure of Python state through a retrieval tool
* the distinction between state and model-visible context

The foundational memory layer is implemented and verified.

The agent can:

* persist long-term memories to `memory.json`
* retrieve persisted memories after a process restart
* expose retrieved memories to the model through a tool response
* store memory with associated metadata as an experimental retrieval mechanism
* retrieve memories by category as a metadata-based baseline

Vector retrieval is implemented and verified manually using Gemini embeddings, persistent memory embeddings, cosine similarity, thresholding, and top-k ranking.

BM25 has been understood at the mechanism level, including TF, DF, IDF, length normalization, per-term scoring, full-query scoring, and ranking.

The practical BM25 implementation will use `rank_bm25` rather than continuing to manually reproduce the algorithm.

The current learning focus is **hybrid retrieval**, but memory retrieval should now be treated as a bounded learning topic rather than the central focus of the project.

The immediate next implementation should be:

```text
Eager BM25 indexing
      +
Existing vector/Chroma retrieval
      ↓
Minimal hybrid retrieval
      ↓
Rank fusion / RRF
      ↓
Move on from memory
```

The hybrid implementation should not introduce lazy index construction.

At memory insertion time, retrieval indexes should be updated eagerly. The query-dependent hybrid score must still be calculated at retrieval time because it depends on the query.

After the minimum viable hybrid retrieval mechanism is understood, move to reranking only if it provides a clear learning objective. Do not spend multiple additional sessions polishing retrieval infrastructure.

After the memory/retrieval layer is sufficiently understood, return to the broader agent roadmap:

```text
Hybrid retrieval
      ↓
Reranking
      ↓
Planning / decomposition
      ↓
Observation → action → feedback
      ↓
ReAct / reasoning patterns
      ↓
Reliability and failure handling
      ↓
Evaluation
      ↓
Multi-agent patterns
      ↓
Architecture trade-offs
      ↓
LangGraph
```

The project should prioritize **breadth across core agent concepts while maintaining sufficient depth to understand each mechanism**, rather than spending disproportionate time perfecting one subsystem.