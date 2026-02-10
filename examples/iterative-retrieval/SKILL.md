---
name: iterative-retrieval
description: Dispatch subagents with automatic refinement loop until sufficient context is gathered
---

# Iterative Subagent Retrieval Protocol

When dispatching a subagent to retrieve information from a source (transcripts, documents, codebases, external data), follow this protocol:

## Phase 1: Initial Dispatch
1.  Define the **PRIMARY OBJECTIVE** - what decision or action does this information support?
2.  Define **INITIAL QUERIES** - specific items to retrieve
3.  Dispatch subagent with both the queries AND the objective context
4.  Store the returned agent ID

---

## Phase 2: Sufficiency Evaluation
Upon receiving the subagent's summary, perform a critical evaluation:

#### Ask yourself:
- Does this summary contain gaps that the objective requires filling?
- Did the subagent mention adjacent information I didn't ask for but now realize I need?
- Are there ambiguities in what was returned that require clarification from the source?
- Would I be confident proceeding with **ONLY** this information?

#### Decision:
- If **SUFFICIENT** → proceed with task, note agent ID for potential future resumption
- If **INSUFFICIENT** → continue to Phase 3

---

## Phase 3: Refinement Request
Resume the request using its agent ID with:
1.  Acknowledge what was useful from the initial return
2.  Specify **EXACTLY** what additional context is needed and **WHY**
3.  Ask if there's related information the subagent noticed but didn't include

---

## Phase 4: Loop
Repeat Phase 2-3 until:
- Sufficiency is achieved, OR
- Maximum 3 refinement cycles reached (prevent infinite loops), OR
- Subagent confirms source is exhausted

---

## Output Format
When reporting to user or continuing work, note:
- Total refinement cycles used
- What additional context was gathered beyond initial request
- Agent ID for future resumption if needed