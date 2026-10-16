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
