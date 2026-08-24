# Session Log Format

## Purpose

`session_log.md` is a compact chronological record of what happened
across project sessions.

It is historical evidence, not the source of truth for current project
state. Current project state belongs in `project_context.md`.

Keep each session concise. Prefer roughly 50–70 lines or less.

---

## Session log entry format

Each entry uses this exact structure. Do not omit sections; write `none`
where nothing applies rather than dropping the header.

## Session N: <short topic title>

**Date:** YYYY-MM-DD

**Scope in:** what this session actually covered — specific, not vague.

**Scope deferred:** what was explicitly pushed to a later session, and why
if not obvious (e.g. "held back to avoid shallow coverage").

**Concepts covered, with confirmed understanding (comprehension-checked,
correct answer stated first):**
- Only include a concept here if it was actually quizzed/tested in this
  session AND the person arrived at the correct understanding by the end.
- State the CORRECT fact as the main sentence. Never lead with a wrong
  guess — the true fact must be readable in isolation with zero risk of
  being taken as fact if only the first clause is read.
- If a concept was only explained but never checked, it does NOT belong in
  this section — put it under "Concepts explained (not yet checked)"
  instead, so mastery isn't overstated.

**Concepts explained (not yet checked):**
- Concepts explained during the session that were not explicitly tested
  for understanding.
- Do not imply mastery.

**Initial misunderstandings (resolved — for pattern-tracking only):**
- Only for genuine wrong-then-corrected moments.
- Format: "X: initially assumed ___; corrected to ___."
- This section exists to identify recurring learning patterns across
  sessions. It does NOT mean the concept remains unresolved.

**Files touched:**
- filename — one line describing what changed, nothing more.

**Other notes (environment/workflow facts, not project state):**
- Tooling, setup issues, dependency changes, API behavior, or other
  non-conceptual events.
- Keep neutral and factual.

**Working-style event (only if it produced a standing preference):**
- Record only events that changed a standing preference or rule.
- Point to `project_context.md` → "How I learn" as the source of truth
  instead of duplicating the preference here.
- Write `none` when there was no such event.

**Next session scope:**
- State the next concrete topic or task.
- It must be specific enough that there is exactly one reasonable
  starting point.

---

## Rules

### 1. Keep the log historical

Do not rewrite previous sessions because the current project state changed.

If something changes later, record the change in the later session.

### 2. Do not duplicate project context

Do not record the complete architecture, roadmap, preferences, or current
state in every session.

`project_context.md` is responsible for those.

### 3. Do not record conversation transcripts

Record outcomes, discoveries, decisions, and verified understanding.

Do not record the conversation itself.

### 4. Do not overstate understanding

Explained ≠ understood.

Tested and correctly demonstrated ≠ merely explained.

### 5. Record meaningful mistakes

Only record misunderstandings that reveal something useful about the
learning process.

Do not record trivial typos or temporary coding mistakes unless they
revealed an important conceptual issue.

### 6. Record important failed approaches

A failed approach belongs in the log when it produced a useful technical
lesson or changed a project decision.

### 7. Every bullet must stand alone

A reader should be able to understand a bullet without reading the
previous bullet.

Never write fragments such as:

- "This worked."
- "That was the problem."
- "We fixed it."

Instead state what "this", "that", or "it" refers to.

### 8. Do not turn unresolved issues into facts

If something is uncertain, explicitly mark it as uncertain.

Do not convert a hypothesis into a confirmed cause.

---

## Rule for anyone reading only ONE line of this log out of context

Every bullet must be self-contained and correct if read in isolation.

Imagine a new chat only skims one line before proceeding.

Would that one line alone lead to a false belief, incorrect assumption,
or wrong action?

If yes, rewrite it.