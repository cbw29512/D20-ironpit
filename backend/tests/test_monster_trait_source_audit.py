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


def test_unknown_outcome_changing_trait_fails_closed() -> None:
    try:
        wolf = _monster("Wolf")
        row = dict(_row("Wolf"))
        row["traits"] = "Magic Resistance. The wolf has Advantage on saving throws against spells and magical effects."
        drifted = wolf.model_copy(update={"source_trait_names": ["Magic Resistance"], "combat_traits": []})
        assert "uncertified-trait:magic-resistance" in trait_issues(drifted, row)
    except Exception:
        logger.exception("Unknown outcome-changing trait fail-closed regression failed.")
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
