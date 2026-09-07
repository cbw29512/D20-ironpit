from app.combat.encounter_setup import build_encounter_setup
from app.combat.saving_throws import legal_save_action
from app.content.monster_catalog import load_monster_rows
from app.content.simple_monster_source_bonus_saves import parse_simple_bonus_save_actions
from app.domain.models import EncounterSelection


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_trample_source_compiles_to_generic_prone_target_requirement() -> None:
    for name, count, size, bonus in (("Elephant", 2, 10, 6), ("Mammoth", 4, 10, 7)):
        action = parse_simple_bonus_save_actions(_row(name))[0]
        assert action["required_target_conditions"] == ["prone"]
        assert action["damage"] == {"count": count, "size": size, "bonus": bonus}
        assert action["success_damage"] == "half"


def test_save_target_condition_requirement_controls_legality() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-constrictor-snake"],
    ))
    hero, snake = setup.heroes[0], setup.monsters[0]
    action = snake.state.template.saving_throw_actions[0].model_copy(update={"required_target_conditions": ["prone"]})
    assert legal_save_action(action, hero, 5) is False
    hero.state.active_effect_ids.append("prone")
    assert legal_save_action(action, hero, 5) is True
