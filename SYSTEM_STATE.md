# CommandHub: System State & Engine Architecture

## 1. System Overview
CommandHub is a sovereign, code-first content production engine. It ingests raw seed text, generates platform-tailored dispatches via the Gemini 2.5 API using strict JSON schemas, renders programmatic visual assets using `node-canvas`, and automatically persists state back to the repository storage vault.

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

## 3. Execution Pipeline & Path Architecture
Execution Trigger: workflow_dispatch (Manual via GitHub Actions UI) or repository_dispatch (signal_capture).

Path Resolution Rules:

Renderer Import: require('../CanvasEngine/canvas_renderer')

Media Output: path.join(__dirname, '..', 'MemoryVault', 'media', imageFilename)

Ledger Output: path.join(__dirname, '..', 'MemoryVault', 'dashboard_feed.json')

## 4. API & JSON Schema Specifications
Gemini API (gemini-3.6-flash) strictly outputs responseMimeType: "application/json" enforced with a strict responseSchema for:

dispatches: Array of platform-specific text dispatches (platform, content).

visual_card: Schema containing meta, styles, and content properties for server-side rendering.
