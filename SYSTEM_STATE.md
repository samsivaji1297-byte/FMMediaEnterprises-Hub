```markdown
# CommandHub: System State & Engine Architecture

## 1. System Overview
CommandHub is a sovereign, code-first content production engine. It ingests raw seed text, generates platform-tailored dispatches via the Gemini 3.6 Flash API using strict JSON schemas, renders programmatic visual assets using `node-canvas`, and automatically persists state back to the repository storage vault.

## 2. Immutable Directory Structure

```text
/ (FMMediaEnterprises-Hub)
├── .github/
│   └── workflows/
│       └── signal_processor.yml      <-- Automated pipeline execution
├── CanvasEngine/
│   └── canvas_renderer.js            <-- Core HTML5 Canvas programmatic renderer
├── MemoryVault/
│   ├── dashboard_feed.json           <-- Ledger of all processed dispatches
│   └── media/                        <-- Auto-generated PNG visual card assets
├── scripts/
│   ├── package.json                  <-- Node dependencies (canvas, etc.)
│   └── process_signal.js             <-- Pipeline logic & Gemini API handler
└── SYSTEM_STATE.md                   <-- Single source of truth for repository state
```

## 3. Execution Pipeline & Path Architecture

* **Execution Triggers:**
  * `workflow_dispatch` (Manual trigger via GitHub Actions UI)
  * `repository_dispatch` (Automated API event: `signal_capture`)

* **Runtime Directory:** Executed from `./scripts/` with `NODE_PATH=${github.workspace}/scripts/node_modules`

* **Path Resolution Rules:**
  * **Renderer Import:** `require('../CanvasEngine/canvas_renderer')`
  * **Media Output:** `path.join(__dirname, '..', 'MemoryVault', 'media', imageFilename)`
  * **Ledger Output:** `path.join(__dirname, '..', 'MemoryVault', 'dashboard_feed.json')`

## 4. API & JSON Schema Specifications

The Gemini API endpoint (`gemini-3.6-flash`) generates output enforced via `responseMimeType: "application/json"` and a strict `responseSchema` containing:

* **`dispatches`**: Array of platform-tailored text posts containing `platform` and `content`.
* **`visual_card`**: Structured object containing `meta` (dimensions), `styles` (colors), and `content` (badge, headline, body, author, footer) required by the Canvas rendering engine.
```
