from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

MANIFEST = Path("data/monsters/2014/source_manifest.json")
OUTPUT = Path("data/monsters/2014/catalog.json")


def _run(command: list[str]) -> int:
    result = subprocess.run(command, check=False)
    return result.returncode


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    with urllib.request.urlopen(manifest["source_raw_url"], timeout=30) as response:
        payload = response.read()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != manifest["sha256"]:
        raise RuntimeError(
            f"2014 source drift: expected {manifest['sha256']}, got {digest}. "
            "Review the source before changing the pinned checksum."
        )
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as handle:
        handle.write(payload)
        source = Path(handle.name)
    try:
        commands = [
            [sys.executable, "scripts/import_2014_monster_catalog.py", str(source), "--output", str(OUTPUT)],
            [sys.executable, "scripts/enrich_2014_save_actions.py", str(source), "--catalog", str(OUTPUT)],
            [sys.executable, "scripts/enrich_2014_breakable_restraints.py", str(source), "--catalog", str(OUTPUT)],
            [sys.executable, "scripts/enrich_2014_healing_actions.py", str(source), "--catalog", str(OUTPUT)],
            [sys.executable, "scripts/enrich_2014_spellcasting.py", str(source), "--catalog", str(OUTPUT)],
        ]
        if any(_run(command) != 0 for command in commands):
            return 1
        catalog = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if len(catalog) != manifest["monster_count"]:
            raise RuntimeError(
                f"2014 catalog count mismatch: expected {manifest['monster_count']}, got {len(catalog)}."
            )
        print(f"verified and normalized {len(catalog)} pinned 2014 monsters")
        return 0
    finally:
        source.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())