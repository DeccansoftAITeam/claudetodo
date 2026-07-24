**What is MCP?**

**Model Context Protocol (MCP)** is an open protocol that lets AI assistants like Claude securely connect to external tools and data sources. Instead of copying code into chat, Claude can directly read repos, create issues, open PRs, and more — all from inside the terminal.

Claude Code ── MCP ── GitHub MCP Server ── API ── GitHub.com

Three transport types exist:

|  |  |
| --- | --- |
| **Transport** | **When to Use** |
| stdio | Local process on your machine (Docker or binary) |
| http | Remote cloud-hosted server (Recommended) |

**GitHub MCP Server Overview**

GitHub's official MCP server (ghcr.io/github/github-mcp-server) exposes tools across these areas:

* **Repositories** — read files, search code, create/fork repos
* **Issues** — create, list, update, add comments
* **Pull Requests** — create PRs, review diffs, merge
* **Branches** — create, list, delete branches
* **Actions** — trigger workflows, check run status
* **Commits** — get history, compare SHAs

**Prerequisites**

1. **Claude Code installed** — npm install -g @anthropic-ai/claude-code
2. **GitHub Personal Access Token (PAT)**
   * Go to GitHub → Settings → Developer Settings → Personal Access Tokens → Fine-grained
   * Grant: repo, issues, pull\_requests, workflows scopes
   * Copy the token — you only see it once
3. **Docker** (for the local server option)

**Setup GitHub MCP Server -** **Option A — Local Server (Docker / Binary)**

The local server runs as a stdio process on your machine. Claude Code spawns it automatically.

**Method 1: Using the CLI (Recommended)**

# Add the GitHub MCP server locally via Docker

claude mcp add github \

-e GITHUB\_PERSONAL\_ACCESS\_TOKEN=ghp\_YOUR\_TOKEN\_HERE \

-- docker run -i --rm -e GITHUB\_PERSONAL\_ACCESS\_TOKEN ghcr.io/github/github-mcp-server

**Method 2: JSON Configuration (Manual Edit)**

Edit **~/.claude.json** or .**claude/settings.json** and add:

{

"**mcpServers**": {

"github": {

"command": "docker",

"args": [

"run", "-i", "--rm",

"-e", "GITHUB\_PERSONAL\_ACCESS\_TOKEN",

"ghcr.io/github/github-mcp-server"

],

"env": {

"GITHUB\_PERSONAL\_ACCESS\_TOKEN": "ghp\_YOUR\_TOKEN\_HERE"

}

}

}

}

**Method 3: Using the Prebuilt Binary (No Docker) -**

If you built the binary from source:

claude mcp add-json github '{

"command": "github-mcp-server",

"args": ["stdio"],

"env": {

"GITHUB\_PERSONAL\_ACCESS\_TOKEN": "ghp\_YOUR\_TOKEN\_HERE"

}

}'

**Option B — Remote Server (HTTP)**

The remote server is hosted by GitHub at https://api.githubcopilot.com/mcp. No Docker needed — Claude Code connects over HTTP using your PAT as a Bearer token.

**Add via CLI (One-liner)**

claude mcp add --transport http github \

https://api.githubcopilot.com/mcp \

-H "Authorization: Bearer ghp\_YOUR\_TOKEN\_HERE"

**Add via JSON (Explicit format)**

claude mcp add-json github '{

"type": "http",

"url": "https://api.githubcopilot.com/mcp",

"headers": {

"Authorization": "Bearer ghp\_YOUR\_TOKEN\_HERE"

}

}'

**Windows Workaround (if add-json fails)**

claude mcp add --transport http github \

https://api.githubcopilot.com/mcp \

--header "Authorization: Bearer ghp\_YOUR\_TOKEN\_HERE"

**Remote server** is great for: quick setup, no Docker, no binary management, insiders/beta features, and teams sharing a common endpoint.

**Verifying the Connection**

# List all configured MCP servers

claude mcp list

# Get details for GitHub specifically

claude mcp get github

# Inside a Claude Code session, check status

/mcp

You should see github with a checkmark. If it shows pending, wait a moment — Claude Code auto-reconnects with exponential backoff up to 5 attempts.

**Demo Prompts — What You Can Do**

Once connected, try these natural language prompts inside Claude Code:

**Repository Operations**

* List all my public repositories and their star counts.
* Read the README.md from my repo "todo-app" and summarize it.
* Search for files containing "useEffect" in my repo "todo-app".

**Issue Management**

* Create an issue in my repo "todo-app" titled "Add dark mode support"
* with label "enhancement".
* List all open issues in "todo-app" and group them by label.

**Pull Requests**

* Create a new branch called "feature/dark-mode" in my "todo-app" repo,
* then open a draft PR titled "WIP: Dark Mode" targeting main.
* Show me the diff for PR #12 in my "todo-app" repo.

**End-to-End Development Flow**

* Look at issue #5 in my "todo-app" repo, implement the requested feature
* in the current codebase, commit the changes, and open a PR linking to that issue.

**Configuration Scopes Explained**

Claude Code supports three scopes that control where the config is stored:

|  |  |  |  |
| --- | --- | --- | --- |
| **Scope** | **Flag** | **Stored In** | **Shared?** |
| local | *(default)* | .mcp.json in project root | No — your machine only |
| project | --scope project | .mcp.json committed to repo | ✅ Yes — whole team |
| user | --scope user | ~/.claude.json | No — all your projects |

**Playwright Testing — Todo App Demo**

You already have a Todo App in your folder. Here's how to add **Playwright MCP** to Claude Code so Claude can actually open a browser, interact with the app, and validate behavior.

**Step 1: Install Playwright MCP Server**

# Add Playwright MCP to Claude Code

claude mcp add --scope user playwright \

-- npx -y @playwright/mcp@latest

Or in JSON format:

{

"mcpServers": {

"playwright": {

"command": "npx",

"args": ["-y", "@playwright/mcp@latest"]

}

}

}

**Step 2: Install Playwright in Your Todo App**

cd todo-app

npm install -D @playwright/test

npx playwright install chromium

**Step 3: Create a Playwright Test File**

Create tests/todo.spec.ts in your Todo App:

import { test, expect } from '@playwright/test';

test.describe('Todo App', () => {

test.beforeEach(async ({ page }) => {

await page.goto('http://localhost:3000');

});

test('should load the app and show empty state', async ({ page }) => {

await expect(page).toHaveTitle(/Todo/i);

await expect(page.getByText('No todos yet')).toBeVisible();

});

test('should add a new todo item', async ({ page }) => {

const input = page.getByPlaceholder('Add a new todo...');

await input.fill('Buy groceries');

await input.press('Enter');

await expect(page.getByText('Buy groceries')).toBeVisible();

});

test('should mark a todo as complete', async ({ page }) => {

// Add a todo first

const input = page.getByPlaceholder('Add a new todo...');

await input.fill('Complete this task');

await input.press('Enter');

// Click the checkbox to complete it

const checkbox = page.getByRole('checkbox').first();

await checkbox.check();

await expect(checkbox).toBeChecked();

});

test('should delete a todo item', async ({ page }) => {

// Add a todo first

const input = page.getByPlaceholder('Add a new todo...');

await input.fill('Delete me');

await input.press('Enter');

// Hover to reveal delete button, then click

const todoItem = page.getByText('Delete me');

await todoItem.hover();

await page.getByRole('button', { name: /delete/i }).first().click();

await expect(page.getByText('Delete me')).not.toBeVisible();

});

test('should filter todos by status', async ({ page }) => {

// Add two todos

const input = page.getByPlaceholder('Add a new todo...');

await input.fill('Active task');

await input.press('Enter');

await input.fill('Completed task');

await input.press('Enter');

// Complete the second one

const checkboxes = page.getByRole('checkbox');

await checkboxes.nth(1).check();

// Filter by Active

await page.getByRole('button', { name: 'Active' }).click();

await expect(page.getByText('Active task')).toBeVisible();

await expect(page.getByText('Completed task')).not.toBeVisible();

// Filter by Completed

await page.getByRole('button', { name: 'Completed' }).click();

await expect(page.getByText('Completed task')).toBeVisible();

await expect(page.getByText('Active task')).not.toBeVisible();

});

test('should persist todos after page refresh', async ({ page }) => {

const input = page.getByPlaceholder('Add a new todo...');

await input.fill('Persistent task');

await input.press('Enter');

await page.reload();

await expect(page.getByText('Persistent task')).toBeVisible();

});

});

**Step 4: Configure playwright.config.ts**

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({

testDir: './tests',

fullyParallel: true,

forbidOnly: !!process.env.CI,

retries: process.env.CI ? 2 : 0,

reporter: 'html',

use: {

baseURL: 'http://localhost:3000',

trace: 'on-first-retry',

screenshot: 'only-on-failure',

},

projects: [

{

name: 'chromium',

use: { ...devices['Desktop Chrome'] },

},

{

name: 'Mobile Chrome',

use: { ...devices['Pixel 5'] },

},

],

// Automatically start your dev server before running tests

webServer: {

command: 'npm run dev',

url: 'http://localhost:3000',

reuseExistingServer: !process.env.CI,

},

});

**Step 5: Run Tests**

# Run all tests (headless)

npx playwright test

# Run with UI (watch the browser)

npx playwright test --headed

# Run a specific test file

npx playwright test tests/todo.spec.ts

# Open interactive Playwright UI

npx playwright test --ui

# View the HTML report after a run

npx playwright show-report

**Step 6: Let Claude Code Run Playwright via MCP**

With Playwright MCP connected, prompt Claude Code like this:

Start my Todo app dev server, then use Playwright to:

1. Open the app at localhost:3000

2. Add three todos: "Buy milk", "Go for a run", "Read a book"

3. Mark "Go for a run" as complete

4. Filter by "Active" and take a screenshot

5. Tell me if the filter is working correctly

Claude will control the browser in real time, interact with your UI, and report back — no manual testing needed.