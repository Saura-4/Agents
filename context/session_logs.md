
## Session 1: Building the Multi-Tool Agent

**Date:** 2026-08-24

**Scope in:** Understanding and implementing a multi-tool Gemini agent with
calculator, search, and save_notes tools; refactoring tool execution;
handling multiple tool calls; debugging tool errors; and investigating
Gemini Google Search integration.

**Scope deferred:** Real external web search implementation and the larger
research-agent workflow were deferred until the current tool architecture
was stable.

**Concepts covered, with confirmed understanding (comprehension-checked,
correct answer stated first):**
- A tool-calling agent repeatedly sends model context to the LLM, executes
  requested tools in Python, returns tool results to the LLM, and continues
  until the model produces a response without a tool call.
- `execute_function()` can centralize dispatching multiple tools instead of
  putting separate execution logic directly inside the agent loop.
- A model response can contain multiple parts, so the agent should inspect
  every part for function calls rather than assuming only the first part can
  contain a tool call.
- `has_tool_call` must represent whether the entire model response requested
  a tool; the agent should return the final answer only after all response
  parts have been inspected.
- Returning `response.text` from inside a loop when a non-tool part is found
  can incorrectly terminate the agent before all tool calls are processed.
- A maximum step limit prevents an agent from continuing indefinitely when
  the model repeatedly requests tools.
- Tool exceptions can be caught and returned to the model as tool results,
  allowing the model to explain or recover from the failure instead of
  crashing the whole application.

**Concepts explained (not yet checked):**
- The distinction between manually implemented function calling and
  provider-managed automatic function calling.
- The architecture of a research agent using a real external search API.
- The trade-off between Gemini's built-in Google Search and an external
  search provider.
- Tool abstraction allows the implementation behind `search(query)` to be
  replaced without changing the agent's core loop.

**Initial misunderstandings (resolved — for pattern-tracking only):**
- Tool-call detection: initially considered returning from inside the
  per-part loop when a part had no function call; corrected to inspect the
  entire response first and return only when no tool call occurred anywhere.
- Google Search failure: initially considered whether the existing custom
  tools were responsible; isolated testing showed calculator and
  calculator + save_notes worked, while the problem appeared after adding
  Google Search.

**Files touched:**
- `main.py` — implemented and tested the multi-tool agent loop and tool
  dispatcher.
- `test.py` — used for isolated Gemini and tool configuration tests.
- `session_log_format.md` — defined the compact session logging format.

**Other notes (environment/workflow facts, not project state):**
- `google-genai` version 2.19.0 is installed in the virtual environment.
- Direct `generate_content()` without Google Search successfully called the
  calculator tool.
- Direct `generate_content()` with calculator + save_notes also worked.
- Gemini's built-in Google Search path produced `429 RESOURCE_EXHAUSTED`.
- A newly created API key/account produced the same Google Search-related
  429 behavior.
- Normal Gemini inference continued to work with the existing setup.

**Working-style event (only if it produced a standing preference):**
- The session established that project context should distinguish stable
  project state from chronological session history; the actual standing
  preference is maintained in `project_context.md` → "How I learn".

**Next session scope:**
- Implement a real external `search(query)` tool while preserving the
  existing manual tool-calling architecture.


  ## Session 2: Implementing real web search and source citations

**Date:** 2026-08-24

**Scope in:** Replaced the fake search tool with Tavily web search, implemented source tracking and citation generation, debugged structured Gemini output, and built a complete mental model of the search/tool-calling/citation flow.

**Scope deferred:** Handling source-ID collisions across multiple searches in the same agent run; deferred until multi-search behavior is developed.

**Concepts covered, with confirmed understanding (comprehension-checked, correct answer stated first):**
- The agent's `search` tool is a Python function that calls Tavily; Gemini does not directly execute the Python function or call Tavily.
- Gemini generates a `function_call` containing the tool name and arguments, and the Python agent detects the function call and executes the corresponding Python function.
- Tavily performs the actual web search and returns search results containing titles, URLs, and content.
- The Python code creates the numeric `id` field for each search result; the IDs are not generated by Tavily.
- Gemini receives the search results through a function-response message after Python executes the search tool.
- Gemini generates the final structured JSON containing `answer` and `sources_used` because the system prompt requests those fields and `response_schema` enforces their structure.
- Python reads `answer` and `sources_used` from Gemini's JSON response and maps the selected source IDs back to the original Tavily results.
- Python, rather than Gemini, generates the final Markdown source links using the selected result's title and URL.
- The citation pipeline was successfully tested: Gemini selected a single authoritative AWS result from five Tavily search results, and Python converted that source ID into the final citation.

**Concepts explained (not yet checked):**
- The complete end-to-end flow of a search-enabled agent: user request → Gemini tool decision → Python function execution → Tavily search → Python source IDs → tool response to Gemini → Gemini source selection → Python citation generation.
- The distinction between data generated by Gemini, data returned by Tavily, and metadata/citations generated by Python.
- Why `response.text` can produce a warning when a Gemini response contains non-text parts such as `function_call`.

**Initial misunderstandings (resolved — for pattern-tracking only):**
- Source metadata ownership: initially uncertain about where `answer`, `sources_used`, and search-result IDs came from; clarified that Gemini generates `answer` and `sources_used`, Tavily provides search-result data, and Python creates result IDs and final Markdown citations.
- Citation generation: initially considered whether Gemini should generate citations directly; clarified that Python-generated citations are preferable because URLs come directly from retrieved search results and Gemini only selects which source IDs support the answer.
- Structured output: initially assumed `json.loads(response.text)` would work automatically; corrected to explicitly configure `response_mime_type="application/json"` and `response_schema`.

**Files touched:**
- `main.py` — replaced the fake search implementation with Tavily search, added structured Gemini output, source tracking, and Python-generated citations.

**Other notes (environment/workflow facts, not project state):**
- Tavily was integrated through `TavilyClient` using `TAVILY_API_KEY`.
- Gemini successfully performed tool calling with Tavily search and returned structured JSON after the response schema was added.
- A temporary `JSONDecodeError` occurred because Gemini was not initially configured to return JSON despite the prompt requesting JSON.
- The Gemini SDK emitted a warning when `response.text` was accessed on responses containing `function_call` parts; the warning did not prevent the tool-calling flow from working.

**Working-style event (only if it produced a standing preference):**
- none

**Next session scope:**
- Fix source-ID collisions when the agent performs multiple web searches in a single `run_agent()` execution.

## Session 3: State and Context

**Date:** 2026-08-25

**Scope in:** Understanding the distinction between model context, agent state, and persistent in-process state; tracing how model responses and tool results are added to `contents`; experimenting with Python state visibility; implementing `retrieve_notes()` to expose stored state to the model.

**Scope deferred:** Memory architecture and persistent storage beyond the current Python process; deferred until state/context boundaries were understood first.

**Concepts covered, with confirmed understanding (comprehension-checked, correct answer stated first):**
- Context is the information made available to the model for a particular model call, including user input, previous model messages, and tool results.
- Agent state is information maintained by the Python agent during execution that is not automatically visible to the model.
- `contents` represents the model-facing context/history that is progressively built across model/tool iterations.
- A model's previous response and the corresponding tool response are appended to `contents`, allowing later model calls to use information from earlier iterations.
- Python state does not automatically become model context; state must be explicitly exposed to the model, such as through a tool result.
- `search_results` is run-scoped agent state because it is initialized inside `run_agent()` and is discarded when that execution ends.
- `notes` is persistent state only within the lifetime of the running Python process because it is defined outside `run_agent()`; restarting the process resets the list.
- The `save_notes()` tool modifies Python state, while `retrieve_notes()` exposes that state to Gemini through a tool response.
- State and context are related but distinct: state is information the agent has, while context is information the model receives.
- The model can only use Python-maintained state when the agent provides an explicit mechanism for retrieving or injecting that state into model context.

**Concepts explained (not yet checked):**
- The distinction between state that survives an agent run and true long-term memory.
- The broader architectural meaning of memory and why a Python global list is not yet a complete memory system.

**Initial misunderstandings (resolved — for pattern-tracking only):**
- State visibility: initially expected a previously saved note to automatically be available to Gemini; corrected to understand that Python state is not automatically visible to the model and requires an explicit retrieval mechanism.
- Memory classification: initially treated persistent `notes` as memory; refined to distinguish in-process persistent state from a proper memory mechanism.

**Files touched:**
- `main.py` — added the `retrieve_notes()` function and corresponding Gemini tool declaration/dispatch, and added temporary context/state inspection during experiments.

**Other notes (environment/workflow facts, not project state):**
- Context inspection showed Gemini's function-call response is represented as structured `Content`/`Part` objects rather than ordinary text.
- The Gemini SDK emitted a warning when `response.text` was accessed on a response containing a function-call part; the full structured response remained available through `candidates[0].content.parts`.
- The multi-search source-ID collision remains unresolved and is intentionally deferred until multi-search/state behavior becomes the relevant learning focus.

**Working-style event (only if it produced a standing preference):**
- The teaching style was adjusted to use a more technically mature level of explanation, with less elementary scaffolding and more direct architectural reasoning; the standing preference is maintained in `project_context.md` → "How I learn".

**Next session scope:**
- Learn the conceptual distinction between agent state and memory, then implement the smallest experiment that demonstrates information persisting beyond the current agent execution.

## Session 5: Memory and Retrieval Foundations

**Date:** 2026-08-25

**Scope in:** Understanding short-term versus long-term memory, persistence across process boundaries, memory retrieval, context construction, naive memory retrieval, metadata filtering, lexical retrieval, BM25, and the progression toward vector, hybrid, and reranked memory retrieval. Implemented and verified persistent long-term memory using a JSON file.

**Scope deferred:** Vector retrieval, hybrid retrieval, and reranking were explicitly deferred to the next session so each retrieval stage can be understood and implemented incrementally.

**Concepts covered, with confirmed understanding (comprehension-checked, correct answer stated first):**
- Long-term memory is information intentionally persisted beyond the lifetime of the current agent execution so that a future execution can retrieve and use it.
- Short-term memory is information retained during the current interaction or task; conversation history can serve as its implementation, but short-term memory and model context are conceptually distinct.
- Model context is the information supplied to the model for a particular model call; memory is a source of information that can be selected and injected into context.
- Long-term memory does not have to use a database; a persistent JSON file can demonstrate the required persistence property.
- Retrieving all stored memories and returning them to the model is a valid naive memory-retrieval implementation, but it does not scale because irrelevant memories consume context.
- Relevant memories can be selected using mechanisms such as recency, metadata filtering, lexical search, vector search, or hybrid retrieval.
- BM25 is a principled lexical retrieval method that ranks memories based on query-term relevance rather than simple substring matching.
- Memory retrieval and memory storage are separate problems: storage determines how memories persist, while retrieval determines which persisted memories are brought back for a current task.
- In a tool-calling architecture, Gemini generates a memory function call and its arguments, Python executes the memory operation, and the resulting function response is returned to Gemini as model-visible context.
- Function schema `required` specifies which arguments Gemini must provide when generating a function call; it does not specify what the Python function must return.
- A memory retrieval tool with a required `category` argument requires Gemini to provide that category in the function call, while application-level validation is still responsible for determining whether the category itself is valid.

**Concepts explained (not yet checked):**
- LLM-generated memory-query rewriting as a retrieval optimization.
- The trade-off between query rewriting quality and its additional latency, cost, and failure modes.
- The conceptual progression from naive retrieval → recency/metadata → BM25 → vector retrieval → hybrid retrieval → reranking.

**Initial misunderstandings (resolved — for pattern-tracking only):**
- Short-term memory was initially treated as simply equivalent to context; refined to distinguish retained information from the subset actually supplied to a particular model call.
- Long-term memory was initially associated specifically with databases; corrected to treat persistence beyond the process lifetime as the important property, with files and databases both being possible implementations.
- Relevance retrieval was initially considered as LLM inspection of all memories; clarified that LLM filtering can select relevant memories but does not solve the scalability problem of sending all memories into context.
- Function-schema `required` was initially uncertain; clarified that it specifies mandatory arguments in the model-generated function call.

**Files touched:**
- `tools.py` — refactored memory functionality and experimented with persistent memory and metadata-based retrieval.
- `agent.py` — refactored agent orchestration and integrated the tool collection.
- `executor.py` — maintained centralized tool dispatch for the refactored agent.
- `main.py` — retained the simple entry point calling `run_agent()`.
- `memory.json` — verified persistent long-term memory across Python process restarts.

**Other notes (environment/workflow facts, not project state):**
- Persistent memory was verified by saving a memory, terminating the Python process, restarting the process, and successfully retrieving the saved memory.
- Naive retrieval was verified by retrieving all stored memories and allowing Gemini to use the returned tool result.
- The uploaded project files were refactored into separate agent, executor, tools, clients, and entry-point modules.

**Working-style event (only if it produced a standing preference):**
- The learning level was explicitly calibrated to final-year CS understanding, with less elementary explanation and greater emphasis on architecture, mechanisms, trade-offs, and implementation reasoning; the standing preference is maintained in `project_context.md` → "How I learn".

**Next session scope:**
- Implement vector-based memory retrieval over the persistent memory store, understand embedding-based similarity retrieval, and compare its behavior with lexical retrieval before implementing hybrid retrieval.