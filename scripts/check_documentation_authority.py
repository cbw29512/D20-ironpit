"""Guard Iron Pit's single documentation authority and local Markdown links.

Historical audits and generated reports are preserved, not rewritten. A new
Markdown file missing from the map is a warning, not a monster-work blocker.
"""
from __future__ import annotations

import logging
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

logger = logging.getLogger(__name__)
MAP = "docs/DOCUMENTATION_MAP.md"
OPERATING = (
    "AGENTS.md",
    "SOUL.md",
    "README.md",
    "docs/CURRENT_OPERATING_STATUS.md",
    "docs/IRON_PIT_IMPLEMENTATION_PLAYBOOK.md",
    "docs/playbooks/MONSTERS.md",
    "docs/playbooks/PREGENS.md",
    "docs/playbooks/UNIVERSAL_ENGINE.md",
    "docs/TWO_AGENT_COORDINATION.md",
    "docs/CONTEXT_TRANSFER_CONTRACT.md",
    ".agents/skills/iron-pit-context-transfer/SKILL.md",
    MAP,
)
OLD_CURSOR = (
    "## Current lane (2026-10-07)",
    "124-monster/305-blocker table",
    "M-015 Brass Dragon Sleep Breath is next",
    "Large 2x2, Huge 3x3, Gargantuan 4x4",
)
ROW = re.compile(r"^\| `([^\x60]+\.md)` \| ([^|]+) \|$", re.MULTILINE)
LINK = re.compile(r"\]\(([^\s)]+)(?:\s+[^)]*)?\)")


def indexed_files(text: str) -> tuple[set[str], list[str]]:
    """Extract map entries, preserving duplicate detection."""
    try:
        rows = [match.group(1) for match in ROW.finditer(text)]
        duplicates = sorted({p for p in rows if rows.count(p) > 1})
        return set(rows), duplicates
    except Exception:
        logger.exception("Cannot parse Markdown ownership index")
        raise


def broken_links(root: Path, source: str, text: str) -> list[str]:
    """Validate only local file/directory links; external URLs are excluded."""
    try:
        base = (root / source).parent
        failures: list[str] = []
        for match in LINK.finditer(text):
            target = unquote(match.group(1).split("#", 1)[0].split("?", 1)[0])
            if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            dest = (base / target).resolve()
            if not dest.is_relative_to(root.resolve()) or not dest.exists():
                failures.append(f"{source}: {match.group(1)}")
        return failures
    except Exception:
        logger.exception("Cannot validate links in %s", source)
        raise


def tracked_markdown(root: Path) -> set[str]:
    """Use tracked paths, not untracked virtualenv or build artifacts."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--", "*.md"],
            cwd=root, capture_output=True, check=True,
        )
        return {item.decode("utf-8") for item in result.stdout.split(b"\0") if item}
    except Exception:
        logger.exception("Cannot read tracked Markdown paths")
        raise


def audit(root: Path, tracked: set[str] | None = None) -> list[str]:
    """Return violations; never modify repository files."""
    try:
        tracked = tracked_markdown(root) if tracked is None else tracked
        map_text = (root / MAP).read_text(encoding="utf-8")
        indexed, duplicates = indexed_files(map_text)
        errors = [f"Duplicate map entry: {p}" for p in duplicates]
        errors += [f"Missing tracked document: {p}" for p in sorted(indexed - tracked)]
        new_docs = sorted(tracked - indexed)
        if new_docs:
            logger.warning("New Markdown files need map classification: %s",
                           ", ".join(new_docs))
        # The source-neutral size override is shared by Python and browser.
        # Prevent historical tabletop footprints from re-entering agent guidance.
        ag = (root / "AGENTS.md").read_text(encoding="utf-8")
        if "every creature size occupies one 5-foot square" not in ag:
            errors.append("Missing one-square Pit footprint invariant in AGENTS.md")
        for path in OPERATING:
            if path not in tracked:
                errors.append(f"Missing operating document: {path}")
                continue
            content = (root / path).read_text(encoding="utf-8")
            errors.extend(broken_links(root, path, content))
            if path != MAP:
                errors.extend(f"Stale execution cursor in {path}: {token}"
                              for token in OLD_CURSOR if token in content)
            headers = re.findall(r"^## .+$", content, re.MULTILINE)
            errors.extend(f"Duplicate heading in {path}: {h}"
                          for h in sorted(set(headers)) if headers.count(h) > 1)
        return errors
    except Exception:
        logger.exception("Documentation authority audit failed")
        raise


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    try:
        root = Path(__file__).resolve().parents[1]
        errors = audit(root)
        if errors:
            for error in errors:
                logger.error("%s", error)
            raise SystemExit(1)
        logger.info("Documentation roles, live links and execution cursors verified")
    except Exception:
        logger.exception("Documentation guard aborted")
        raise


if __name__ == "__main__":
    main()
