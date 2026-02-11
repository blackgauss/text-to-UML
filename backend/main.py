"""CLI entrypoint."""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from backend.utils import DiagramGenerationError, Orchestrator, ProviderError, build_provider
from backend.utils.env import load_dotenv

_ROOT = Path.cwd()


def main() -> None:
    load_dotenv()

    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    if not prompt:
        print("Usage: text-to-uml <description>", file=sys.stderr)
        print('  e.g. text-to-uml "Login system with 2FA"', file=sys.stderr)
        sys.exit(1)

    max_retries = int(os.environ.get("MAX_RETRIES", "3"))
    diagram_type = os.environ.get("DIAGRAM_TYPE", "auto")
    skip_refine = os.environ.get("SKIP_REFINE", "false").lower() in ("true", "1", "yes")

    try:
        provider = build_provider()
        orchestrator = Orchestrator(provider=provider, max_retries=max_retries, skip_refine=skip_refine)
        artifact = orchestrator.run(prompt, diagram_type=diagram_type)
    except (DiagramGenerationError, ProviderError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    out_dir = _ROOT / "outputs"
    out_dir.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    slug = prompt[:40].replace(" ", "_").replace("/", "-")
    out_file = out_dir / f"{timestamp}_{slug}.mmd"
    out_file.write_text(artifact.code + "\n")
    print(f"Saved to {out_file.relative_to(_ROOT)}", file=sys.stderr)

    print(artifact.code)


if __name__ == "__main__":
    main()