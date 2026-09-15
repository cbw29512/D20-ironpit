from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.state import build_combatant_state
from app.content.monster_catalog_2014 import monster_by_id_2014
from app.content.monster_catalog_2014_defenses import unresolved_defenses_2014
from app.domain.weapons import DamageType


def _attack_with_flags(attack, *, magical: bool = False, adamantine: bool = False, silvered: bool = False):
    weapon = attack.weapon.model_copy(update={
        "magical": magical,
        "adamantine": adamantine,
        "silvered": silvered,
    })
    return attack.model_copy(update={"weapon": weapon})


def test_flesh_golem_blocks_mundane_physical_weapon_damage() -> None:
    flesh_golem = build_combatant_state(monster_by_id_2014("flesh-golem"))
    veteran = monster_by_id_2014("veteran")
    crossbow = next(
        attack for attack in [veteran.weapon_attack, *veteran.alternate_weapon_attacks]
        if attack.id == "heavy-crossbow"
    )

    assert adjusted_damage_amount(
        10, DamageType.PIERCING, flesh_golem, attack=crossbow
    ) == 0


def test_flesh_golem_immunity_is_bypassed_by_adamantine_or_magical_weapon() -> None:
    flesh_golem = build_combatant_state(monster_by_id_2014("flesh-golem"))
    veteran = monster_by_id_2014("veteran")
    longsword = next(
        attack for attack in [veteran.weapon_attack, *veteran.alternate_weapon_attacks]
        if attack.id == "longsword"
    )

    assert adjusted_damage_amount(
        9, DamageType.SLASHING, flesh_golem,
        attack=_attack_with_flags(longsword, adamantine=True),
    ) == 9
    assert adjusted_damage_amount(
        9, DamageType.SLASHING, flesh_golem,
        attack=_attack_with_flags(longsword, magical=True),
    ) == 9


def test_qualified_physical_defense_does_not_apply_without_weapon_attack_context() -> None:
    flesh_golem = build_combatant_state(monster_by_id_2014("flesh-golem"))

    assert adjusted_damage_amount(
        8, DamageType.BLUDGEONING, flesh_golem, attack=None
    ) == 8


def test_unknown_weapon_qualified_defense_fails_closed() -> None:
    source = next(
        item for item in __import__("app.content.monster_catalog_2014", fromlist=["load_catalog_2014"]).load_catalog_2014()
        if item.id == "flesh-golem"
    )
    copy = source.model_copy(update={
        "unsupported_defense_text": ["piercing from magic weapons wielded by good creatures"],
        "damage_immunities_text": "piercing from magic weapons wielded by good creatures",
    })

    assert unresolved_defenses_2014(copy) == [
        "piercing from magic weapons wielded by good creatures"
    ]