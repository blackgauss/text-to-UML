"""CLI entrypoint."""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from text_to_uml.utils import DiagramGenerationError, Orchestrator, ProviderError, build_provider

_ROOT = Path(__file__).resolve().parents[2]


def _load_dotenv() -> None:
    env_path = _ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def main() -> None:
    _load_dotenv()

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