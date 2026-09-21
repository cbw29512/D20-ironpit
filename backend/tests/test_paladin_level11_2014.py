from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.paladin_devotion_2014_combat_profile import build_aurelia_brightshield_2014_combat_profile
from app.content.paladin_devotion_2014_profile import build_aurelia_brightshield_2014_profile
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.domain.models import RollMode


def test_paladin_level_11_certifies_improved_divine_smite_data() -> None:
    profile = build_aurelia_brightshield_2014_profile(11)
    runtime = build_aurelia_brightshield_2014(11)
    fingerprint = build_aurelia_brightshield_2014_combat_profile(11)

    assert runtime.id == "aurelia-brightshield-2014-l11"
    assert profile.template_id == runtime.id
    assert_pregen_combat_stats(runtime, fingerprint)
    assert_character_resources_raw_ready(runtime, profile, fingerprint)
    assert {item.id: item.max_uses for item in runtime.resources}["spell-slot-3"] == 3

    for attack in [runtime.weapon_attack, *runtime.alternate_weapon_attacks]:
        assert len(attack.on_hit_damage) == 1
        rider = attack.on_hit_damage[0]
        assert (rider.source, rider.dice_count, rider.dice_size, rider.damage_type.value) == (
            "Improved Divine Smite", 1, 8, "radiant",
        )


def test_improved_divine_smite_rolls_and_critically_doubles_without_spending_a_resource() -> None:
    state = build_combatant_state(build_aurelia_brightshield_2014(11))
    before = {item.id: item.current_uses for item in state.resources}

    _, components = resolve_weapon_damage(
        state, state.template.alternate_weapon_attacks[0],
        FixedDiceProvider([4, 7]), False, RollMode.NORMAL, "1:aurelia",
    )
    rider = next(item for item in components if item.source == "Improved Divine Smite")
    assert rider.notation == "1d8+0"
    assert {item.id: item.current_uses for item in state.resources} == before

    _, critical_components = resolve_weapon_damage(
        state, state.template.alternate_weapon_attacks[0],
        FixedDiceProvider([4, 7, 8]), True, RollMode.NORMAL, "1:aurelia-crit",
    )
    critical_rider = next(item for item in critical_components if item.source == "Improved Divine Smite")
    assert critical_rider.notation == "2d8+0"
