# Session 4 Teaching Guide — Skills & Hooks: Packaging Instructions vs Enforcing Rules

Trainer crib sheet + participant lab. ~2 hours.

**One-line thesis (repeat it until they can say it back):**
> **Skills are advisory — Claude will *probably* follow them. Hooks are enforced — Claude
> *cannot* get past them.** Skills package procedures; hooks encode policy.

**Artifacts built this session** (all committed, so the whole team inherits them):

```
.claude/
├── skills/
│   ├── commit/SKILL.md          # user-only /commit command
│   ├── api-endpoint/SKILL.md    # named arguments
│   └── standup/SKILL.md         # dynamic context injection
├── hooks/
│   ├── guard_files.py           # PreToolUse — blocks protected files
│   ├── format.py                # PostToolUse — prettier after edits
│   └── audit_bash.py            # PostToolUse — command audit log
└── settings.json                # hook registrations
```

---

## Pre-session checklist (trainer)

- [ ] Session 3 work merged; clean `git status` on `main`.
- [ ] `python --version` works on the demo machine (hooks are Python scripts — portable
  across Windows/macOS/Linux, unlike bash one-liners).
- [ ] Prettier resolvable in the frontend: `cd frontend && npx --no-install prettier --version`
  (if not: `npm i -D prettier`).
- [ ] A `.env` file exists at repo root for the guardrail demo — create a dummy:
  `echo "SECRET_KEY=demo123" > .env` (and confirm it's gitignored).
- [ ] All SKILL.md contents and hook scripts below in a snippets file — **never live-type
  JSON with escaped quotes on a projector.**
- [ ] Optional for the third-party segment: internet access for
  `/plugin marketplace add anthropics/claude-plugins-community`.

---

# PART A — SKILLS (0:00–0:55)

## Section A1 — What a skill is (0:00–0:10, slides)

- A skill = a **directory with a SKILL.md** — markdown + YAML frontmatter. Nothing more.
- It solves one problem: **repeated instructions**. If you've pasted the same guidance twice,
  it should be a skill.
- Discovery: at session start only the *descriptions* load; the full content loads when the
  skill is invoked — by you (`/skill-name`) or by Claude automatically when the description
  matches the task.
- Where skills live decides who gets them:

| Location | Path | Scope |
| --- | --- | --- |
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<name>/SKILL.md` | Everyone who clones this repo |

> **Narration:** "CLAUDE.md is for *facts that are always true*. When a section of CLAUDE.md
> starts describing a *procedure* — 'when committing, do X then Y' — that's a skill trying to
> be born. Move it out."

## Section A2 — Demo: built-in skills tour (0:10–0:25)

Claude Code ships skills. Run two or three live on the session-3 diff:

1. **`/security-review`** — run it on the category/due-date work:
   ```
   /security-review
   ```
   Walk the findings (it may flag the raw SQL patterns — good discussion fodder).
   *Caution: it diffs against `origin/HEAD` — needs the remote to exist and be pushed.*
2. **`fewer-permission-prompts`** — the crowd-pleaser: it scans your transcript history and
   proposes a permission allowlist for the read-only commands you approve over and over.
   Show the generated `.claude/settings.json` entries — this connects to hooks later
   (same file, same idea: encode decisions once).
3. Name-drop the rest — `/init` (they saw it in session 1), `/review` (PR review, session 6),
   `simplify`, `loop`, `schedule`.

## Section A3 — Demo: build three custom skills (0:25–0:45)

Each skill teaches exactly one mechanism. Build them in this order.

### Skill 1 — `/commit` (mechanism: user-only invocation + tool gating)

`.claude/skills/commit/SKILL.md`:

```markdown
---
name: commit
description: Stage all changes and create a conventional commit.
disable-model-invocation: true
allowed-tools: Bash(git add *), Bash(git commit *), Bash(git status *), Bash(git diff *)
---

Stage and commit the current changes:

1. Run git status and git diff HEAD to understand what changed.
2. Stage everything: git add .
3. Write a conventional commit message:
   - Format: <type>(<scope>): <summary>   (types: feat, fix, docs, refactor, chore)
   - Summary under 72 characters.
4. Commit and show the hash.

If $ARGUMENTS is provided, use it as extra context for the message.
```

Run `/commit` on any pending change. Then point at the two frontmatter lines:

- `disable-model-invocation: true` → **only you** can fire this. Claude never auto-commits.
- `allowed-tools` → even while the skill runs, Claude can only use these git commands.
  A skill can *narrow* power, not just add it.

### Skill 2 — `/api-endpoint` (mechanism: named arguments)

`.claude/skills/api-endpoint/SKILL.md`:

```markdown
---
name: api-endpoint
description: Scaffold a new FastAPI endpoint following this repo's conventions.
disable-model-invocation: true
arguments: [method, path]
argument-hint: [GET|POST|PATCH|DELETE] [/api/route]
---

Add a $method endpoint at $path to backend/main.py.

Requirements (from backend/CLAUDE.md — read it first):
- Route lives under /api so the Vite proxy reaches it.
- Pydantic request/response models with extra: "forbid".
- Explicit 404/422 handling consistent with the existing endpoints.
- Use the existing _get_conn() helper; per-request connection; close it.

After writing it, show me a curl command to test it. Do not run the server.
```

Invoke: `/api-endpoint GET /api/todos/stats` — show how `$method` / `$path` substituted.

### Skill 3 — `/standup` (mechanism: dynamic context injection — the magic one)

`.claude/skills/standup/SKILL.md`:

```markdown
---
name: standup
description: Summarise recent work in this repo as a standup update.
disable-model-invocation: true
---

## Repo state (injected live)

- Uncommitted changes: !`git diff HEAD --stat`
- Recent commits: !`git log --oneline -5`

## Your task

Write a 3-bullet standup update: what was done (from the commits), what is in
progress (from the diff), and any risk you can infer. Plain language, no file paths.
```

Run `/standup`. Then explain the trick: the `` !`command` `` lines executed **before** Claude
saw anything — the output replaced the placeholder. Claude received real repo state, not an
instruction to go look.

> **Narration:** "Three skills, three mechanisms: gating, arguments, injection. Every skill
> you'll ever write is some combination of these."

Commit all three: `/commit skills for the team`.

## Section A4 — Third-party skills & marketplaces (0:45–0:55)

- You don't write everything yourself. Skills follow an **open standard** (agentskills.io) and
  install via plugin marketplaces:
  ```
  /plugin marketplace add anthropics/claude-plugins-community
  /plugin install <name>@<marketplace>
  ```
- Anthropic's own `anthropics/skills` repo ships polished skills (the document/PDF/spreadsheet
  family, and more). Community marketplaces bundle skills + agents + hooks + MCP servers in one
  install — that's a **plugin**, and it's session 5's closing topic.
- Demo one install if the network cooperates; otherwise show the marketplace listing and move on.

---

# PART B — HOOKS (0:55–1:30)

## Section B1 — Concept (0:55–1:05, slides)

- A hook = "**when event X fires, run this command**." Your command. Deterministic. The model
  is not consulted.
- The contrast that justifies the session:
  > Put "always run the formatter" in a skill and Claude will *usually* do it.
  > Put it in a PostToolUse hook and it happens **every time, mechanically**.
  > Policy, not prompting.
- The events that matter today (full catalogue in `docs/Hooks.md`):

| Event | Fires | Today's use |
| --- | --- | --- |
| `PreToolUse` | Before a tool call — **can block it** | Protect `.env` & friends |
| `PostToolUse` | After a tool call succeeds | Auto-format, audit log |
| `Notification` | Claude waits for you | Desktop ping |
| `SessionStart` (matcher `compact`) | After compaction | Re-inject project rules |

- The contract: hooks receive event JSON on **stdin**; **exit 0** = proceed (stdout can add
  context on some events); **exit 2** = **block**, and stderr is fed back to Claude so it can
  adapt.
- We write hooks as **Python scripts**, not bash one-liners — same file runs on Windows,
  macOS, Linux; no `jq`, no quoting hell.

## Section B2 — Demo: the two-minute win — Notification hook (1:05–1:10)

Into `~/.claude/settings.json` (user-level — this one is personal, not project):

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "powershell.exe -Command \"[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms'); [System.Windows.Forms.MessageBox]::Show('Claude Code needs your attention', 'Claude Code')\""
          }
        ]
      }
    ]
  }
}
```

Trigger something that needs permission, alt-tab away, get pinged. Cheap dopamine; now they
believe hooks are real.

## Section B3 — Demo: the project hook bundle (1:10–1:30)

Build the three project hooks. Scripts first, one registration block at the end.

### Hook 1 — `guard_files.py` (PreToolUse — the star demo)

`.claude/hooks/guard_files.py`:

```python
import json
import sys

PROTECTED = [".env", "package-lock.json", "todos.db", ".git/"]

data = json.load(sys.stdin)
path = (data.get("tool_input") or {}).get("file_path", "") or ""
norm = path.replace("\\", "/")

for pattern in PROTECTED:
    if pattern in norm:
        print(f"Blocked: {path} matches protected pattern '{pattern}'", file=sys.stderr)
        sys.exit(2)

sys.exit(0)
```

### Hook 2 — `format.py` (PostToolUse)

`.claude/hooks/format.py`:

```python
import json
import subprocess
import sys
from pathlib import Path

FRONTEND_EXT = {".js", ".jsx", ".ts", ".tsx", ".css", ".json", ".html", ".md"}

data = json.load(sys.stdin)
path = (data.get("tool_input") or {}).get("file_path", "") or ""
if path and Path(path).suffix in FRONTEND_EXT and "node_modules" not in path:
    subprocess.run(
        f'npx --no-install prettier --write "{path}"',
        shell=True,
        capture_output=True,
    )
sys.exit(0)
```

(If the backend grows a formatter later — black/ruff — this script is where it plugs in.)

### Hook 3 — `audit_bash.py` (PostToolUse on shell tools)

`.claude/hooks/audit_bash.py`:

```python
import json
import os
import sys
import time

data = json.load(sys.stdin)
entry = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "cmd": (data.get("tool_input") or {}).get("command", ""),
    "cwd": data.get("cwd", ""),
}
log = os.path.join(
    os.environ.get("CLAUDE_PROJECT_DIR", "."), ".claude", "bash-audit.log"
)
with open(log, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry) + "\n")
sys.exit(0)
```

### Registration — `.claude/settings.json` (project-level, committed)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python",
            "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/guard_files.py"]
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python",
            "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/format.py"]
          }
        ]
      },
      {
        "matcher": "Bash|PowerShell",
        "hooks": [
          {
            "type": "command",
            "command": "python",
            "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/audit_bash.py"]
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "echo Project rules: category is a fixed enum. All routes under /api. Verify in browser - no test suite exists."
          }
        ]
      }
    ]
  }
}
```

Verify: run `/hooks` — you should see PreToolUse (1), PostToolUse (2), SessionStart (1).

**Timing note (say it):** tool-event hooks (Pre/PostToolUse) take effect on the next matching
tool call in the current session. `SessionStart` hooks only run at the *next* session start —
so the compact re-inject won't be demoable until a restart.

### Try to break it (the moment the room remembers)

```
Open .env and change SECRET_KEY to something stronger.
```

The PreToolUse hook refuses (exit 2). Read Claude's reaction aloud — it *receives the stderr
message and adapts*, usually explaining that the file is protected and suggesting an
alternative.

> **Narration:** "I didn't ask nicely. I didn't put it in CLAUDE.md and hope. The edit is
> *mechanically impossible*. That's the difference between a convention and a policy."

Then two quick proofs:
- Ask Claude to write a deliberately ugly one-line HTML/JSX file → open it → prettier already
  reformatted it (PostToolUse).
- `type .claude\bash-audit.log` → every shell command from this session, timestamped
  (compliance people in the room will perk up).

Commit the bundle.

---

## Section C — LAB (1:30–1:55)

Participants on their own clones. Post these instructions:

### Part 1 — Build a skill (pick ONE)

- **Option A — `/log-milestone`:** appends a structured entry (date, prompt used, concept,
  files changed) to `docs/BUILD-LOG.md`. Use `$ARGUMENTS` for the milestone title and
  `` !`git diff HEAD --stat` `` to inject what changed. *You'll use this skill for the rest of
  the course to document your own progress — meta, and genuinely useful.*
- **Option B — your own `/commit` variant:** e.g. enforce a ticket-number prefix, or a
  different commit convention your real team uses.

Acceptance: invoke it, show the rendered result, and explain which of the three mechanisms
(gating / arguments / injection) it uses.

### Part 2 — Build the guardrail hook

1. Create `guard_files.py` protecting **`.env` and one file you choose** (e.g. `PRD.md`).
2. Register it in `.claude/settings.json` (copy the registration block, adjust).
3. Verify with `/hooks`.
4. **Prove it:** ask Claude to edit the protected file. Screenshot the refusal.

Stretch: add the audit hook and show the log; or a `SessionStart`/`compact` re-inject with
your own project rules (verify it next session).

**Trainer roams for:** JSON syntax errors in settings.json (`/hooks` showing nothing = the file
didn't parse — this is the #1 failure), and hooks tested in the same turn they were written
(needs a *next* tool call to fire).

---

## Wrap (1:55–2:00)

The decision guide — leave this on screen:

| Situation | Reach for |
| --- | --- |
| A fact that's always true ("routes live under /api") | CLAUDE.md |
| A procedure you repeat ("commit like this", "scaffold an endpoint") | **Skill** |
| A rule that must never be violated ("never touch .env") | **Hook** |
| A scoped job someone else should do in isolation | Sub-agent (session 6) |

- Everything we built today is **in the repo** — clone it and you inherit the commands and the
  guardrails. That's the team story.
- **Homework:** write one skill for your real project; bring it. And before session 5:
  create a GitHub PAT + install Node 18+ (setup mail follows) — we're connecting Claude to
  GitHub and a live browser next.

---

## Trainer notes & fallbacks

- **`/hooks` shows nothing after editing settings.json** → JSON parse error. Paste the file
  into Claude: `Validate this JSON and fix it.` Debugging this live is instructive, once.
- **Prettier hook does nothing** → `npx --no-install` requires prettier in
  `frontend/node_modules`; the demo file must be inside `frontend/`. Quick fix:
  `cd frontend && npm i -D prettier`.
- **`python` not on PATH on a participant machine** → try `py` as the command, or point the
  registration at the backend venv's python.
- **Hook fires but nothing blocks** → they exited 1, not 2. Exit 2 is the block signal; other
  non-zero codes just log an error and proceed.
- **`/security-review` errors about origin/HEAD** → repo has no pushed remote; either push
  first or skip to `fewer-permission-prompts` and name-drop it.
- **Notification MessageBox annoying after the demo** → show how to delete the hook from
  `~/.claude/settings.json` — deleting a hook is also a lesson.
- **Someone asks "can Claude edit the hook to unblock itself?"** → great question: project
  settings changes require review, and you'd see the edit; for real enforcement, put policy
  hooks in managed (admin) settings that users can't override. Bridge to the governance story.
