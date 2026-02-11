# text-to-UML

CLI tool that converts natural-language descriptions into valid Mermaid.js diagrams. An LLM generates the diagram, `mmdc` compiles it, and a repair loop fixes syntax errors automatically. Configure the provider, model, through environment variables in `.env`.

## Quick start

```bash
cp .env.example .env   # add your API key
./start.sh
```

Checks for dependencies (`python3 ≥ 3.12`, `uv`, `node`/`npm`), installs anything missing (with your permission), syncs backend & frontend packages, and starts both servers.

Backend on `http://localhost:8000`, frontend on `http://localhost:5173`.

## Manual start

```bash
uv run text-to-uml-api          # terminal 1 — backend on :8000
cd frontend && npm run dev       # terminal 2 — frontend on :5173
```