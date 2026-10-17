"""Regression: renamed cards still use universal owner-grapple attack policy."""
from app.combat.attack_grapple_auto_hit import owned_grapple_auto_hit
from app.combat.grapple import apply_grapple
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.demo import build_goblin_warrior


def test_renamed_source_card_auto_hit_requires_owner_link() -> None:
    source = next(row for row in load_monster_source_2014() if row.id == "salamander")
    template = compile_combatant(adapt_basic_monster_2014(source))
    attack = next(item for item in [template.weapon_attack, *template.alternate_weapon_attacks]
                  if item.grapple_target_policy == "auto_hit_own_grapple")
    renamed = attack.model_copy(update={"id": "custom-attack"})
    target = build_combatant_state(build_goblin_warrior())
    assert not owned_grapple_auto_hit(renamed, "custom-owner", target)
    apply_grapple(target, "custom-owner", 14, 10, restrains=True)
    assert owned_grapple_auto_hit(renamed, "custom-owner", target)
    assert not owned_grapple_auto_hit(renamed, "different-owner", target)


def test_renamed_redirect_uses_replacement_armor_class() -> None:
    """Resolve a real attack with a synthetic card and distinct target AC."""
    from app.combat.attacks import resolve_attack
    from app.combat.dice import FixedDiceProvider
    from app.content.monster_goblin_boss import build_goblin_boss

    source = next(row for row in load_monster_source_2014() if row.id == "salamander")
    template = compile_combatant(adapt_basic_monster_2014(source))
    attack = next(item for item in [template.weapon_attack, *template.alternate_weapon_attacks]
                  if item.grapple_target_policy == "auto_hit_own_grapple")
    renamed = attack.model_copy(update={"id": "homebrew-grasp"})
    attacker = build_combatant_state(template.model_copy(update={
        "id": "homebrew-owner", "name": "Homebrew Grappler",
    }))
    boss = build_combatant_state(build_goblin_boss())
    replacement = build_combatant_state(
        build_goblin_warrior().model_copy(update={"armor_class": 30}),
    )
    apply_grapple(boss, "homebrew-owner-instance", 14, 10, restrains=True)
    result = resolve_attack(
        1, 1, attacker, boss, renamed, 5, FixedDiceProvider([12]),
        actor_event_id="homebrew-owner-instance", target_event_id="boss",
        redirect_target=replacement, redirect_target_event_id="replacement",
        spend_action=False, affected_states=[boss, replacement],
    )
    assert result.target_id == "replacement"
    assert result.target_ac == 30
    assert result.attack_roll is not None and result.attack_roll.selected_roll == 12
    assert not result.hit
    assert not boss.reaction_available
