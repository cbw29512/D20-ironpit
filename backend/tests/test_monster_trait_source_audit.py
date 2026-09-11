from __future__ import annotations

import logging

from app.content.monster_catalog import build_monster_catalog, load_monster_rows
from app.content.monster_trait_source_audit import parse_trait_names, trait_issues
from app.content.roster import build_arena_roster
from app.domain.catalog import CoverageStatus
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)


def _row(name: str) -> dict[str, object]:
    try:
        return next(row for row in load_monster_rows() if row["name"] == name)
    except Exception:
        logger.exception("Failed to load SRD monster row for %r.", name)
        raise


def _monster(name: str):
    try:
        return next(monster for monster in build_arena_roster().monsters if monster.name == name)
    except Exception:
        logger.exception("Failed to load arena monster for %r.", name)
        raise


def test_trait_parser_preserves_multiple_printed_headings() -> None:
    try:
        assert parse_trait_names(
            "Pack Tactics. The wolf has Advantage on attack rolls. Sunlight Sensitivity. While in sunlight, it has Disadvantage."
        ) == ["Pack Tactics", "Sunlight Sensitivity"]
    except Exception:
        logger.exception("Trait-heading parser regression failed.")
        raise


def test_wolf_pack_tactics_is_source_derived_and_runtime_backed() -> None:
    try:
        wolf = _monster("Wolf")
        assert wolf.source_trait_names == ["Pack Tactics"]
        assert CombatTrait.PACK_TACTICS in wolf.combat_traits
        assert trait_issues(wolf, _row("Wolf")) == []
    except Exception:
        logger.exception("Pack Tactics source/runtime parity regression failed.")
        raise


def test_arena_neutral_trait_remains_fingerprinted() -> None:
    try:
        deer = _monster("Deer")
        assert deer.source_trait_names == ["Agile"]
        assert trait_issues(deer, _row("Deer")) == []
    except Exception:
        logger.exception("Arena-neutral trait fingerprint regression failed.")
        raise


def test_environmental_breathing_traits_are_arena_neutral() -> None:
    try:
        wolf = _monster("Wolf")
        for trait_name, description in (
            ("Water Breathing", "The creature can breathe only underwater."),
            ("Limited Amphibiousness", "The creature can breathe air and water for a limited time."),
        ):
            row = {"traits": f"{trait_name}. {description}"}
            synthetic = wolf.model_copy(update={"source_trait_names": [trait_name], "combat_traits": []})
            assert trait_issues(synthetic, row) == []
    except Exception:
        logger.exception("Environmental breathing trait neutrality regression failed.")
        raise


def test_information_only_traits_do_not_block_combat_certification() -> None:
    try:
        wolf = _monster("Wolf")
        for trait_name, description in (
            ("Divine Awareness", "The creature knows if it hears a lie."),
            (
                "Inscrutable",
                "No magic can observe the creature remotely or detect its thoughts without permission.",
            ),
        ):
            row = {"traits": f"{trait_name}. {description}"}
            synthetic = wolf.model_copy(update={"source_trait_names": [trait_name], "combat_traits": []})
            assert trait_issues(synthetic, row) == []
            assert synthetic.source_trait_names == [trait_name]
    except Exception:
        logger.exception("Information-only trait neutrality regression failed.")
        raise


def test_real_srd_information_traits_are_fingerprinted_without_trait_blockers() -> None:
    try:
        for monster_name, trait_slug in (
            ("Planetar", "divine-awareness"),
            ("Solar", "divine-awareness"),
            ("Sphinx of Lore", "inscrutable"),
            ("Sphinx of Valor", "inscrutable"),
        ):
            issues = trait_issues(_monster(monster_name), _row(monster_name))
            assert f"uncertified-trait:{trait_slug}" not in issues
    except Exception:
        logger.exception("Real SRD information-only trait regression failed.")
        raise


def test_sunlight_sensitivity_is_inactive_without_explicit_sunlight() -> None:
    try:
        wolf = _monster("Wolf")
        row = {
            "traits": (
                "Sunlight Sensitivity. While in sunlight, the creature has Disadvantage on attack rolls."
            )
        }
        synthetic = wolf.model_copy(
            update={"source_trait_names": ["Sunlight Sensitivity"], "combat_traits": []}
        )
        assert trait_issues(synthetic, row) == []
        assert synthetic.source_trait_names == ["Sunlight Sensitivity"]
    except Exception:
        logger.exception("Default no-sunlight certification regression failed.")
        raise


def test_shadow_open_arena_traits_are_source_fingerprinted_but_inactive() -> None:
    try:
        shadow = _monster("Shadow")
        assert shadow.source_trait_names == ["Amorphous", "Sunlight Weakness"]
        assert trait_issues(shadow, _row("Shadow")) == []
    except Exception:
        logger.exception("Shadow arena-neutral trait regression failed.")
        raise


def test_recognized_magic_resistance_trait_fails_closed_without_runtime_support() -> None:
    try:
        wolf = _monster("Wolf")
        row = dict(_row("Wolf"))
        row["traits"] = "Magic Resistance. The wolf has Advantage on saving throws against spells and magical effects."
        drifted = wolf.model_copy(
            update={"source_trait_names": ["Magic Resistance"], "combat_traits": [], "magic_resistance": False}
        )
        assert "trait-runtime-missing:magic-resistance" in trait_issues(drifted, row)
    except Exception:
        logger.exception("Magic Resistance runtime fail-closed regression failed.")
        raise


def test_catalog_blocks_missing_runtime_pack_tactics(monkeypatch) -> None:
    try:
        roster = build_arena_roster()
        monsters = [
            monster.model_copy(update={"combat_traits": []}) if monster.name == "Wolf" else monster
            for monster in roster.monsters
        ]
        monkeypatch.setattr(
            "app.content.roster.build_arena_roster",
            lambda: roster.model_copy(update={"monsters": monsters}),
        )
        card = next(item for item in build_monster_catalog() if item.name == "Wolf")
        assert card.coverage_status is CoverageStatus.BLOCKED
        assert card.runnable_template_id is None
        assert "trait-runtime-missing:pack-tactics" in card.blockers
    except Exception:
        logger.exception("Missing runtime Pack Tactics fail-closed regression failed.")
        raise
