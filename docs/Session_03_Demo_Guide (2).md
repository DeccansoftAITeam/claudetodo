# Session 5 Demo Guide: Agentic Thinking

### Step 1 — Start a named session

```bash
cd claudetodo
claude -n "s5-category"
```

### Step 2 — Enter Plan mode

Press `**Shift+Tab**` until the mode indicator reads `plan`.

Narration: "We're in Plan mode. Claude will write the plan out before editing anything. You'll read it, then I'll tell Claude to proceed."

### Step 3 — Give Claude the goal (one prompt, no steps)

```
Add a category system to ClaudeTodo. Each todo belongs to a category.
Support filtering by category. Plan first. Follow CLAUDE.md.
Done means: all tests pass AND the filter works in the browser.
```

Let Claude write the plan. Read it aloud to the audience.

### Step 4 — Approve or correct

If the plan is good: "Proceed."

If something needs to change — e.g., you want the category to be a fixed dropdown, not free text — correct it NOW, before any file is touched:

```
Good plan, but change free-text categories to a fixed dropdown: Work, Personal, Other.
Update the plan accordingly, then proceed.
```

Narration: "Correcting the plan is cheap. Correcting the code is expensive. We always approve the plan first."

Exit Plan mode (`Shift+Tab`) and let Claude execute.



### Step 5 — The intervention demo

Say to the audience: "What if I want to change the design mid-flight?"

```
Change the category field from free-text to a dropdown with fixed values:
Work, Personal, Other. Update backend validation and the frontend input.
```

Watch Claude:

- Read the current state (models.py, main.py, App.jsx).
- Make the targeted changes — not a rewrite.
- Test the change.

Narration: "Claude didn't start from scratch. It knew the current implementation and made the minimal delta."

### Step 6 — Audit the run

Scroll through the tool-call log. Narrate out loud:

- Total Read calls.
- Total Edit calls.
- Total Bash calls.
- Files touched — none of which we named in the prompt.

Narration: "This is what one agentic prompt did. You wrote one sentence."

---
