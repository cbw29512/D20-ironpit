"""Source-neutral no-HP-regain effects cannot be selected for pooled healing."""
import logging

from app.combat.cleric_channel_policy import choose_channel_divinity
from app.combat.cleric_preserve_life import preserve_life_targets
from app.combat.encounter_setup import build_encounter_setup
from app.combat.pooled_healing import pooled_healing_capacity
from app.combat.timed_conditions import apply_timed_condition
from app.combat.timed_condition_lifecycle import remove_effect_instance
from app.domain.encounters import EncounterSelection

logger = logging.getLogger(__name__)


def test_2014_cleric_cannot_waste_preserve_life_on_healing_block():
    try:
        setup = build_encounter_setup(EncounterSelection(
            ruleset="2014",
            hero_ids=["seraphine-dawnshield-2014-l3"],
            monster_ids=["2014-mummy"],
        ))
        cleric = setup.heroes[0]
        state = cleric.state
        state.current_hp = min(state.current_hp, 1)
        source_snapshot = state.template.model_dump_json()
        assert pooled_healing_capacity(cleric, 1, 2) > 0
        applied = apply_timed_condition(
            state, "poisoned", setup.monsters[0].combatant_id,
            source_effect_id="renamed-no-recovery-effect",
            cannot_regain_hit_points=True,
            expires_at_start_of_source_turn=False,
            use_default_poison_recovery=False,
        )
        assert applied is not None
        assert pooled_healing_capacity(cleric, 1, 2) == 0
        assert not preserve_life_targets(cleric, setup)
        choice = choose_channel_divinity(cleric, setup)
        assert choice is None or choice.kind != "preserve-life"
        remove_effect_instance(state, state.timed_effects[0])
        assert pooled_healing_capacity(cleric, 1, 2) > 0
        assert state.template.model_dump_json() == source_snapshot
    except Exception:
        logger.exception("2014 no-recovery pooled-healing selection regression")
        raise
