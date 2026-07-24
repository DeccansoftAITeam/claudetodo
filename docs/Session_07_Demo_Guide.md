# Session 7 Demo Guide: Sub-Agents & Parallel Workstreams

Trainer crib sheet. Narration cues, exact commands, pivot points. Keep a terminal, a browser, and the Claude Code window visible together.

---

## Section 1: Frame the Concept (2–3 min, on slides)

Three beats before going to the terminal:

- A sub-agent is a Claude spawned from your main session — isolated context, own tools, scoped task.
- Parallelism lets independent work happen concurrently. One message, many agents.
- Git worktrees give each agent its own workspace so parallel edits don't collide.

Then switch to the demo.

---

## Section 2: Set Up the Two Worktrees

### Step 1 — Confirm clean state

```bash
cd claudetodo
git status
git branch
```

Narration: "We're on main, working tree clean. We're going to split the next feature — authentication — into two parallel workstreams. Backend agent on one branch, frontend agent on another."

### Step 2 — Create the worktrees

```bash
git worktree add ../auth-backend -b feat/auth-backend
git worktree add ../auth-frontend -b feat/auth-frontend
git worktree list
```

Narration: "Two new directories outside the main repo. Each has a fresh checkout on its own branch. The .git folder is shared — worktrees are lightweight. Now each agent has its own place to work."

---

## Section 3: Fire Two Agent Calls in One Message

This is the moment of truth. Paste the whole prompt as a single message:

```
I want you to delegate authentication work to two sub-agents in parallel.

Set up: two git worktrees exist — ../auth-backend on branch feat/auth-backend,
and ../auth-frontend on branch feat/auth-frontend. Each agent should work only
in its assigned worktree.

Use the Agent tool (alias: Task). Fire BOTH Agent calls in a single response so
they run concurrently. Use subagent_type: "general-purpose" for each.

AGENT A — BACKEND. 
Prompt:
  "Working directory: /absolute/path/to/auth-backend/backend
   Add JWT authentication to this FastAPI project.

   Required:
   - A new module auth.py with: bcrypt password hashing, JWT signing with a
     secret from env (AUTH_SECRET_KEY), JWT verification, and a get_current_user
     dependency.
   - A User ORM model added to models.py (id, email unique, hashed_password).
   - Endpoints: POST /auth/register, POST /auth/login (returns {access_token,
     token_type}).
   - The existing /todos endpoints require authentication via the dependency.
   - Tests in tests/test_auth.py covering register, login, and that an
     authenticated request to /todos succeeds while an unauthenticated one
     returns 401.
   - Follow CLAUDE.md conventions.

   Verify by running pytest and report the number of passing tests.
   Return: a short summary (under 200 words) of files changed and test result.
   Commit your changes on the current branch before finishing."

AGENT B — FRONTEND. Prompt:
  "Working directory: /absolute/path/to/auth-frontend/frontend
   Add login and registration UI to this React (Vite) app.

   Required:
   - Login.jsx and Register.jsx under src/pages/ — email + password form,
     validation, error display, fetch to the backend /auth/login and
     /auth/register.
   - AuthContext.jsx under src/context/ — holds the token, provides login(),
     logout(), and isAuthenticated. Token persisted in localStorage.
   - App.jsx updated: unauthenticated users see Login; authenticated users see
     the existing todos UI. Logout button visible when logged in.
   - api.js updated to send Authorization: Bearer <token> on all requests.

   Verify by running npm run build and report any warnings or errors.
   Return: a short summary (under 200 words) of files changed and build result.
   Commit your changes on the current branch before finishing."

After both agents complete, report back with:
1. Which files each agent changed
2. Whether each verification passed
3. The commit SHA on each branch
```

Narration while the agents run:

- "Both agents kick off together. That's parallel execution — one message from me, two agents running concurrently."
- "Each agent has its own tool stream. Reads, edits, bash calls — but they're not visible in my main context. Only the final reports will come back."
- "Waiting. The backend agent is usually faster — JWT and bcrypt are well-known patterns. The frontend agent takes a bit longer — more files."

---

## Section 4: Read the Reports and Verify

When both agents finish, the main Claude summarises. Read the summaries aloud to the room. Then verify.

### Backend verification

```bash
cd ../auth-backend/backend
export AUTH_SECRET_KEY="demo-secret-not-for-prod"
export MSSQL_SA_PASSWORD='YourStrong!Passw0rd'
pytest -v
git log --oneline -5
git diff main --stat
```

Narration: "Report said tests pass. I'm running them myself. Green. Report said five files changed. Diff confirms. That matches."

### Frontend verification

```bash
cd ../auth-frontend/frontend
npm install   # if dependencies changed
npm run build
git log --oneline -5
git diff main --stat
```

Narration: "Build successful. Diff shows the new pages and context file. Matches the report."

---

## Section 6: Merge Both Branches

Back to main:

```bash
cd ../claudetodo
git merge feat/auth-backend --no-ff -m "Merge auth-backend: JWT + register/login"
git merge feat/auth-frontend --no-ff -m "Merge auth-frontend: Login/Register UI + AuthContext"
```

Restart the servers:

```bash
cd backend
# Ctrl+C then:
uvicorn main:app --reload

# In another terminal:
cd frontend
npm run dev
```

Narration: "Two merges. Both clean because the agents stayed in their lanes. No conflicts."

---

## Section 7: Prove It End-to-End

Open `http://localhost:5173`:

1. You should see the Register / Login page (not todos).
2. Register a new user — email + password.
3. You're logged in. The todos UI appears.
4. Create a todo. It persists.
5. Click Logout. Back to Login page.
6. Log back in. Your todos are still there.

Narration: "One message from me. Two agents. Two branches. One merge. Working authentication. Total time — about one build cycle, because everything happened in parallel."

---

## Section 8: Cleanup the Worktrees

```bash
git worktree remove ../auth-backend
git worktree remove ../auth-frontend
git worktree list
```

Narration: "Worktrees gone. Main branch has all the work. Clean state."

---

## Section 9: Create the Custom Reviewer Sub-Agent

Open .claude/agents/code-reviewer.md` in your editor. Paste:
```bash
    ---
    name: code-reviewer
    description: Review recent code changes for bugs, security issues, missing tests, and CLAUDE.md convention violations. Returns a numbered list of findings with file paths and line numbers.
    tools: Read, Grep, Glob, Bash
    model: inherit
    ---

    # Code Reviewer

    You review the changes made in the current Claude Code session. Your job is to find issues before the user declares the work done.

    ## What to check

    1. **Correctness** — logic errors, broken error handling, missed edge cases.
    2. **Security** — injection risks, leaked secrets, missing auth checks, unvalidated input.
    3. **Tests** — new code paths without corresponding tests; fixture drift.
    4. **Conventions** — violations of CLAUDE.md (naming, layout, error handling style).

    ## Steps

    1. Run `git diff` to see the changes in the working tree.
    2. Read each changed file in full, not just diff context.
    3. Cross-reference CLAUDE.md for project conventions.
    4. For every issue, produce one bullet with: file path, line number, problem, one-line suggested fix.
    5. If there are no issues, reply exactly: `No issues found.`

    ## Output format

    A numbered list. Under 300 words total. Example:

    1. `backend/models.py:47` — `Todo.priority` accepts any string. Add an enum constraint limiting to low/medium/high.
    2. `backend/main.py:89` — `PUT /todos/{id}` doesn't check `Depends(get_current_user)`. Add the dependency.
    3. `frontend/src/components/TodoForm.jsx:23` — Priority select has no default value; React warns. Default to "medium".
```

### Step 2 — Commit it

    git add .claude/agents/code-reviewer.md
    git commit -m "Session 8: add code-reviewer sub-agent"

Narration: "This file is now in the repo. Every tea



---

## Trainer Notes

**If the two agents' prompts are too long for one paste:** paste them as a text file reference. "Open parallel_prompt.md in the project and follow it." Keep the prompt visible so the room can see what's being delegated.

**If one agent finishes much faster than the other:** narrate it. "Backend's done. Frontend is still working. This is why isolation matters — backend is sitting still, not burning my context. When frontend reports, I'll read both together."

**If one agent fails verification:** show it to the room. "Agent reported tests pass, but pytest locally shows one failing. Trust but verify. I'll re-delegate with a narrow prompt." Then fire a one-prompt follow-up with file paths and the specific failure.

**If merges conflict:** almost never happens with clean splits, but if it does, walk through it. "Conflict here — both branches touched main.py. Let me decide which change wins and resolve it." Good teaching moment for why split discipline matters.

**If someone asks 'why not one agent doing everything?':** "Two reasons. Speed — parallel is faster for independent work. Context — each agent's tool stream doesn't pollute the others. One big agent doing everything fills up its context window fast and gets slower."

**If /auth endpoints fail with CORS errors on the frontend:** the backend already has CORS configured from Session 2; if not, narrate and fix on the spot by asking Claude to add CORS middleware.

**If the database needs the User table:** the backend agent should handle the migration, but if the table is missing, ask Claude to run `python -c "from database import Base, engine; Base.metadata.create_all(engine)"`.
