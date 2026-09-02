from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any

from app.content.certified_heroes import build_certified_hero_entries
from app.content.hero_catalog import build_hero_catalog
from app.content.hero_progressions import CANONICAL_HEROES
from app.content.monster_catalog import _READY_BY_NAME, build_monster_catalog, load_monster_rows
from app.content.roster import build_arena_roster
from app.domain.catalog import CoverageStatus
from export_browser_heroes import render as render_browser_heroes
from export_browser_monsters import render as render_browser_monsters
from report_zero_engine_monsters import _source_blockers

ROOT = Path(__file__).resolve().parents[1]
HERO_MANIFEST = ROOT / "data" / "hero_certification_manifest.json"
MONSTER_MANIFEST = ROOT / "data" / "monster_certification_manifest.json"
HERO_BROWSER_ARTIFACT = ROOT / "frontend" / "browser-heroes.js"
MONSTER_BROWSER_ARTIFACT = ROOT / "frontend" / "browser-monsters-generated.js"


def _mechanics(template: Any) -> list[str]:
    mechanics = {
        *(f"attack:{item.id}" for item in [template.weapon_attack, *template.alternate_weapon_attacks]),
        *(f"resource:{item.id}" for item in template.resources),
        *(f"trait:{item.value}" for item in template.combat_traits),
        *(f"saving-throw-action:{item.id}" for item in template.saving_throw_actions),
        *(f"spell-save-action:{item.id}" for item in template.spell_save_actions),
        *(f"spell-attack-action:{item.id}" for item in template.spell_attack_actions),
        *(f"defensive-spell-action:{item.id}" for item in template.defensive_spell_actions),
        *(f"healing-action:{item.id}" for item in template.healing_actions),
        *(f"condition-removal-action:{item.id}" for item in template.condition_removal_actions),
    }
    if template.attack_action is not None:
        mechanics.add("multiattack-or-extra-attack")
    features = template.progression_features
    if features.critical_hit_minimum < 20:
        mechanics.add("expanded-critical-range")
    if features.initiative_advantage:
        mechanics.add("initiative-advantage")
    if features.athletics_advantage:
        mechanics.add("athletics-advantage")
    if features.danger_sense:
        mechanics.add("danger-sense")
    if features.reckless_attack:
        mechanics.add("reckless-attack")
    if features.frenzy:
        mechanics.add("frenzy")
    if features.fast_movement_bonus_ft:
        mechanics.add("fast-movement")
    if features.mindless_rage:
        mechanics.add("mindless-rage")
    if features.instinctive_pounce_fraction:
        mechanics.add("instinctive-pounce")
    if features.great_weapon_fighting:
        mechanics.add("great-weapon-fighting")
    if features.indomitable_bonus:
        mechanics.add("indomitable")
    if features.tactical_master_sap_weapon_ids:
        mechanics.add("tactical-master")
    if features.heroic_warrior:
        mechanics.add("heroic-warrior")
    if features.studied_attacks:
        mechanics.add("studied-attacks")
    if features.sneak_attack_d6:
        mechanics.add("sneak-attack")
    if features.critical_move_fraction:
        mechanics.add("post-critical-movement")
    if features.tactical_shift_fraction:
        mechanics.add("tactical-shift")
    return sorted(mechanics)


def _assert_generated_artifact(path: Path, expected: str) -> None:
    if path.read_text(encoding="utf-8") != expected:
        raise RuntimeError(f"Generated browser artifact is stale: {path.relative_to(ROOT)}")


def build_hero_manifest() -> dict[str, Any]:
    _assert_generated_artifact(HERO_BROWSER_ARTIFACT, render_browser_heroes())
    catalog = build_hero_catalog()
    entries = dict(build_certified_hero_entries())
    cards = {(card.class_id, card.level, card.build_id): card for card in catalog}
    heroes: list[dict[str, Any]] = []
    for hero in CANONICAL_HEROES:
        levels: list[dict[str, Any]] = []
        for level in range(1, 21):
            key = (hero.class_id, level, "canonical")
            card = cards[key]
            template = entries.get(key)
            ready = card.coverage_status is CoverageStatus.RAW_READY
            if ready != (template is not None):
                raise RuntimeError(f"Hero catalog/template disagreement for {hero.class_id} level {level}.")
            mechanics = _mechanics(template) if template else []
            blockers = list(card.blockers)
            levels.append({
                "level": level,
                "subclass": ({"id": hero.subclass_id, "name": hero.subclass_name} if level >= 3 else None),
                "runtime_template_id": card.runnable_template_id,
                "source_references": [template.source if template else card.source],
                "expected_combat_features": mechanics,
                "supported_mechanics": mechanics,
                "unsupported_mechanics": blockers,
                "python_certification_status": "certified" if ready else "blocked",
                "browser_certification_status": "certified" if ready else "blocked",
                "generated_static_status": "current" if ready else "not-generated",
                "public_ready_status": "ready" if ready else "blocked",
                "blockers": blockers,
            })
        heroes.append({
            "hero_id": hero.class_id,
            "hero_name": hero.hero_name,
            "class_id": hero.class_id,
            "class_name": hero.class_name,
            "canonical_build_id": "canonical",
            "levels": levels,
        })
    ready_count = sum(level["public_ready_status"] == "ready" for hero in heroes for level in hero["levels"])
    return {
        "schema_version": 1,
        "ruleset": "srd-5.2.1-2024",
        "generation_policy": "Derived from canonical hero catalog, certified runtime entries, and generated browser parity.",
        "summary": {"canonical_heroes": len(heroes), "level_slots": len(catalog), "public_ready": ready_count},
        "heroes": heroes,
    }


def _detected_monster_mechanics(row: dict[str, object], source_blockers: list[str]) -> list[str]:
    actions = str(row.get("actions", ""))
    detected = set(source_blockers)
    if re.search(r"\b(?:Melee|Ranged|Melee or Ranged)\s+Attack Roll:", actions, re.I):
        detected.add("attack-roll")
    if re.search(r"\bMultiattack\b", actions, re.I):
        detected.add("multiattack")
    if re.search(r"\bSaving Throw:", actions, re.I):
        detected.add("saving-throw-action")
    if str(row.get("traits", "")).strip():
        detected.add("trait")
    if str(row.get("bonusActions", "")).strip():
        detected.add("bonus-action")
    if str(row.get("reactions", "")).strip():
        detected.add("reaction")
    if str(row.get("legendaryActions", "")).strip():
        detected.add("legendary")
    if re.search(r"\b(?:Vulnerabilities|Resistances|Immunities)\b", str(row.get("rawText", "")), re.I):
        detected.add("damage-or-condition-defense")
    return sorted(detected)


def build_monster_manifest() -> dict[str, Any]:
    _assert_generated_artifact(MONSTER_BROWSER_ARTIFACT, render_browser_monsters())
    rows = load_monster_rows()
    cards = {card.name: card for card in build_monster_catalog()}
    runtime = {template.id: template for template in build_arena_roster().monsters}
    monster_names = {str(row["name"]) for row in rows}
    monsters: list[dict[str, Any]] = []
    for row in rows:
        name = str(row["name"])
        card = cards[name]
        ready = card.coverage_status is CoverageStatus.RAW_READY
        source_blockers = _source_blockers(row, monster_names)
        blockers = [] if ready else sorted(set([*card.blockers, *source_blockers]))
        detected = _detected_monster_mechanics(row, source_blockers)
        unsupported = [] if ready else sorted(set(source_blockers or card.blockers))
        supported = detected if ready else sorted(set(detected) - set(unsupported))
        runtime_template_id = card.runnable_template_id or _READY_BY_NAME.get(name)
        if runtime_template_id is not None and runtime_template_id not in runtime:
            blockers = sorted(set([*blockers, "missing-runtime-template"]))
        monsters.append({
            "monster_id": str(row["id"]),
            "monster_name": name,
            "srd_source_page": int(row["sourcePage"]),
            "srd_source_reference": str(row["sourceReference"]),
            "runtime_template_id": runtime_template_id,
            "detected_combat_mechanics": detected,
            "supported_mechanics": supported,
            "unsupported_mechanics": unsupported,
            "python_certification_status": "certified" if ready else "blocked",
            "browser_certification_status": "certified" if ready else "blocked",
            "generated_static_status": "current" if ready else "catalog-only",
            "public_ready_status": "ready" if ready else "blocked",
            "blockers": blockers,
        })
    ready_count = sum(row["public_ready_status"] == "ready" for row in monsters)
    return {
        "schema_version": 1,
        "ruleset": "srd-5.2.1-2024",
        "generation_policy": "Derived from canonical SRD rows, runtime/source audit readiness, blocker analysis, and generated browser parity.",
        "summary": {"catalog_monsters": len(monsters), "public_ready": ready_count, "blocked": len(monsters) - ready_count},
        "monsters": monsters,
    }


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _assert_exact_ci_head() -> None:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    expected = os.environ.get("GITHUB_SHA")
    if event_path and Path(event_path).is_file():
        event = json.loads(Path(event_path).read_text(encoding="utf-8"))
        expected = event.get("pull_request", {}).get("head", {}).get("sha") or expected
    if not expected:
        return
    actual = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout.strip()
    if actual != expected:
        raise RuntimeError(f"CI checked out {actual}, but the event requires exact head {expected}.")


def _validate_invariants(hero_manifest: dict[str, Any], monster_manifest: dict[str, Any]) -> None:
    heroes = hero_manifest["heroes"]
    if len(heroes) != 12 or sum(len(hero["levels"]) for hero in heroes) != 240:
        raise RuntimeError("Hero manifest must contain exactly 12 identities and 240 level slots.")
    for hero in heroes:
        if [level["level"] for level in hero["levels"]] != list(range(1, 21)):
            raise RuntimeError(f"Hero {hero['hero_id']} does not expose exactly levels 1-20.")
    monsters = monster_manifest["monsters"]
    if len(monsters) != 330 or len({row["monster_id"] for row in monsters}) != 330:
        raise RuntimeError("Monster manifest must contain exactly 330 unique SRD records.")
    ready_rows = [level for hero in heroes for level in hero["levels"]] + monsters
    for row in ready_rows:
        refs = row.get("source_references", [row.get("srd_source_reference")])
        if row["public_ready_status"] == "ready" and (not refs or not refs[0]):
            raise RuntimeError("Every certified manifest entry must have a source reference.")
    blocker_counts = Counter(blocker for row in monsters for blocker in row["blockers"])
    if monster_manifest["summary"]["blocked"] and not blocker_counts:
        raise RuntimeError("Blocked monsters must expose machine-readable blocker families.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate or verify Iron Pit certification manifests.")
    parser.add_argument("--write", action="store_true", help="Rewrite manifests from authoritative repository state.")
    args = parser.parse_args()
    heroes = build_hero_manifest()
    monsters = build_monster_manifest()
    _validate_invariants(heroes, monsters)
    _assert_exact_ci_head()
    if args.write:
        _write(HERO_MANIFEST, heroes)
        _write(MONSTER_MANIFEST, monsters)
        print("Wrote certification manifests from authoritative repository state.")
        return
    if json.loads(HERO_MANIFEST.read_text(encoding="utf-8")) != heroes:
        raise RuntimeError("Hero certification manifest is stale or hand-edited.")
    if json.loads(MONSTER_MANIFEST.read_text(encoding="utf-8")) != monsters:
        raise RuntimeError("Monster certification manifest is stale or hand-edited.")
    print("Certification manifests match authoritative runtime, source, browser, and catalog state.")


if __name__ == "__main__":
    main()
