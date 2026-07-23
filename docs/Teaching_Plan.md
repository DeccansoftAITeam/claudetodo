# ClaudeTodo — Claude Code Training Plan (Sessions 3–6)

**Audience:** Working developers (comfortable with git, terminal, REST, React/Python) who are new to Claude Code.
**Format:** Demo-led + guided labs. Trainer demos each concept on the ClaudeTodo repo, then participants repeat a scoped exercise on their own copy.
**Duration:** ~2 hours per session (adjust lab time to fit).
**Vehicle:** The ClaudeTodo app — every concept lands as a real change to this repo.

## Where we are

Sessions 1–2 (completed) delivered: install & first session, prompting basics, building the base app (FastAPI + SQLite backend, React/Vite frontend), `CLAUDE.md` at root/backend/frontend, the API contract, and git fundamentals with Claude.

**Current repo state:** base CRUD todo app working, 2 commits on `main`, no `.claude/` directory yet, no categories, no auth. That is exactly the starting state the remaining demos assume.

## Coverage map

| Session | Theme | Existing doc used | New material |
| --- | --- | --- | --- |
| 3 | Agentic thinking, Plan mode, checkpoints, memory | `Session_03_Demo_Guide (2).md` | `/rewind`, checkpoints, memory (`#`), permission modes |
| 4 | Skills & Hooks | `5 - Skills.md`, `Hooks.md` | Built-in skills tour, third-party skills, marketplaces |
| 5 | MCP & Plugins | `6 - MCP.md` | Chrome DevTools / context7 / Serena MCPs, plugins |
| 6 | Sub-agents, parallel worktrees, headless & CI | `SubAgents.md`, `Session_07_Demo_Guide.md` | `claude -p`, GitHub Actions, wrap-up |

---

# Session 3 — Agentic Thinking: Plan Mode, Checkpoints & Memory

**Goal:** Participants stop treating Claude as autocomplete and start treating it as an agent: one goal-level prompt, a reviewed plan, verified execution, and the ability to rewind mistakes.

**Feature built this session:** Category system (fixed dropdown: Work / Personal / Other) with filtering.

### Agenda

| Time | Block | Mode |
| --- | --- | --- |
| 0:00–0:20 | Recap + "under the hood": Claude Code's system-prompt architecture (Piebald-AI extraction repo) vs Codex's lean prompt → why CLAUDE.md must stay minimal and scoped. Then the agentic loop and permission modes (`Shift+Tab`). | Slides + browser |
| 0:15–0:45 | **Demo: Plan mode feature build** — follow `Session_03_Demo_Guide (2).md`. One goal-level prompt for the category system, read the plan aloud, correct it *before* code ("correcting the plan is cheap"), approve, execute. | Demo |
| 0:45–1:00 | **Demo: Mid-flight intervention + audit.** Change a design decision mid-run; then scroll the tool-call log — count Reads/Edits/Bash calls, note files touched that were never named in the prompt. | Demo |
| 1:00–1:15 | **Demo: Checkpoints & `/rewind`.** Ask Claude for a deliberately bad change (e.g. "rewrite App.jsx to inline all styles"). Show Esc twice / `/rewind` → restore code, conversation, or both. Message: experimentation is cheap when undo is instant. Note what checkpoints do NOT cover (bash side effects, DB rows). | Demo |
| 1:15–1:30 | **Memory.** The `#` shortcut to append a rule to CLAUDE.md live; memory hierarchy (enterprise → project → user); `/memory` to edit; auto memory directory. Add a real rule mid-demo (e.g. "categories are a fixed enum — never free text") and show it persist to the file. | Demo |
| 1:30–1:55 | **Lab:** each participant adds a **due-date feature** (date field, overdue highlight, sort toggle) using Plan mode end-to-end: goal prompt → read plan → correct at least one thing → approve → verify in browser. Then use `#` to record one project convention they discovered. | Lab |
| 1:55–2:00 | Wrap: the discipline — never approve a plan you didn't read. Homework: use `/rewind` once on real work this week. | — |

### Trainer prep
- Both servers runnable; clean `git status` on `main`.
- Pre-write the goal prompt and the correction prompt (in the demo guide).
- Have a "bad change" prompt ready for the rewind demo.

### Fallbacks
- Plan too shallow → good teaching moment: reject it, demand file-level detail, re-plan.
- Lab overruns → due-date backend only; frontend becomes homework.

---

# Session 4 — Skills & Hooks: Packaging Instructions vs Enforcing Rules

**Goal:** Participants can package repeated instructions as skills and enforce non-negotiable rules with hooks — and can articulate the line between them: **skills are advisory, hooks are enforced.**

**Artifacts built this session:** `.claude/skills/commit/`, `.claude/skills/api-endpoint/`, and a project hook bundle (format-on-edit, protect-files, bash audit) — all committed so the whole team inherits them.

### Agenda

| Time | Block | Mode |
| --- | --- | --- |
| 0:00–0:10 | What skills are, where they live (enterprise/personal/project), how discovery works (descriptions load; full content loads on invoke). From `5 - Skills.md`. | Slides |
| 0:10–0:25 | **Demo: built-in skills tour.** `/review` on the working diff, `/security-review` on the category branch, `simplify`, `fewer-permission-prompts` (scans transcripts, proposes an allowlist — a crowd-pleaser). | Demo |
| 0:25–0:45 | **Demo: build two custom skills.** (1) `/commit` — conventional commits, `disable-model-invocation: true`, `allowed-tools` gating. (2) `/api-endpoint` — scaffolds a new FastAPI route following backend/CLAUDE.md conventions, using `$ARGUMENTS` and dynamic context injection (`` !`git diff HEAD` ``) — show the rendered prompt so the mechanism is visible. | Demo |
| 0:45–0:55 | **Third-party skills.** `anthropics/skills` repo and skills marketplaces; installing one; the Agent Skills open standard (works across tools). Show one polished example (e.g. a document or PDF skill) rather than a survey. | Demo |
| 0:55–1:05 | Hooks concept: lifecycle events (`PreToolUse`, `PostToolUse`, `SessionStart`, `Notification`, `Stop`…), matchers, exit codes (0 = proceed, 2 = block + stderr feeds back to Claude). From `Hooks.md`. Key line: *a SKILL.md says "always run tests" and Claude probably will; a PreToolUse hook means it literally cannot skip them.* | Slides |
| 1:05–1:30 | **Demo: hook bundle, built live.** (1) Notification hook (desktop ping — 2 min win). (2) PostToolUse format-on-edit with prettier. (3) PreToolUse `protect-files` script blocking `.env` / `package-lock.json` — then *ask Claude to edit `.env`* and watch it get blocked and adapt. (4) Bash audit log via `jq`. Verify with `/hooks`. | Demo |
| 1:30–1:55 | **Lab:** participants build one skill (their choice: `/commit` variant or a `/standup` diff-summary skill) **and** the protect-files hook, then prove the hook fires by asking Claude to violate it. Stretch: SessionStart `compact` matcher that re-injects project rules. | Lab |
| 1:55–2:00 | Wrap: decision guide — repeated instructions → skill; non-negotiable rule → hook; both committed to the repo = team-wide automatically. | — |

### Trainer prep
- `jq` installed (Windows: `choco install jq`); prettier available in frontend.
- Hook scripts pre-written in a snippets file — live-typing JSON with escaped quotes on a projector is where demos die.
- Test the Windows notification variant beforehand.

### Fallbacks
- Hook JSON typo → `/hooks` shows what actually registered; debug live, it's instructive.
- prettier slow on first run → warm it up before class.

---

# Session 5 — MCP: Connecting Claude to the Outside World (+ Plugins)

**Goal:** Participants can connect and use MCP servers — GitHub for repo workflows, a browser for real UI verification, docs/code-intel servers for better answers — and know how plugins distribute all of this as one install.

**Depends on:** participants need a GitHub PAT and Node.js (for `npx` MCP servers). Send setup instructions **before** this session.

### Agenda

| Time | Block | Mode |
| --- | --- | --- |
| 0:00–0:15 | What MCP is (open protocol; Claude ↔ server ↔ external system), transports (stdio vs http), config scopes (local / project `.mcp.json` / user), `/mcp` status. From `6 - MCP.md`. | Slides |
| 0:15–0:45 | **Demo: GitHub MCP.** Add the remote server (`claude mcp add --transport http github …`), verify with `/mcp`. Then the end-to-end flow: *create an issue ("Add a clear-completed button") → have Claude read the issue, implement it, commit, push a branch, open a PR linking the issue* — all by natural language. This is the "aha" demo. | Demo |
| 0:45–1:10 | **Demo: browser MCP — Claude verifies its own UI.** Add Playwright MCP (`claude mcp add --scope user playwright -- npx -y @playwright/mcp@latest`). Prompt: open localhost:5173, add three todos, complete one, filter by category, screenshot, report whether the filter works. Message: *the agent closes its own verification loop — no manual clicking.* Mention Chrome DevTools MCP as the alternative when you also want console/network/performance access. | Demo |
| 1:10–1:20 | **Quick tour: knowledge & code-intel servers.** context7 (live library docs — ask a FastAPI question and watch it cite current docs), Serena (symbol-level code navigation/editing), sequential-thinking. One prompt each — breadth, not depth. | Demo |
| 1:20–1:35 | **Plugins & marketplaces.** A plugin = skills + agents + hooks + MCP servers in one installable bundle. `/plugin marketplace add <repo>`, browse, install one, show what it added. Team distribution story: one plugin install replaces this whole session's manual setup. | Demo |
| 1:35–1:55 | **Lab:** participants add Playwright MCP and have Claude drive their own app through the full create/complete/filter/delete flow and report findings. Stretch: GitHub MCP issue → implement → PR against their own fork. | Lab |
| 1:55–2:00 | Wrap: scope guidance (project `.mcp.json` for team servers, user scope for personal), token/context cost of over-connecting servers, security note on tokens. | — |

### Trainer prep
- PAT created and tested; a scratch GitHub repo (or fork) you can safely create issues/PRs in.
- Playwright MCP pre-run once (`npx` first-download is slow on venue Wi-Fi).
- Both app servers running before the browser demo.

### Fallbacks
- Venue network blocks Docker/ghcr → use the remote HTTP GitHub server (no Docker).
- `npx` download stalls → have the package cached, or switch the demo to Chrome DevTools MCP if pre-installed.
- PAT scopes wrong → classic failure; show the error, fix the scopes, reconnect. Real-world debugging.

---

# Session 6 — Sub-agents, Parallel Workstreams, Headless & CI

**Goal:** Participants can delegate to sub-agents, run parallel workstreams in git worktrees, define a custom reviewer agent, and take Claude out of the terminal into scripts and CI.

**Feature built this session:** Full authentication (JWT backend + login/register frontend) built by two parallel agents.

### Agenda

| Time | Block | Mode |
| --- | --- | --- |
| 0:00–0:10 | Sub-agent concept: isolated context, own tools, only the final report returns. Built-ins (Explore, Plan, general-purpose). When to delegate: high-volume output, parallel independent work, tool restriction. From `SubAgents.md`. | Slides |
| 0:10–0:25 | **Demo: custom `code-reviewer` agent.** Create `.claude/agents/code-reviewer.md` via `/agents` (read-only tools: Read, Grep, Glob, Bash; strong action-oriented `description` so it auto-triggers). Run it on the session-5 diff. Commit it. | Demo |
| 0:25–1:10 | **Demo: parallel auth build** — follow `Session_07_Demo_Guide.md`. Two worktrees (`feat/auth-backend`, `feat/auth-frontend`), one message firing both Agent calls, narrate isolation while they run, **verify each report yourself** (pytest, npm run build — "trust but verify"), merge both, prove register→login→todos→logout in the browser, clean up worktrees. | Demo |
| 1:10–1:30 | **Demo: headless mode & CI.** `claude -p "list all API endpoints and their status codes" --output-format json` — Claude as a scriptable Unix tool. Then GitHub Actions: `/install-github-app`, the `claude-code-action` workflow, `@claude` on an issue/PR triggering automated work; automated PR review pipeline as the flagship use case. | Demo |
| 1:30–1:50 | **Capstone lab:** participants run their `code-reviewer` agent on the merged auth code and fix one finding; then write a headless one-liner (`claude -p`) that produces a review summary of `git diff main`. Stretch: two-agent parallel task of their own design. | Lab |
| 1:50–2:00 | **Course wrap:** the full toolkit map (CLAUDE.md → plan mode → skills → hooks → MCP → agents → CI), adoption path for their teams (start: CLAUDE.md + plan mode; then commit skills/hooks; then MCP; then CI), where to keep learning (docs, `anthropics/skills`, plugin marketplaces). | Slides |

### Trainer prep
- Clean `main` including sessions 3–5 work; the auth prompts from the Session 7 guide updated with **absolute paths** for your machine.
- Dry-run the parallel auth demo once — it's the longest, most failure-prone demo of the course.
- A GitHub repo with Actions enabled and the Claude GitHub app installable (needs API key/subscription decision beforehand).

### Fallbacks
- All the Session 7 guide's trainer notes apply (agent fails verification → re-delegate narrowly; merge conflict → resolve live as a lesson).
- GitHub Actions blocked by org policy → show the workflow YAML and a recorded/screenshot run instead; keep `claude -p` local, which always works.

---

## Cross-session threads

- **One repo, compounding state.** Every session's artifacts (`.claude/skills/`, hooks in `.claude/settings.json`, `.mcp.json`, `.claude/agents/`) get **committed**, so by session 6 the repo itself demonstrates the team-distribution story.
- **Verify everything.** Each session repeats the ritual: Claude reports done → we check ourselves (browser, pytest, diff). By session 6 (sub-agent reports) this discipline pays off visibly.
- **Homework between sessions** keeps hands warm: S3→S4: use plan mode + `/rewind` on real work. S4→S5: write one skill for your own project + do the PAT/Node setup. S5→S6: connect one MCP server to a personal project.

## Master prep checklist (do once, before Session 3)

- [ ] Repo on clean `main`, both servers verified running.
- [ ] `jq`, prettier, Node/npx, Docker (optional) installed on the demo machine.
- [ ] GitHub PAT with repo/issues/PR scopes; scratch repo for MCP demos.
- [ ] Snippets file with every long prompt, hook script, and JSON block — never live-type these.
- [ ] Participant pre-work email: git clone, Python venv + `pip install`, `npm install`, Claude Code login, (before S5) PAT + Node.
