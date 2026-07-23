# Session 5 Teaching Guide — MCP: Connecting Claude to the Outside World (+ Plugins)

Trainer crib sheet + participant lab. ~2 hours.

**One-line thesis (repeat it until they can say it back):**
> **A skill teaches Claude a procedure; a hook enforces a rule; an *MCP server* gives Claude
> new *hands* — the ability to reach systems outside the repo.** GitHub, a live browser, docs
> indexes — all become tools Claude calls by name.

**What "outside the world" means here:** until now Claude could only read/write files and run
shell commands. MCP lets it *create a GitHub issue, open a PR, drive a real browser, and cite
live library docs* — without you copy-pasting anything.

**Artifacts produced this session** (the committable one is `.mcp.json`):

```
.mcp.json                 # project-scoped MCP servers — committed, whole team inherits
~/.claude.json            # user-scoped servers (GitHub PAT lives here — NOT committed)
```

> **Anchor the demo in what already exists:** the category filter built in Session 3 (fixed
> enum `General/Work/Personal/Shopping`, client-side filtering) is the exact feature the
> browser-MCP demo will verify. Claude closes the loop on its *own* prior work.

---

## Pre-session checklist (trainer)

- [ ] Sessions 3–4 merged; clean `git status` on `main`; `.claude/` skills + hooks present.
- [ ] **Both app servers runnable and confirmed:** backend `uvicorn main:app --reload` on
  `:8000`, frontend `npm run dev` on `:5173`. (Note the real ports — the `6 - MCP.md` handout
  says `:3000`; that's generic boilerplate. **Our app is `:5173`.**)
- [ ] **Node 18+ / `npx`** on PATH (`node --version`) — Playwright MCP downloads via `npx`.
- [ ] **GitHub PAT** created and tested (fine-grained: `repo`, `issues`, `pull_requests`,
  `workflows`). Have it in a paste buffer — you only see it once.
- [ ] A **scratch GitHub repo** (or a fork of ClaudeTodo) you can safely create issues/PRs in.
- [ ] **Pre-warm Playwright MCP once** before class: `npx -y @playwright/mcp@latest --version`
  (first download is slow on venue Wi-Fi; also runs `npx playwright install chromium`).
- [ ] All long prompts + `claude mcp add` commands in a snippets file — **never live-type a
  Bearer token or a long flag string on a projector.**
- [ ] Decide the participant path: everyone does **Playwright MCP** (no account needed);
  GitHub MCP is the stretch for those who did the PAT pre-work.

> **Participant pre-work email (must go out BEFORE this session):** install Node 18+, create a
> GitHub fine-grained PAT with the four scopes above, and `git pull` the latest `main`.

---

# PART A — MCP FUNDAMENTALS (0:00–0:15, slides)

## What MCP is

- **Model Context Protocol** = an *open* protocol for connecting an AI assistant to external
  tools and data. One client (Claude Code), many servers (GitHub, browser, docs…).
- The shape to draw on the board:
  ```
  Claude Code  ──MCP──►  MCP Server  ──API──►  External system
    (client)             (GitHub, Playwright,     (GitHub.com,
                          context7, …)             a browser, docs)
  ```
- A server exposes **tools** (things Claude can *call*), and sometimes **resources** (things
  Claude can *read*). Claude decides when to call them, the same way it decides to use Edit or
  Bash.

## The two transports

| Transport | When to use |
| --- | --- |
| **stdio** | Server runs as a **local process** on your machine (a binary, `npx`, or Docker). Claude Code spawns it. |
| **http** | Server is **remote / cloud-hosted**. Claude connects over HTTP with a token. No local install. |

> **Narration:** "stdio = a program on your laptop Claude talks to over a pipe. http = a URL
> Claude talks to with a Bearer token. GitHub offers both; we'll use the remote HTTP one — no
> Docker."

## The three config scopes (this is the team story)

| Scope | Flag | Stored in | Shared? |
| --- | --- | --- | --- |
| **local** | *(default)* | `.mcp.json` in project root, gitignored | No — your machine only |
| **project** | `--scope project` | `.mcp.json` **committed to the repo** | ✅ Yes — whole team |
| **user** | `--scope user` | `~/.claude.json` | No — all *your* projects |

- **Rule of thumb (put it on screen):** a server the whole team needs and that carries **no
  secret** → `project` (commit it). A server carrying **your token** (GitHub) → `user`
  (never commit a PAT). A one-off experiment → `local`.
- Check status any time inside a session with **`/mcp`**; from the shell with
  `claude mcp list` and `claude mcp get <name>`.

---

# PART B — GITHUB MCP: THE END-TO-END "AHA" (0:15–0:45)

The flagship demo: Claude reads a GitHub issue, implements it *in this codebase*, commits,
pushes a branch, and opens a PR — all by natural language.

## B1 — Add the server (remote HTTP, user scope)

Remote server = no Docker, no binary. The PAT rides as a Bearer token; user scope keeps it out
of the repo.

```bash
claude mcp add --transport http --scope user github \
  https://api.githubcopilot.com/mcp \
  --header "Authorization: Bearer ghp_YOUR_TOKEN_HERE"
```

> **Windows note:** use `--header "…"` (shown). If a shell mangles the quotes, the
> `claude mcp add-json github '{…}'` form in `docs/6 - MCP.md` is the fallback.

Verify:

```bash
claude mcp list          # github should be listed
```
Then inside a session: **`/mcp`** → `github` with a checkmark. If it says *pending*, wait —
Claude Code auto-reconnects with exponential backoff (up to 5 tries).

> **Security beat (say it out loud):** "That token is now in `~/.claude.json` in plaintext.
> Treat it like a password. Scope it to the minimum repos. Rotate it if it leaks. This is why
> GitHub goes in **user** scope, never in the committed `.mcp.json`."

## B2 — Warm-up prompts (prove the connection, 3 min)

Fire one or two so the room sees real data come back:

```
List my public repositories with their star counts.
```
```
Read the README from my "claudetodo" repo and summarise it in three bullets.
```

## B3 — The end-to-end flow (the demo they'll remember)

Do it as **two prompts** so the issue exists before the implementation starts.

1. Create the issue:
   ```
   Create an issue in my "claudetodo" repo titled "Add a Clear Completed button"
   describing: a button above the list that deletes all completed todos in one click.
   Label it "enhancement".
   ```
2. Implement it end-to-end:
   ```
   Look at that issue, implement the feature in this codebase, commit on a new branch
   feat/clear-completed, push it, and open a PR that links the issue. Do not merge.
   ```

Narrate as it runs: Claude **reads the issue via MCP**, then switches to its **normal file
tools** (Read/Edit) to write the code, uses **Bash** for git, then swaps back to **MCP** to
open the PR. *One agent, two kinds of hands — local tools and remote tools — in one loop.*

> **Verify, don't trust (the course ritual):** open the PR in the browser. Read the diff
> yourself. Does "Clear Completed" actually call `DELETE /api/todos/{id}` per completed row and
> reconcile state? If it's wrong, that's the lesson — say so and move on; don't merge it live.

> **Fallback if the network/PAT misbehaves:** the *issue → read → implement* half works fully
> offline of GitHub once the issue text is pasted. Degrade to that rather than debugging PAT
> scopes for ten minutes on stage.

---

# PART C — BROWSER MCP: CLAUDE VERIFIES ITS OWN UI (0:45–1:10)

The payoff of the whole course's "verify everything" thread: the agent closes its **own**
verification loop — no human clicking.

## C1 — Add Playwright MCP (user scope)

```bash
claude mcp add --scope user playwright -- npx -y @playwright/mcp@latest
```

`/mcp` → `playwright` with a checkmark. (First run pulls the package + a browser; this is why
we pre-warmed it.)

> **Two browser MCPs, one sentence of context:** Playwright MCP drives the page (click, type,
> snapshot). **Chrome DevTools MCP** is the alternative when you *also* want console errors,
> network requests, and performance traces. Use Playwright for "does the flow work"; reach for
> DevTools MCP when "why is it slow / what 500'd" matters.

## C2 — The demo prompt (uses OUR real app)

Both servers must be running. Then:

```
Open my app at http://localhost:5173. Add three todos:
"Buy milk" (Shopping), "Ship the release" (Work), and "Call the dentist" (Personal).
Mark "Ship the release" complete. Then click the Work filter pill and take a screenshot.
Tell me whether the filter shows only Work todos and whether the completed styling applied.
```

Claude drives the real browser: types into the input, picks the category `<select>`, clicks
pills, screenshots, and **reports back in prose**. This is exactly the create/complete/filter
flow from the PRD acceptance criteria — verified by the agent.

> **Why this beats the `.spec.ts` file in the handout:** `docs/6 - MCP.md` includes a written
> Playwright *test suite* (`tests/todo.spec.ts`). That's the **scripted, CI** style (great, and
> it's a Session 6 thread). **MCP is the interactive style** — no test file, Claude explores the
> live UI on command. Contrast them explicitly; both are legitimate, they solve different jobs.
>
> **Also flag the handout's placeholders:** that spec targets `localhost:3000`, a
> `"Add a new todo..."` placeholder, and `Active/Completed` filters — none of which match our
> app (`:5173`, `"What needs to be done?"`, category pills). Use it to teach that **you must
> adapt generic examples to your real UI**, which is precisely what MCP lets Claude do live.

## C3 — Break it on purpose (optional, high value)

```
Now filter by Personal and tell me the exact empty-state text if there are none,
then confirm the header count still reflects ALL todos, not the filtered subset.
```

This surfaces the two deliberate design decisions from Session 3 (global count, filter-aware
empty state) — and shows the agent *reading UI state to answer a question*, not just clicking.

---

# PART D — KNOWLEDGE & CODE-INTEL SERVERS (1:10–1:20)

Breadth, not depth — one prompt each so they know these exist.

- **context7** (live library docs). Ask something version-sensitive:
  ```
  Using context7, what's the current recommended way to define a FastAPI lifespan
  handler? Compare it to what backend/main.py does.
  ```
  Watch it cite *current* docs rather than training-cutoff memory — the fix for "the model is
  confidently out of date."
- **Serena** (symbol-level code navigation/editing): "find every reference to the `Todo`
  response model" — LSP-grade navigation instead of grep.
- **sequential-thinking**: a scratchpad server for multi-step reasoning on gnarly problems.

> **Narration:** "GitHub and Playwright give Claude *hands*. These give it *better eyes and a
> reference library*. Same protocol, different purpose."

---

# PART E — PLUGINS & MARKETPLACES (1:20–1:35)

The distribution finale that ties Sessions 4–5 together.

- A **plugin** = **skills + agents + hooks + MCP servers** bundled as **one installable thing**.
  Everything we set up by hand this session (and last) can ship as a single install.
  ```
  /plugin marketplace add anthropics/claude-plugins-community
  /plugin marketplace list
  /plugin install <name>@<marketplace>
  ```
- Install one live (if the network cooperates), then show **what it added** — new slash
  commands, maybe an MCP server, maybe a hook. Otherwise browse the marketplace listing and
  name-drop `anthropics/skills`.

> **The team story, stated plainly:** "Session 4 you committed skills and hooks so teammates
> inherit them on clone. Session 5, project-scope `.mcp.json` does the same for servers. A
> plugin collapses *all* of it into `/plugin install`. That's how an org rolls out a paved road."

---

# PART F — LAB (1:35–1:55)

Participants on their own clones, both servers running.

### Part 1 — Browser MCP (everyone)

1. Add Playwright MCP: `claude mcp add --scope user playwright -- npx -y @playwright/mcp@latest`.
2. Verify with `/mcp`.
3. Prompt Claude to drive **their** app through the full flow: add one todo per category,
   complete one, filter to each pill in turn, and **report** whether filtering + the
   global count behave correctly. Save the screenshot.

**Acceptance:** paste Claude's written report + the screenshot; state one thing the agent
observed that you did *not* explicitly tell it to check.

### Part 2 — GitHub MCP (stretch, needs PAT)

1. Add the remote GitHub server at **user** scope (command in B1).
2. Create an issue in your fork ("Add a todo count badge to the header", say).
3. Have Claude read it, implement on a branch, push, and open a PR linking the issue.
4. Review the diff yourself before merging — screenshot the PR.

**Trainer roams for:** `/mcp` showing *pending*/failed (usually a bad token or wrong scopes —
the #1 failure); `.mcp.json` accidentally holding a PAT (call it out — must be user scope);
`npx` still downloading (pre-warm saves this); the app not actually running on `:5173`.

---

## Wrap (1:55–2:00)

The updated decision guide — leave it on screen:

| Situation | Reach for |
| --- | --- |
| A fact that's always true ("routes live under /api") | CLAUDE.md |
| A procedure you repeat | **Skill** (S4) |
| A rule that must never be violated | **Hook** (S4) |
| Claude needs to reach an **external system** (GitHub, a browser, live docs) | **MCP server** |
| Ship skills + hooks + servers as one install | **Plugin** |

- **Scope discipline:** team server, no secret → project `.mcp.json` (commit it). Server with
  your token → user scope (never commit). One-off → local.
- **Cost note:** every connected server loads tool descriptions into context. Connecting ten
  servers you don't use is token tax on every turn — connect what you need, disconnect the rest.
- **Homework (S5→S6):** connect one MCP server to a *personal* project and do one real task
  with it. Next session: sub-agents and parallel worktrees — we build full auth with two agents
  working at once.

---

## Trainer notes & fallbacks

- **`/mcp` shows `github` pending or failed** → almost always the PAT: wrong scopes, expired, or
  a stray space in the Bearer header. Regenerate, re-add, reconnect — debugging this once is
  instructive.
- **`claude mcp add-json` fails on Windows** → use the `--transport http … --header "…"` form
  (shown in B1); it's the reliable Windows path.
- **Playwright MCP does nothing / times out** → the app isn't running, or it's on the wrong
  port. Confirm `:5173` (frontend) **and** `:8000` (backend) are both up before prompting.
- **`npx` first-run stalls on venue Wi-Fi** → the pre-warm step; if skipped, run the `npx`
  command in a side terminal while you talk through slides, then switch back.
- **Remote GitHub server blocked by org network** → fall back to the local Docker server
  (`docs/6 - MCP.md` Option A), or degrade the demo to issue-text-pasted + local implementation.
- **Someone commits a PAT** → great teachable moment: rotate the token immediately, move the
  server to user scope, and show that `.mcp.json` is where secrets must *never* live.
- **"Can I share the GitHub server with my team via `.mcp.json`?"** → yes for the *server
  definition*, but each teammate supplies their **own** token via an env var reference — you
  share the wiring, not the credential.
- **Context bloat after adding many servers** → show `/mcp` and `claude mcp remove <name>`;
  disconnecting is part of hygiene, same lesson as deleting a stale hook in Session 4.
