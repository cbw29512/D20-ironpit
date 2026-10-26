"""Generate the 327-card staged-disease coverage report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))
DEFAULT_OUTPUT = ROOT / "docs" / "generated" / "STAGED_DISEASE_BINDINGS_2014.json"

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_staged_disease_2014 import staged_disease_candidates_2014
from app.content.monster_source_staged_disease_2014 import source_bound_staged_disease_2014
from app.content.monster_source_staged_disease_2014 import source_proven_arena_neutral_periodic_2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.content.monster_mixed_damage_2014 import source_completed_mixed_attack_2014
from app.content.monster_basic_attack_effects_2014 import basic_attack_effects_2014
from app.content.capability_attack_compiler import compile_attack
from app.domain.capabilities import AttackCapabilityDefinition
from app.domain.capability_effects import DiceSpec, SavePersistentEffectDefinition
from scripts.browser_on_hit_condition_serializer import serialize_on_hit_condition_save


def _has_bound_transition(card) -> bool:
    for attack in card.attacks:
        effect = source_bound_staged_disease_2014(card, attack).on_hit_save_effect
        if isinstance(effect, dict) and "delayed_transition" in effect:
            return True
    return False



def _compiled_paths(card) -> tuple[bool, bool]:
    """Prove genuine Python capability compilation and browser serialization."""
    for original in card.attacks:
        attack = source_completed_mixed_attack_2014(card, original)
        if not attack.source_complete or not isinstance(attack.on_hit_save_effect, dict):
            continue
        if "delayed_transition" not in attack.on_hit_save_effect:
            continue
        effects = basic_attack_effects_2014(attack)
        if not any(isinstance(item, SavePersistentEffectDefinition) for item in effects):
            continue
        definition = AttackCapabilityDefinition(
            id=attack.id, name=attack.name, attack_kind=attack.kind,
            attack_bonus=attack.attack_bonus,
            damage=DiceSpec(
                count=attack.damage.dice_count, size=attack.damage.dice_size,
                bonus=attack.damage.bonus,
            ),
            damage_type=attack.damage.type, animation="slash",
            reach_ft=attack.reach_ft, effects=effects,
        )
        compiled = compile_attack(definition)
        if compiled.on_hit_condition_save is None:
            return False, False
        row = serialize_on_hit_condition_save(compiled.on_hit_condition_save)
        return True, row.get("delayedTransition", {}).get("targetTurns") == (
            attack.on_hit_save_effect["delayed_transition"]["target_turns"]
        )
    return False, False


def report() -> dict:
    cards = load_monster_source_2014()
    candidates = staged_disease_candidates_2014(cards)
    applicable = [card.id for card in candidates]
    stage_wired = [card.id for card in cards if _has_bound_transition(card)]
    wired_python, wired_browser, exceptions, neutral = [], [], [], []
    for card in candidates:
        py, js = _compiled_paths(card)
        if py:
            wired_python.append(card.id)
        if js:
            wired_browser.append(card.id)
        if not (py and js):
            exceptions.append({
                "monster": card.id,
                "reason": "Source-proof or Python/browser staged-disease integration incomplete",
            })
        for attack in card.attacks:
            section = source_sections_2014(
                card.source_actions, include_continuations=True,
            ).get(attack.name, "")
            proof = source_proven_arena_neutral_periodic_2014(section)
            if proof is not None and source_bound_staged_disease_2014(
                card, attack,
            ).source_complete:
                neutral.append({"monster": card.id, **proof})
    complete = sorted(set(wired_python) & set(wired_browser))
    return {
        "source_cards_scanned": len(cards),
        "applicable_card_count": len(applicable),
        "applicable_cards": applicable,
        "removal_contract_card_count": len(applicable),
        "latent_activation_contract_card_count": len(stage_wired),
        "stage_wired_python_card_count": len(stage_wired),
        "stage_wired_browser_card_count": len(stage_wired),
        "stage_wired_cards": stage_wired,
        "wired_python_card_count": len(wired_python),
        "wired_browser_card_count": len(wired_browser),
        "wired_cards": complete,
        "arena_neutral_periodic_component_count": len(neutral),
        "arena_neutral_periodic_components": neutral,
        "remaining_card_count": len(exceptions),
        "exceptions": exceptions,
        "status": "complete" if not exceptions else "partial: source integration incomplete",
    }


def render() -> str:
    return json.dumps(report(), indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    rendered = render()
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"{args.output} is stale; regenerate with this script.")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()

