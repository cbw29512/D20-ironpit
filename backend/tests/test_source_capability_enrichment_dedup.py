from types import SimpleNamespace

from app.content.source_capability_enrichment import _merge_attack_effects, _merge_save_actions
from app.domain.capability_effects import ProneEffectDefinition
from app.domain.charge import ChargeProfile
from app.domain.size import CreatureSize


def _save(action_id: str):
    return SimpleNamespace(
        id=action_id,
        name="Constrict",
        action_cost="action",
        resource_id=None,
    )


def test_existing_semantic_save_duplicates_collapse_to_canonical_action() -> None:
    canonical = _save("giant-constrictor-snake-constrict")
    stale_source_copy = _save("srd-giant-constrictor-snake-constrict")
    source = _save("srd-giant-constrictor-snake-constrict")

    merged = _merge_save_actions([canonical, stale_source_copy], [source], {})

    assert [action.id for action in merged] == [canonical.id]


def test_charge_owned_prone_is_not_merged_as_unconditional_attack_rider() -> None:
    profile = ChargeProfile(
        minimum_move_ft=20,
        max_target_size=CreatureSize.MEDIUM,
        prone_max_target_size=CreatureSize.MEDIUM,
    )
    source_effects = [ProneEffectDefinition(max_target_size=CreatureSize.MEDIUM)]

    merged = _merge_attack_effects([], source_effects, charge_profile=profile)

    assert merged == []


def test_non_charge_prone_still_merges_as_normal_attack_rider() -> None:
    source_effect = ProneEffectDefinition(max_target_size=CreatureSize.LARGE)

    merged = _merge_attack_effects([], [source_effect])

    assert merged == [source_effect]
