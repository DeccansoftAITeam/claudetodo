# Session 3 Teaching Guide — Agentic Thinking: Plan Mode, Checkpoints & Memory

Trainer crib sheet + participant lab. ~2 hours. Keep a terminal, the browser (app at
`localhost:5173`), and the Claude Code window visible together.

**Feature built this session:** a category system (fixed dropdown: Work / Personal / Other)
with filtering — driven by ONE goal-level prompt.

**Big idea of the session:** stop treating Claude as autocomplete. The workflow is:
*goal → plan → review the plan → execute → verify → (rewind if wrong)*. Correcting a plan
costs one sentence; correcting code costs a rework.

---

## Pre-session checklist (trainer)

- [ ] `git status` clean on `main`; both servers start (`uvicorn main:app --reload` in
  `backend/`, `npm run dev` in `frontend/`).
- [ ] App works in browser: create / complete / delete a todo.
- [ ] Delete stray test todos so the demo data is clean (or note that `todos.db` is disposable).
- [ ] This file open on a second screen; all prompts below are copy-paste ready.
- [ ] Claude Code updated (`claude update`) — checkpoints/rewind and memory behave as described
  on current versions.
- [ ] Browser tabs pre-opened for the "under the hood" segment:
  - `github.com/Piebald-AI/claude-code-system-prompts` (system-prompts folder)
  - `github.com/openai/codex` → `codex-rs/core/prompt.md` (Codex CLI's system prompt)

---

## Section 0 — Recap, Under the Hood & the Agentic Loop (0:00–0:20, slides + browser)

Four beats:

1. **Recap:** Sessions 1–2 built the app and its `CLAUDE.md` files. Those files load
   automatically every session — that's why Claude already "knows" the API contract.

2. **Under the hood — what Claude already knows before your first prompt** (~8 min):

   Open `github.com/Piebald-AI/claude-code-system-prompts` — a community project that extracts
   every prompt string from each Claude Code release within minutes of it shipping (500+
   strings as of v2.1.212). Scroll the `system-prompts/` folder and point out:

   - There is **no single system prompt** — it's assembled per session from fragments:
     the core behavioral prompt, descriptions for ~27 built-in tools, sub-agent prompts
     (Explore / Plan / general-purpose — "remember these names, they're session 6"),
     compaction & summarization prompts, and the system reminders that get injected
     mid-conversation.
   - Open ONE tool description (e.g. Edit or Bash) and skim it: "every rule you've seen Claude
     follow — read before edit, prefer dedicated tools — is written down here. It's prompts
     all the way down."
   - **Contrast: Codex.** Open `openai/codex` → `codex-rs/core/prompt.md`. One comparatively
     short file. Different philosophy: Claude Code encodes behavior in an elaborate prompt
     architecture; Codex keeps the prompt lean and relies more on the model. Neither is
     "right" — but knowing what's already in the context changes how you write instructions.

   **The payoff — say this slowly:** your `CLAUDE.md` is injected into this same context,
   flagged as *overriding* default behavior. That's why it works — and why it must be
   **minimal and scoped to what's necessary**. Your instructions land on top of tens of
   thousands of tokens of system prompt and compete with them (and with the actual task) for
   attention. Every line that doesn't earn its place dilutes the lines that do.

   Rules of thumb for the room:
   - Include only what Claude **cannot derive from the code**: run commands, non-obvious
     constraints, the API contract, "never do X" rules.
   - Don't restate what a glance at the repo reveals; don't paste style guides; don't write
     essays.
   - *Live audit (2 min):* open this repo's root `CLAUDE.md` and ask the room: "which lines
     earn their place?" (Ours is deliberately tight — layout, contract, seam rules — use it
     as the positive example.)

3. **The agentic loop:** every good Claude Code interaction is *gather context → plan → act →
   verify*. Today we make each step explicit and controllable.

4. **Permission modes** — cycle `Shift+Tab` live so the room sees the indicator change:

| Mode | What runs without asking | When to use |
| --- | --- | --- |
| `default` (Manual) | Reads only — every edit/command asks | Sensitive work, learning the tool |
| `acceptEdits` | Reads + file edits + basic filesystem commands | Iterating on code you're watching |
| `plan` | Reads only — Claude may **not** change anything; it produces a plan for approval | Any non-trivial feature. Today's mode. |

Mention (don't demo): `auto` and `bypassPermissions` exist for long autonomous runs and
sandboxed CI — powerful, out of scope today.

> **Narration:** "Plan mode is a contract: Claude can look but not touch. It must show you the
> approach first. You approve the approach, not each keystroke."

---

## Section 1 — Demo: Plan Mode Feature Build (0:20–0:50)

### Step 1 — Start fresh

```bash
cd claudetodo
claude
```

Press `Shift+Tab` until the mode indicator reads **plan**.

### Step 2 — One goal-level prompt (paste exactly)

```
Add a category system to ClaudeTodo. Each todo belongs to a category.
Support filtering by category in the UI. Follow CLAUDE.md.
Done means: the create/complete/delete/filter flow works in the browser,
and GET /api/todos returns a category for every todo.
```

> **Narration:** "Notice what I did NOT say: which files to touch, what the schema change is,
> how the frontend state works. That's Claude's job. My job is the goal and the definition of
> done."

### Step 3 — Read the plan ALOUD

Walk the room through the plan Claude produces. Point out what a good plan contains:

- The DB schema change (new `category` column in `todos.db` — including how existing rows are
  handled).
- Both sides of the seam: backend validation AND frontend UI (root `CLAUDE.md` says the API
  contract is the boundary — change both sides together).
- A verification step at the end.

### Step 4 — Correct the plan BEFORE approving (the key teaching beat)

The plan will almost certainly propose free-text categories. Correct it now:

```
Good plan, but categories must be a fixed set, not free text: Work, Personal, Other.
Backend rejects anything else; frontend uses a dropdown. Update the plan, then proceed.
```

> **Narration:** "One sentence just changed the design. If I'd caught this after execution,
> it would have been edits across three files, a schema migration, and re-testing. **Correcting
> the plan is cheap. Correcting the code is expensive.** This is the single most important
> habit in this course."

Approve the revised plan (Claude will ask to exit plan mode; accept). Watch it execute.

### Step 5 — Verify like you mean it

When Claude reports done, don't take its word:

```bash
curl http://localhost:8000/api/todos
```

Then in the browser: create a todo in each category, filter by each, delete one, reload.

> **Narration:** "Claude said done. We check. Every session in this course ends with this
> ritual — later, when sub-agents report back to us, this habit is what keeps us honest."

---

## Section 2 — Demo: Mid-Flight Intervention (0:50–1:00)

Say to the room: "What if I want a change *after* execution — without starting over?"

```
Add a category filter chip showing the count of todos in each category,
e.g. Work (3). Update only what's needed.
```

Watch Claude:
- Read the current state (`main.py`, `App.jsx`) — it does not guess.
- Make the targeted delta — not a rewrite.

> **Narration:** "Claude didn't start from scratch. It read the current implementation and made
> the minimal change. Agentic doesn't mean fire-and-forget — you can steer at any point."

---

## Section 3 — Demo: Audit the Run (1:00–1:05, keep it brisk)

Scroll back through the session's tool-call log. Count out loud:

- How many **Read** calls (context gathering).
- How many **Edit/Write** calls (action).
- How many **Bash** calls (verification).
- Files touched — **none of which we named** in the prompt.

Then show the cost of it all:

```
/context
```

> **Narration:** "One sentence from me became this many operations. And look at the context
> meter — everything we do consumes context. That's why later sessions teach delegation:
> keeping heavy work out of this window."

Commit the work:

```
Commit the category feature with a descriptive message.
```

---

## Section 4 — Demo: Checkpoints & /rewind (1:05–1:20)

### Set up the mistake

Switch to `acceptEdits` mode (`Shift+Tab`) and deliberately ask for something bad:

```
Rewrite App.jsx to put all styling inline on every element and remove the CSS file.
```

Let it finish. Show the browser — it may even still work, but the code is now worse. Then:

### Rewind it

Press **Esc Esc** (with an empty prompt box) — or type `/rewind`. Walk the room through the
three restore options:

| Option | What it does |
| --- | --- |
| Restore code and conversation | Full undo — files AND chat return to that point |
| Restore conversation only | Keep the files, rewind the chat |
| Restore code only | Revert the files, keep the conversation (Claude remembers *why*) |

Pick **Restore code and conversation** to the checkpoint before the bad prompt. Show
`git status` / the browser: the damage is gone.

### The fine print (say this explicitly — it prevents real-world disasters)

- A checkpoint is captured automatically **before each prompt**; the last ~100 are kept per
  session, and they survive session resume.
- Checkpoints track **Claude's file edits only**. They do **NOT** undo:
  - **Bash side effects** — `rm`, `mv`, database writes…
  - **Our `todos.db`!** Perfect concrete example: rewind restores `main.py`, but rows Claude
    inserted into SQLite stay. *Demonstrate this if time allows.*
  - Files you edited yourself in your editor.
- Checkpoints are not a git replacement — they're an experiment-undo. Git is still the real
  safety net (which is why we commit at every milestone).

> **Narration:** "This changes how bold you can be. 'Try a completely different approach' is
> now a free move — if it's worse, Esc-Esc and you're back."

---

## Section 5 — Demo: Memory (1:20–1:35)

Three layers, demoed in order:

### 1. CLAUDE.md — the project's shared memory

Ask Claude to make today's design decision permanent:

```
Add a rule to backend/CLAUDE.md: category is a fixed enum (Work, Personal, Other) —
validation must reject anything else. Keep it to two lines.
```

Open the file; show the diff. This is committed → **every teammate's Claude inherits it.**
Note the "two lines" constraint — callback to Section 0: CLAUDE.md stays minimal; a decision
earns its place there only if Claude can't derive it from the code.

### 2. The hierarchy (slide)

All of these load and concatenate, broadest first:

| Level | File | Who sees it |
| --- | --- | --- |
| Managed policy | e.g. `C:\Program Files\ClaudeCode\CLAUDE.md` | Whole org (admin-controlled) |
| User | `~/.claude/CLAUDE.md` | You, in every project |
| Project | `./CLAUDE.md` (+ `backend/CLAUDE.md` etc., loaded on demand) | Everyone in the repo |
| Local | `./CLAUDE.local.md` (gitignored) | Just you, just this repo |
| Imports | `@path/to/file` syntax inside any CLAUDE.md | Composable includes |

`/memory` opens a picker to edit any of them without leaving the session.

### 3. Auto memory — Claude's own notebook

Say: "There's also memory Claude manages itself." Tell Claude:

```
Remember: in this training repo, todos.db is disposable demo data — never worry about
preserving its contents.
```

Show where it landed: `~/.claude/projects/<project>/memory/` (entry point `MEMORY.md`,
loaded each session; topic files load on demand).

> **Rule of thumb for the room:** *facts the team needs* → CLAUDE.md (committed).
> *Your personal quirks* → `~/.claude/CLAUDE.md` or `CLAUDE.local.md`.
> *Session-to-session working notes* → let auto memory handle it.

---

## Section 6 — LAB (1:35–1:55)

Participants work on their own clone. Post these instructions:

### Lab: Add a due-date feature using the full loop

1. `claude`, then `Shift+Tab` into **plan** mode.
2. One goal-level prompt — write your own, but it must contain a **definition of done**.
   Skeleton if stuck:
   ```
   Add an optional due date to todos. Show it on each todo; highlight overdue todos.
   Follow CLAUDE.md. Done means: create-with-date, display, and overdue highlight
   all work in the browser, and the API returns due_date.
   ```
3. **Read the plan. Correct at least one thing before approving** (date format? where the
   highlight logic lives? nullable vs required?). This is the graded move of the lab.
4. Approve, let it execute, then verify yourself: `curl` the API + click through the browser.
5. Use `/rewind` at least once — even just to see the menu (bonus: revert a styling change).
6. Make one decision permanent in `CLAUDE.md` (e.g. "due_date is ISO8601 date-only, nullable").
7. Commit.

**Trainer roams for:** people approving plans without reading them (call it out gently — that's
the anti-pattern this whole session exists to break), and people writing step-by-step prompts
instead of goal + definition of done.

---

## Wrap (1:55–2:00)

- The loop: **goal → plan → correct → approve → verify → commit** (and rewind is your undo).
- Never approve a plan you didn't read.
- Memory turns today's decisions into tomorrow's defaults.
- **Homework:** use plan mode + one `/rewind` on your real work this week. Bring one story.
- Next session: turning repeated instructions into **skills** and non-negotiable rules into
  **hooks**.

---

## Trainer notes & fallbacks

- **Plan is too shallow** ("I'll add a category field and update the UI") → don't accept it.
  Reply: `Too vague. List the exact files, the schema change, how existing rows migrate, and
  the verification steps.` This failure is a better lesson than a perfect first plan.
- **Plan proposes dropping/recreating the table** → point at the data-loss risk, have it use
  `ALTER TABLE ADD COLUMN` with a default instead. (Existing rows need a default category —
  'Other' is fine.)
- **Claude adds tests** → fine, but note the repo has no test runner configured; verification
  in this project is browser + curl (backend/CLAUDE.md says so).
- **Rewind demo anticlimax** (bad change was too small) → the inline-styles prompt above is
  reliably ugly; alternatively `Delete all comments and rename all variables in main.py to
  single letters` is dramatic and safe.
- **`todos.db` gets weird mid-demo** → delete the file; the lifespan handler recreates the
  table on next server start. Say so out loud — it reinforces the "checkpoints don't cover the
  DB" point.
- **Participant machines without the app running** → pair them up; the lab works fine driver-
  navigator style.
