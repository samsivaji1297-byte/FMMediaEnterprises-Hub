name: Test Groq Niche Engine

on:
  workflow_dispatch: # Enables manual trigger button in GitHub browser UI

jobs:
  run-groq-test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Install Dependencies
        run: pip install groq

      - name: Execute Groq Niche Engine
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: python test_groq_niche.py
