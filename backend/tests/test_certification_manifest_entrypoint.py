from __future__ import annotations

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "verify_certification_manifests.py"


def test_certification_manifest_script_executes_its_cli_entrypoint() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (
        "Certification manifests match authoritative runtime, source, browser, and catalog state."
        in result.stdout
    )
