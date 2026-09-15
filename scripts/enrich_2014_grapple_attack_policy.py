from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)
_AUTO_HIT_OWN_GRAPPLE = re.compile(
    r"(?:the\s+)?[A-Za-z' -]+ can automatically hit the target with its [A-Za-z' -]+,\s*"
    r"and (?:the\s+)?[A-Za-z' -]+ can(?:not|'t|’t) make [A-Za-z' -]+ attacks against other targets",
    re.I,
)
_OWN_GRAPPLE_ADVANTAGE = re.compile(
    r"(?:the\s+)?[A-Za-z'’ -]+ has advantage on attack rolls "
    r"(?:to do so|against (?:the|a) (?:target|creature) it is grappling)",
    re.I,
)


def parse_grapple_attack_policy(text: str) -> tuple[str | None, str]:
    try:
        match = _AUTO_HIT_OWN_GRAPPLE.search(text)
        if match is None:
            return None, text
        residual = f"{text[:match.start()]} {text[match.end():]}".strip(" .,;")
        return "auto_hit_own_grapple", residual
    except Exception as exc:
        logger.exception("Failed to parse grapple attack policy: %s", exc)
        raise RuntimeError("Grapple attack policy parsing failed.") from exc


def _bind_own_grapple_only(attack: dict, text: str) -> tuple[bool, str]:
    if not attack.get("forbid_target_grappled_by_self"):
        return False, text
    match = _OWN_GRAPPLE_ADVANTAGE.search(text)
    if match is None:
        return False, text
    attack["forbid_target_grappled_by_self"] = False
    attack["grapple_target_policy"] = "own_grapple_only"
    advantages = attack.setdefault("conditional_attack_advantage", [])
    if not any(item.get("trigger") == "target_grappled_by_self" for item in advantages):
        advantages.append({"trigger": "target_grappled_by_self"})
    residual = f"{text[:match.start()]} {text[match.end():]}".strip(" .,;")
    return True, residual


def main() -> int:
    parser = argparse.ArgumentParser(description="Enrich 2014 grapple-locked attack targeting policies.")
    parser.add_argument("--catalog", type=Path, default=Path("data/monsters/2014/catalog.json"))
    args = parser.parse_args()
    try:
        catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
        parsed = 0
        for monster in catalog:
            for attack in monster.get("attacks", []):
                if attack.get("source_complete", True):
                    continue
                text = attack.get("unsupported_text") or ""
                policy, residual = parse_grapple_attack_policy(text)
                if policy is not None:
                    attack["grapple_target_policy"] = policy
                    parsed += 1
                else:
                    bound, residual = _bind_own_grapple_only(attack, text)
                    if not bound:
                        continue
                    parsed += 1
                attack["unsupported_text"] = residual or None
                attack["source_complete"] = not residual
        args.catalog.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"enriched {parsed} grapple attack policy rider(s)")
        return 0
    except Exception as exc:
        logger.exception("2014 grapple attack policy enrichment failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
