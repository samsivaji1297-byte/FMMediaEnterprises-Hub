# CommandHub: System State & Engine Architecture

## 1. System Overview
CommandHub is a sovereign, code-first content production engine. It ingests raw seed text, generates platform-tailored dispatches via the Gemini 2.5 API using strict JSON schemas, renders programmatic visual assets using `node-canvas`, and automatically persists state back to the repository storage vault.

## 2. Immutable Directory Structure

```text
/ (Repo Root)
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
