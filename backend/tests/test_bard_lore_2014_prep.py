from app.content.bard_lore_2014_combat_profile import build_lyra_silverstring_2014_combat_profile
from app.content.bard_lore_2014_data import CANTRIPS_KNOWN, SPELLS_KNOWN, SPELL_SLOTS, ability_scores, bardic_inspiration_die
from app.content.bard_lore_2014_profile import build_lyra_silverstring_2014_profile
from app.content.bard_lore_2014_runtime import build_lyra_silverstring_2014
from app.content.certified_hero_progressions import CERTIFIED_HERO_PROGRESSIONS


def test_2014_lore_bard_source_progression_covers_levels_one_through_twenty() -> None:
    assert tuple(SPELL_SLOTS) == tuple(range(1, 21))
    assert len(SPELLS_KNOWN) == 20
    assert len(CANTRIPS_KNOWN) == 20
    assert SPELL_SLOTS[1] == (2,)
    assert SPELL_SLOTS[10] == (4, 3, 3, 3, 2)
    assert SPELL_SLOTS[20] == (4, 3, 3, 3, 3, 2, 2, 1, 1)
    assert SPELLS_KNOWN[0] == 4
    assert SPELLS_KNOWN[19] == 22
    assert CANTRIPS_KNOWN[0] == 2
    assert CANTRIPS_KNOWN[9] == 4
    assert bardic_inspiration_die(1) == 6
    assert bardic_inspiration_die(5) == 8
    assert bardic_inspiration_die(10) == 10
    assert bardic_inspiration_die(15) == 12


def test_lyra_persistent_identity_and_asi_choices_are_stable_through_twenty() -> None:
    first = build_lyra_silverstring_2014_profile(1)
    prior_advancements = 0
    for level in range(1, 21):
        profile = build_lyra_silverstring_2014_profile(level)
        runtime = build_lyra_silverstring_2014(level)
        fingerprint = build_lyra_silverstring_2014_combat_profile(level)

        assert profile.character_name == first.character_name == "Lyra Silverstring"
        assert profile.species_id == first.species_id == "half-elf"
        assert profile.background_id == first.background_id == "noble"
        assert profile.class_equipment == first.class_equipment
        assert profile.template_id == runtime.id == fingerprint.template_id
        assert profile.level == runtime.level == fingerprint.level == level
        assert len(profile.advancement_increases) >= prior_advancements
        prior_advancements = len(profile.advancement_increases)

    assert ability_scores(1).charisma == 17
    assert ability_scores(4).charisma == 19
    assert ability_scores(8).charisma == 20
    assert ability_scores(12).dexterity == 18
    assert ability_scores(16).constitution == 16
    assert ability_scores(19).dexterity == 20


def test_lyra_runtime_resources_and_static_combat_math_match_fingerprint() -> None:
    for level in (1, 2, 3, 5, 10, 15, 20):
        runtime = build_lyra_silverstring_2014(level)
        fingerprint = build_lyra_silverstring_2014_combat_profile(level)
        runtime_resources = {item.id: item.max_uses for item in runtime.resources}

        assert runtime.armor_class == fingerprint.armor_class
        assert runtime.max_hp == fingerprint.max_hp
        assert runtime.initiative_bonus == fingerprint.initiative_bonus
        assert runtime_resources == dict(fingerprint.resources)
        assert runtime_resources["bardic-inspiration"] == max(
            1, runtime.ability_scores.modifier("charisma")
        )
        slots = tuple(
            runtime_resources[f"spell-slot-{spell_level}"]
            for spell_level in range(1, len(SPELL_SLOTS[level]) + 1)
        )
        assert slots == SPELL_SLOTS[level]


def test_fey_ancestry_and_superior_inspiration_bind_to_existing_generic_primitives() -> None:
    first = build_lyra_silverstring_2014(1)
    grants = first.progression_features.saving_throw_advantage_grants
    assert len(grants) == 1
    assert grants[0].source_name == "Fey Ancestry"
    assert grants[0].against_effect_tags == ["charmed"]

    nineteen = build_lyra_silverstring_2014(19)
    twenty = build_lyra_silverstring_2014(20)
    assert nineteen.initiative_resource_refill_grants == []
    assert len(twenty.initiative_resource_refill_grants) == 1
    refill = twenty.initiative_resource_refill_grants[0]
    assert refill.source_name == "Superior Inspiration"
    assert refill.resource_id == "bardic-inspiration"
    assert refill.when_at_or_below == 0
    assert refill.restore_amount == 1


def test_lore_bard_preparation_does_not_claim_certification() -> None:
    assert all(
        not (
            item.class_id == "bard"
            and getattr(item.template_builder, "__name__", "") == "build_lyra_silverstring_2014"
        )
        for item in CERTIFIED_HERO_PROGRESSIONS
    )
    level_three = build_lyra_silverstring_2014_profile(3)
    cutting = next(item for item in level_three.feature_audits if item.feature_id == "cutting-words")
    inspiration = next(item for item in level_three.feature_audits if item.feature_id == "bardic-inspiration")
    assert cutting.automated is False
    assert inspiration.automated is False


def test_peerless_skill_reuses_generic_failed_d20_bonus_die_grant() -> None:
    thirteen = build_lyra_silverstring_2014(13)
    fourteen = build_lyra_silverstring_2014(14)
    assert thirteen.progression_features.failed_d20_bonus_die_grants == []

    grants = fourteen.progression_features.failed_d20_bonus_die_grants
    assert len(grants) == 1
    grant = grants[0]
    assert grant.source_id == "peerless-skill"
    assert grant.source_name == "Peerless Skill"
    assert grant.resource_id == "bardic-inspiration"
    assert grant.resource_cost == 1
    assert grant.dice_size == bardic_inspiration_die(14)
    assert grant.test_kinds == ["ability_check"]

    audit = next(
        item for item in build_lyra_silverstring_2014_profile(14).feature_audits
        if item.feature_id == "peerless-skill"
    )
    assert audit.automated is True
