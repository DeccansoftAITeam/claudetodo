# What Are Subagents?

Subagents are specialized AI assistants that Claude Code can delegate specific tasks to. Each subagent runs in its own context window with a custom system prompt, specific tool access, and independent permissions.

Use a subagent when a side task would flood your main conversation with search results, logs, or file contents you will not reference again. The subagent does that work in its own context and returns only the summary.

|  |  |
| --- | --- |
| **Benefit** | **What It Means in Practice** |
| Preserve context | Keep exploration and implementation out of your main conversation so you can run longer sessions without hitting context limits. |
| Enforce constraints | Limit which tools a subagent can use — e.g. a doc-reviewer that can only Read and Grep, never Write. |
| Reuse configurations | Define a subagent once in ~/.claude/agents/ and use it across every project on your machine. |
| Specialise behaviour | Give a subagent a focused system prompt for a specific domain — SQL, security, testing, etc. |
| Control costs | Route lightweight tasks to faster, cheaper models like Claude Haiku instead of Sonnet or Opus. |

**Built-In SubAgents:**

1. Explore
2. Plan
3. General Purpose
4. Statusline
5. Claude Code Guide

# Creating Custom Subagents

Custom subagents are defined as Markdown files with YAML frontmatter. You can create them interactively via the /agents command or by writing files manually.

The /agents command is the recommended way to create and manage subagents.

Run it inside Claude Code:

/agents

This opens a tabbed interface. The Running tab shows live subagents. The Library tab lets you:

* View all available subagents — built-in, user, project, and plugin
* Create new subagents with guided setup or Claude generation
* Edit existing subagent configuration and tool access
* Delete custom subagents
* See which subagents are active when duplicates exist

# Subagent File Structure

Subagent files use YAML frontmatter for configuration, followed by the system prompt in Markdown:

---

**name: code-reviewer**

**description: Reviews code for quality and best practices. Use proactively after code changes.**

**tools: Read, Glob, Grep**

**model: sonnet**

**background: false**

---

You are a code reviewer. When invoked, analyse the code and provide

specific, actionable feedback on quality, security, and best practices.

For each issue found:

- Explain the problem

- Show the current code

- Provide an improved version

Note: Setting **background: true** makes the subagent run as a non-blocking background task.

|  |
| --- |
| Subagents are loaded at session start.  If you create a subagent by manually adding a file, restart your session or use /agents to load it immediately. |

# Invoking Subagents

## Automatic Delegation

Claude **automatically** decides when to invoke subagents based on each subagent's description field. This means the description is one of the most important things you write — make it specific and action-oriented.

# Weak description (Claude may not delegate correctly)

description: Helps with code

# Strong description (Claude delegates precisely when needed)

description: Expert code review specialist. Use proactively after any

code changes to check for security vulnerabilities, performance issues,

and adherence to project coding standards.

## Explicit Invocation

You can also ask Claude to use a specific subagent by name in your prompt:

**USER PROMPT EXAMPLES**

Use the **code-reviewer agent** to review the authentication module

Run the data-scientist agent on sales\_q3.csv and summarise key trends

## Common Patterns

### Isolate high-volume operations

Running tests, fetching documentation, or processing log files can consume significant context. Delegate these to a subagent so the verbose output stays in the subagent's context, and only the relevant summary returns to your main conversation.

**USER PROMPT**

Use a **subagent** to run the full test suite and report only the failing tests with their error messages.

### Run parallel research

For independent investigations, spawn multiple subagents to work simultaneously. Each subagent explores its area independently, then Claude synthesises the findings. This works best when the research paths do not depend on each other.

**USER PROMPT**

Research the authentication, database, and API modules in **parallel** **using separate subagents.**

### Chain subagents sequentially

Each subagent's output becomes the input for the next. Use this when steps have strict dependencies.

**CONCEPTUAL CHAIN**

Step 1: Use the **schema-reader agent** to extract the DB schema

Step 2: Pass that schema to the **migration-writer agent** to produce the migration SQL

Step 3: Pass the SQL to the **validator agent** to check for destructive operations before applying

|  |
| --- |
| Subagents cannot spawn their own subagents. Do not include 'Agent' in a subagent's tools array. |

## Example Subagent Definitions

The following are production-ready subagent definitions adapted from the official Anthropic documentation. Save any of these as .md files in .claude/agents/ or ~/.claude/agents/.

## Code Reviewer

---

name: code-reviewer

description: Reviews code for quality, security, and best practices.

Use proactively after any code changes.

tools: Read, Glob, Grep

model: sonnet

---

You are a code reviewer specialising in quality, security, and best practices.

When reviewing code:

1. Identify security vulnerabilities (OWASP Top 10, injection, auth issues)

2. Check for performance problems (N+1 queries, unnecessary computation)

3. Verify adherence to project coding standards

4. Suggest specific, actionable improvements with examples

For each issue: state the file and line, explain the problem,

show the current code, and provide an improved version.

## Debugger

---

name: debugger

description: Identifies root causes of bugs and test failures.

Use when there are errors, exceptions, or failing tests.

tools: Read, Bash, Grep, Glob

model: sonnet

---

You are a debugging specialist. When given an error or test failure:

1. Reproduce the issue by examining the relevant code and tests

2. Trace the execution path to find the root cause

3. Identify all affected code paths

4. Propose a minimal, targeted fix

5. Suggest a test case that would catch this bug in future

## Database Query Validator

---

name: db-validator

description: Validates SQL queries and migration scripts for safety.

Use before applying any migration to a shared or production database.

tools: Read, Bash

model: sonnet

---

You are a database safety specialist. For each SQL script:

1. Parse and validate syntax

2. Flag destructive operations: DROP TABLE, DROP COLUMN, TRUNCATE

3. Check for missing WHERE clauses on UPDATE/DELETE statements

4. Identify operations that cannot be rolled back

5. Write a corresponding rollback script if possible

6. Return a safety verdict: SAFE, CAUTION, or RISKY with reasons