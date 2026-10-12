"""2014 Black Pudding: one hit, two typed components, no unsupported gear mutation."""
from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_attack_compiler import compile_attack
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import _attack
from app.content.monster_mixed_damage_2014 import source_completed_mixed_attack_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.weapons_base import DamageType


def _printed():
    monster = next(row for row in load_monster_source_2014() if row.id == "black-pudding")
    return monster, next(row for row in monster.attacks if row.name.lower() == "pseudopod")


def test_both_printed_types_are_admitted_without_changing_source():
    monster, attack = _printed()
    before = monster.model_dump_json()
    corrected = source_completed_mixed_attack_2014(monster, attack)
    assert corrected.source_complete, (attack.model_dump(), monster.source_actions)
    assert corrected.damage.model_dump() == {
        "average": 6, "dice_count": 1, "dice_size": 6, "bonus": 3,
        "type": "bludgeoning",
    }
    assert corrected.on_hit_damage == [{
        "average": 18, "dice_count": 4, "dice_size": 8, "bonus": 0, "type": "acid",
    }]
    runtime = compile_attack(_attack(monster, attack))
    assert runtime.attack_bonus == 5
    assert runtime.weapon.reach_ft == 5
    assert runtime.weapon.damage_type == DamageType.BLUDGEONING
    assert [(r.dice_count, r.dice_size, r.damage_type)
            for r in runtime.on_hit_damage] == [(4, 8, DamageType.ACID)]
    assert not basic_blockers_2014(monster)
    assert monster.model_dump_json() == before


def test_proof_fails_closed_when_any_printed_component_is_missing():
    monster, attack = _printed()
    for text in (
        (monster.source_actions or "").replace("4d8", "9d9"),
        (monster.source_actions or "").replace("nonmagical armor", "magical armor"),
    ):
        changed = monster.model_copy(update={"source_actions": text})
        assert source_completed_mixed_attack_2014(changed, attack) == attack
        assert "attack:incomplete" in basic_blockers_2014(changed)


def test_distinct_damage_type_defenses_apply_independently():
    monster, source_attack = _printed()
    weapon = compile_attack(_attack(monster, source_attack))
    attacker = build_combatant_state(build_commoner())
    victim_template = build_commoner().model_copy(update={
        "max_hp": 100, "damage_immunities": [DamageType.ACID],
    })
    victim = build_combatant_state(victim_template)
    hit = resolve_attack(
        1, 1, attacker, victim, weapon, 10,
        FixedDiceProvider([18, 4, 8, 8, 8, 8]), spend_action=False,
    )
    assert hit.hit
    parts = {str(part.damage_type): part for part in hit.damage_components}
    assert "bludgeoning" in parts and "acid" in parts
    assert parts["acid"].applied_total == 0
    assert parts["bludgeoning"].applied_total > 0
    assert victim.current_hp == 100 - parts["bludgeoning"].applied_total
    assert not victim.active_modifiers  # no unproven nonmagical worn armor
