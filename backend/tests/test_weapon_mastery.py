from app.combat.state import build_combatant_state
from app.combat.weapon_mastery import weapon_is_mastered, weapon_is_owned, weapon_mastery_active
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.content.equipment import build_greatsword


def _fighter():
    return build_karnok_stoneward().model_copy(deep=True)


def test_2024_mastery_requires_owned_weapon_and_selection() -> None:
    template = _fighter()
    attack = template.weapon_attack
    template.weapon_masteries = [attack.weapon.id]
    state = build_combatant_state(template)

    assert template.ruleset == "2024"
    assert attack.weapon.mastery_property == "Graze"
    assert weapon_is_owned(state, attack) is True
    assert weapon_is_mastered(state, attack) is True
    assert weapon_mastery_active(state, attack, "Graze") is True
    assert weapon_mastery_active(state, attack, "Sap") is False


def test_unselected_owned_weapon_skips_mastery() -> None:
    template = _fighter()
    template.weapon_masteries = []
    state = build_combatant_state(template)

    assert weapon_is_owned(state, template.weapon_attack) is True
    assert weapon_is_mastered(state, template.weapon_attack) is False
    assert weapon_mastery_active(state, template.weapon_attack, "Graze") is False


def test_mastery_selection_cannot_authorize_unowned_weapon() -> None:
    template = _fighter()
    foreign_attack = template.weapon_attack.model_copy(deep=True)
    foreign_attack.weapon = foreign_attack.weapon.model_copy(
        update={"id": "foreign-weapon"},
    )
    template.weapon_masteries = [foreign_attack.weapon.id]
    state = build_combatant_state(template)

    assert weapon_is_owned(state, foreign_attack) is False
    assert weapon_is_mastered(state, foreign_attack) is False
    assert weapon_mastery_active(state, foreign_attack, "Graze") is False


def test_2014_never_activates_2024_weapon_mastery() -> None:
    template = _fighter()
    attack = template.weapon_attack
    template.ruleset = "2014"
    template.weapon_masteries = [attack.weapon.id]
    state = build_combatant_state(template)

    assert weapon_is_owned(state, attack) is True
    assert weapon_is_mastered(state, attack) is False
    assert weapon_mastery_active(state, attack, "Graze") is False


def test_explicit_homebrew_monster_uses_same_mastery_contract_as_pregen() -> None:
    template = build_goblin_warrior().model_copy(deep=True)
    greatsword_attack = template.weapon_attack.model_copy(
        update={"id": "homebrew-greatsword", "weapon": build_greatsword()},
        deep=True,
    )
    template.id = "homebrew-greatsword-brute"
    template.name = "Homebrew Greatsword Brute"
    template.weapon_attack = greatsword_attack
    template.alternate_weapon_attacks = []
    template.weapon_masteries = [greatsword_attack.weapon.id]
    template.ruleset = "2024"
    state = build_combatant_state(template)

    assert template.kind == "monster"
    assert greatsword_attack.weapon.two_handed is True
    assert greatsword_attack.weapon.mastery_property == "Graze"
    assert weapon_is_owned(state, greatsword_attack) is True
    assert weapon_is_mastered(state, greatsword_attack) is True
    assert weapon_mastery_active(state, greatsword_attack, "Graze") is True

    template.weapon_masteries = []
    unmastered_state = build_combatant_state(template)
    assert weapon_is_owned(unmastered_state, greatsword_attack) is True
    assert weapon_is_mastered(unmastered_state, greatsword_attack) is False
    assert weapon_mastery_active(unmastered_state, greatsword_attack, "Graze") is False
