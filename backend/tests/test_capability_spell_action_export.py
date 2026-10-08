from __future__ import annotations

from app.content.capability_compiler import compile_combatant
from app.content.monster_capabilities_2014 import load_2014_mvp_definitions
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.sorcerer_draconic_2014_spell_support import magic_missile_2014
from app.content.sorcerer_draconic_2014_spells import fire_bolt_2014
from app.domain.capabilities import CombatantDefinition
from app.domain.combatants import ResourceDefinition
from scripts.browser_template_serializer import template_row


def test_capability_compiler_preserves_spell_attack_and_auto_hit_action_parity() -> None:
    """A source-neutral definition must export both existing spell-action kinds."""
    mage = next(item for item in load_monster_source_2014() if item.name == "Mage")
    source = mage.spellcasting
    assert source is not None and source["source_complete"] is True
    assert {"fire-bolt", "magic-missile"} <= {spell["id"] for spell in source["spells"]}

    # Use a certified base definition to exercise the capability compiler itself.
    # Do not admit the blocked Mage to the arena before its entire spell list is bound.
    base = load_2014_mvp_definitions()["2014-goblin"]
    original = base.model_dump(mode="json")
    assert "spell_attack_actions" not in original
    assert "auto_hit_spell_actions" not in original
    definition = CombatantDefinition.model_validate({
        **original,
        "spell_attack_actions": [
            fire_bolt_2014(source["attack_bonus"], source["caster_level"]).model_dump(mode="json")
        ],
        "auto_hit_spell_actions": [magic_missile_2014().model_dump(mode="json")],
        "resources": [
            ResourceDefinition(id="spell-slot-1", name="Spell Slot 1", max_uses=4).model_dump()
        ],
    })
    template = compile_combatant(definition)
    assert base.model_dump(mode="json") == original
    assert template.spell_attack_actions[0].id == "fire-bolt"
    assert template.spell_attack_actions[0].attack_bonus == 6
    assert template.spell_attack_actions[0].damage_dice_count == 2
    assert template.auto_hit_spell_actions[0].id == "magic-missile"
    assert template.auto_hit_spell_actions[0].projectile_count == 3
    assert [(r.id, r.max_uses) for r in template.resources] == [("spell-slot-1", 4)]

    browser = template_row(template)
    assert browser["spell_attack_actions"][0]["attackBonus"] == 6
    assert browser["spell_attack_actions"][0]["damageDiceCount"] == 2
    assert browser["auto_hit_spell_actions"][0]["projectileCount"] == 3
    assert browser["resources"] == {"spell-slot-1": 4}
