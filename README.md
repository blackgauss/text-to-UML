# text-to-UML

CLI tool that converts natural-language descriptions into valid Mermaid.js diagrams. An LLM generates the diagram, `mmdc` compiles it, and a repair loop fixes syntax errors automatically. Configure the provider, model, and pipeline behaviour through environment variables in `.env`.