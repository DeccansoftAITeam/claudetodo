**About Skills**

# What Are Skills?

* Skills extend what Claude can do. You create a **SKILL.md** file with instructions and Claude adds it to its toolkit.
* Skills solve a very specific problem: **repeated instructions**.
* Claude uses skills **automatically** when relevant, or you can invoke one directly with **/skill-name**.

## Bundled Skills

Claude Code ships with a set of built-in bundled skills available in every session. Unlike fixed built-in commands, bundled skills are prompt-based: they give Claude detailed instructions and let it orchestrate work using its tools.

1. **update-config:** Configure Claude Code via settings.json (hooks, permissions, env vars)
2. **keybindings**-**help**: Helps edit ~/.claude/keybindings.json
3. **simplify —** Review changed code for reuse, quality, efficiency
4. **fewer**-**permission-prompts**: Scans your transcript history, generates an allowlist for repetitive read-only commands.
5. **loop:** Run a prompt/slash command on a recurring interval
6. **schedule:** Create/manage scheduled remote agents (cron-style)
   1. Every weekday at 9am, run a security-review on the main branch and email me the result
7. **claude-api** : Build/debug/optimize Claude API & Anthropic SDK apps
8. **init:** Initialize a new CLAUDE.md with codebase documentation
9. **review:** Review a pull request or current branch

* /review 42: review PR #42 on GitHub before merging
* /review on the current branch to get feedback before opening the PR

1. **security**-**review**: Security review of pending changes on current branch

* After adding a new login endpoint, run /security-review to check for auth/session issues
* Before merging the SQL Server migration branch, run it to catch SQL injection or connection-string leaks

# Where Skills Live

Where you store a skill determines who can use it. When skills share the same name across levels, higher priority wins.

|  |  |  |  |
| --- | --- | --- | --- |
| **Location** | **Path** | **Scope** | **Priority** |
| Enterprise | Managed settings directory | All users in the organisation | 1 (highest) |
| Personal | ~/.claude/skills/<name>/SKILL.md | All your projects | 2 |
| Project | .claude/skills/<name>/SKILL.md | This project only | 3 |

# Skill File Structure

Every skill is a directory named after the command it creates. The directory contains a required SKILL.md file and optional supporting files.

**my-skill**/

**── SKILL.md # Main instructions (required)**

── template.md # Template for Claude to fill in

── examples/

└── sample.md # Example output showing expected format

── scripts/

└── validate.sh # Script Claude can execute

## Live Change Detection:

They takes effect within the current session without restarting.

The one exception: if you create a brand-new top-level skills directory that did not exist when the session started, restart Claude Code so the new directory can be watched.

SKILL.md has two parts:

---

name: my-skill

description: Summarises uncommitted changes and flags risky edits.

Use when the user asks what changed, wants a commit

message, or asks to review their diff.

---

## Current changes

!`git diff HEAD`

## Instructions

Summarise the changes above in two or three bullet points,

then list any risks: missing error handling, hardcoded values,

or tests that need updating. If the diff is empty, say so.

The !`git diff HEAD` line is dynamic context injection: Claude Code runs the command and replaces the line with its output before Claude sees the skill. This grounds Claude's response in your actual working tree rather than guesswork.

## String Substitutions

|  |  |
| --- | --- |
| **Variable** | **Description** |
| $ARGUMENTS | All arguments passed when invoking the skill. Appended as ARGUMENTS: <value> if not present.  /my-skill A1 A2 A3 |
| $ARGUMENTS[N] | Access a specific argument by 0-based index. $ARGUMENTS[0] = first argument. |
| $N | Shorthand for $ARGUMENTS[N]. $0 = first, $1 = second. |
| $nameofarg | Named argument declared in the arguments frontmatter list. Names map to positions in order.  /my-skill n1=A1 |
| ${CLAUDE\_SESSION\_ID} | The current session ID. Useful for logging or session-specific files. |
| ${CLAUDE\_EFFORT} | Current effort level: low, medium, high, xhigh, or max. Adapt instructions to effort setting. |
| ${CLAUDE\_SKILL\_DIR} | Directory containing the skill's SKILL.md. Use to reference scripts bundled with the skill regardless of working directory. |

# Controlling Who Invokes a Skill

By default, both you and Claude can invoke any skill. Two frontmatter fields let you restrict this precisely.

|  |  |  |  |
| --- | --- | --- | --- |
| **Frontmatter setting** | **You can invoke** | **Claude can invoke** | **Description in context** |
| **(default, neither set)** | Yes | Yes | Always in context: Claude always knows about this skill |
| **disable-model-invocation: true** | Yes | No | Not in context: Claude never auto-triggers this skill |
| **user-invocable: false** | No | Yes | Always in context: Claude triggers it, but /name is hidden from menu |

# Passing Arguments to Skills

Both you and Claude can pass arguments when invoking a skill. Arguments substitute into the skill content via placeholders.

SKILL.md: fix-issue (single argument)

---

name: **fix-issue**

description: Fix a GitHub issue by number. Use when the user provides an issue number to fix.

disable-model-invocation: true

---

Fix GitHub issue $ARGUMENTS following our coding standards.

1. Read the issue description with: gh issue view $ARGUMENTS

2. Understand the requirements

3. Implement the fix with tests

4. Create a commit referencing the issue

When you run /fix-issue 123, Claude receives 'Fix GitHub issue 123 following our coding standards...'

**For multiple arguments, use positional access:**

---

name: **migrate-component**

description: Migrate a UI component from one framework to another.

**arguments: [component, from\_framework, to\_framework]**

**argument-hint: [component-name] [from] [to]**

---

Migrate the **$component** component from **$from\_framework** to **$to\_framework**.

Preserve all existing behaviour and tests.

Use $0 as the component name, $1 as source framework, $2 as target.

**Run:**

**/migrate-component** SearchBar React Vue

Replaces $component with SearchBar, $from\_framework with React, $to\_framework with Vue.

# Dynamic Context Injection

The !`<command>` syntax runs shell commands before the skill content is sent to Claude. The command output replaces the placeholder, so Claude receives actual live data, not the command text itself.

**pr-summary**\**SKILL.md:**

---

name: pr-summary

description: Summarise changes in the current pull request.

context: fork

agent: Explore

allowed-tools: Bash(gh \*)

---

## Pull request context

- PR diff: **!`gh pr diff`**

- PR comments: **!`gh pr view --comments`**

- Changed files: **!`gh pr diff --name-only`**

## Your task

Summarise what changed, why, and any risks you spot.

When this skill runs: (1) each !`command` executes immediately before Claude sees anything, (2) the output replaces the placeholder, (3) Claude receives the fully-rendered prompt with live PR data already inlined.

**Demo\SKILL.md**

---

name: demo

description: This skill is used to create file with system time.

---

MSG = The current time is !`echo %time%

## Your task

Create a file by name $ARGUMENTS[0] in root directory of workspace and write to it MSG

**For multi-line commands**, use a fenced code block opened with ```! instead of the inline form:

## Environment

```!

node --version

npm --version

git status --short

```

|  |
| --- |
| This is preprocessing, not something Claude executes. Claude only sees the final rendered result. To disable shell execution for security, set **disableSkillShellExecution: true** in settings. |

# Running Skills in a Subagent

Add context: fork to run the skill in a forked subagent context. The skill runs independently and returns only its result to your main conversation: keeping heavy output out of your main context window.

**SKILL.md**

---

name: **research-topic**

description: Research a technical topic thoroughly.

**context: fork**

**agent: Explore**

---

Research the following topic comprehensively: $ARGUMENTS

1. Search for recent documentation and resources

2. Summarise the key concepts

3. Identify best practices and common pitfalls

4. Return a structured markdown report

Use **context: fork** when the skill produces verbose intermediate output (search results, file listings, log processing) that you do not want accumulating in your main conversation.

# Real-World Skill Examples

## Git Commit Skill (User-only, side-effecting)

---

name: commit

description: Stage all changes and create a conventional commit.

disable-model-invocation: true

allowed-tools: Bash(git add \*) Bash(git commit \*) Bash(git status \*) Bash(git diff \*)

---

Stage and commit the current changes:

1. Run git status to see what has changed

2. Run git diff HEAD to understand the changes

3. Stage all changes: git add .

4. Write a conventional commit message:

- Format: <type>(<scope>): <short summary>

- Types: feat, fix, docs, style, refactor, test, chore

- Keep the summary under 72 characters

5. Commit with: git commit -m '<message>'

6. Show the commit hash and summary

If $ARGUMENTS is provided, use it as additional context for the message.

## PR Review Skill (Parallel subagent, dynamic context)

---

name: review-pr

description: Thorough review of the current PR covering security, logic, and style.

context: fork

agent: Explore

allowed-tools: Bash(gh \*) Read Grep Glob

disable-model-invocation: true

---

## PR data

- Diff: !`gh pr diff`

- Metadata: !`gh pr view`

- Files: !`gh pr diff --name-only`

## Review checklist

Perform a thorough review covering ALL of the following:

### Security

- SQL injection, XSS, IDOR vulnerabilities

- Hardcoded secrets or credentials

- Authentication and authorisation gaps

### Logic

- Edge cases and error handling

- Algorithmic correctness

- Performance implications

### Style

- Naming conventions

- Code duplication

- Missing or inadequate tests

Return a structured report with severity ratings: CRITICAL, HIGH, MEDIUM, LOW.

## 9.3 Deploy Skill (User-only, gated)

---

name: deploy

description: Deploy the application to the target environment.

disable-model-invocation: true

argument-hint: [staging|production]

allowed-tools: Bash

---

Deploy to $ARGUMENTS environment:

1. Confirm environment: must be 'staging' or 'production'

2. Run the full test suite and STOP if any test fails

3. Build the application

4. Run database migrations (dry-run first for production)

5. Push to ${ARGUMENTS} deployment target

6. Run smoke tests against the deployed URL

7. Report success or rollback instructions

Session ID for this deploy: ${CLAUDE\_SESSION\_ID}

## Session Logger Skill (Dynamic session ID)

---

name: start-session

description: Initialise a work session log for tracking what was done.

allowed-tools: Bash(mkdir \*) Bash(echo \*) Bash(date \*)

disable-model-invocation: true

---

Initialise a session log at logs/${CLAUDE\_SESSION\_ID}.log

1. Create the logs/ directory if it does not exist

2. Write a header with current date/time and goal: $ARGUMENTS

3. Confirm the log file path to the user

All subsequent actions in this session should be noted in that file.

# Skills vs Sub-Agents — Detailed Comparison

Skills and subagents are complementary, not competing. Understanding when to use each is one of the most important design decisions you will make when building Claude Code workflows.

## Side-by-Side Comparison

|  |  |  |
| --- | --- | --- |
| **Dimension** | **Skills** | **Sub-Agents** |
| Primary purpose | Package **repeatable instructions**, procedures, and domain knowledge | **Isolate subtasks** into independent agents with their own context |
| Context isolation | No: skill content enters the main context | Yes: full isolation; parent context not visible to subagent |
| Invocation mechanism | /skill-name (command) or automatic when Claude sees the description | Claude decides, or you request by name (natural language) |
| Arguments | Via $ARGUMENTS, $N, or named $var substitution | Via the prompt string passed to the Agent tool |
| Output | Stays in the main conversation thread | Only the final message returns to the parent conversation |
| Tool access | Uses main conversation's tools (or allowed-tools subset) | Has its own configurable tool set: can be more or less than parent |
| Model choice | Can override model per-invocation via model frontmatter field | Has its own model setting via model frontmatter field |
| Persistent memory | No | Yes: via memory: user|project|local frontmatter field |
| Shell preprocessing | Yes: !`command` syntax for dynamic context injection | No: but subagent can run Bash tool calls itself |
| Background running | No | Yes: via background: true frontmatter field |
| Git worktree isolation | No | Yes: via isolation: worktree frontmatter field |
| Open standard | **Yes: Agent Skills (agentskills.io)** | No: Claude Code specific |

## Decision Guide — Which Should You Use?

|  |  |
| --- | --- |
| **Scenario** | **Use** |
| You keep pasting the same instructions into chat | Skill |
| A CLAUDE.md section has become a procedure rather than a fact | Skill |
| You want to create a /deploy or /commit command | Skill (with disable-model-invocation: true) |
| You need background domain knowledge without a user-facing command | Skill (with user-invocable: false) |
| You need live data (git diff, PR details, env info) injected before Claude thinks | Skill (with !`command` injection) |
| A task produces logs or search results that would flood your main context | Sub-Agent (context isolation) |
| You want to run 3 tasks simultaneously (security, logic, style review) | Sub-Agent (parallel fan-out) |
| You need a worker limited to read-only tools (can never write) | Sub-Agent (tool restriction) |
| You need a worker that accumulates knowledge across sessions | Sub-Agent (memory: project) |
| You need a worker to run in an isolated git worktree | Sub-Agent (isolation: worktree) |
| You need a non-blocking background task | Sub-Agent (background: true) |
| You want to run heavy research without polluting the main conversation | Sub-Agent with context: fork, OR Skill with context: fork |

## Using Skills and Sub-Agents Together

The most powerful patterns combine both. Preload domain-knowledge skills into a subagent so it starts with context that would otherwise cost tokens on every invocation.

**SubAgent:**

---

name: security-auditor

description: Expert security auditor. Use for any security review.

tools: Read, Grep, Glob

model: sonnet

**skills:**

- owasp-top-10 # preloads OWASP knowledge skill

- api-conventions # preloads internal API patterns

- security-checklist # preloads project security checklist

---

You are a security auditor specialising in web application security.

Apply the OWASP Top 10 knowledge and project API conventions from your

preloaded skills to every review.

The skills list in a subagent's frontmatter injects the full skill content at startup, rather than waiting for Claude to discover and load it on demand. This is different from how skills work in the main conversation, where only descriptions load unless the skill is invoked.

# Skill Content Lifecycle

Understanding how skill content persists through a session helps you write more effective skills.

|  |  |
| --- | --- |
| **Phase** | **What happens** |
| Session start | Skill descriptions load into context so Claude knows what's available. Full content does not load yet. |
| Invocation | Full SKILL.md content renders (shell commands run, substitutions expand) and enters the conversation as a single message. |
| Rest of session | Content stays in context for the entire session. Claude Code does not re-read the skill file on later turns. |
| Auto-compaction | When context fills, Claude Code re-attaches the most recent invocation of each skill, keeping the first 5,000 tokens per skill. Shared budget of 25,000 tokens across all re-attached skills: older skills may be dropped. |
| After compaction | If a skill seems to stop influencing behaviour, re-invoke it with /skill-name to restore the full content. |

|  |
| --- |
| Write standing instructions rather than one-time steps.  Since skill content stays in context for the whole session, guidance phrased as 'always do X' works better than 'now do X'. |