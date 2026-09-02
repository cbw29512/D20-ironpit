from app.combat.state import build_combatant_state
from app.combat.weapon_mastery import weapon_is_mastered, weapon_mastery_active
from app.content.audited_fighter import build_karnok_stoneward


def test_mastery_requires_both_weapon_property_and_combatant_selection() -> None:
    template = build_karnok_stoneward().model_copy(deep=True)
    attack = template.weapon_attack
    template.weapon_masteries = [attack.weapon.id]
    state = build_combatant_state(template)

    assert attack.weapon.mastery_property == "Graze"
    assert weapon_is_mastered(state, attack) is True
    assert weapon_mastery_active(state, attack, "Graze") is True
    assert weapon_mastery_active(state, attack, "Sap") is False


def test_unselected_weapon_skips_its_mastery() -> None:
    template = build_karnok_stoneward().model_copy(deep=True)
    template.weapon_masteries = []
    state = build_combatant_state(template)

    assert weapon_is_mastered(state, template.weapon_attack) is False
    assert weapon_mastery_active(state, template.weapon_attack, "Graze") is False
