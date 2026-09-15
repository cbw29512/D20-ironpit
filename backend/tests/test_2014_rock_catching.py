from app.combat.action_economy import is_available
from app.combat.dice import FixedDiceProvider
from app.combat.projectile_catch import resolve_projectile_catch
from app.combat.state import build_combatant_state
from app.content.monster_catalog_2014 import monster_by_id_2014
from app.domain.event_support import DamageRollComponent
from app.domain.weapons import DamageType


def test_stone_giant_rock_catching_uses_reaction_and_negates_bludgeoning_damage() -> None:
    state = build_combatant_state(monster_by_id_2014("stone-giant"))
    profile = state.template.projectile_catch_reaction
    assert profile is not None
    assert profile.save_dc == 10
    attack = state.template.alternate_weapon_attacks[0] if state.template.weapon_attack.weapon.attack_kind.value == "melee" else state.template.weapon_attack
    component = DamageRollComponent(
        source="test rock", notation="2d10+4", rolls=[5, 5], modifier=4,
        damage_type=DamageType.BLUDGEONING, total=14, applied_total=14,
    )
    components, roll, succeeded = resolve_projectile_catch(state, attack, [component], FixedDiceProvider([20]))
    assert succeeded is True
    assert roll is not None and roll.total >= 10
    assert components[0].applied_total == 0
    assert not is_available(state, "reaction")
