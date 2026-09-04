import logging

from app.combat.conditions import attack_roll_condition_sources
from app.content.arena_eligibility import is_flat_standard_arena_eligible
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source

logger = logging.getLogger(__name__)


def _sahuagin():
    try:
        return build_combatant_from_capabilities("srd-sahuagin-warrior")
    except Exception:
        logger.exception("Failed to compile Sahuagin Warrior capability profile.")
        raise


def _source_row() -> dict[str, object]:
    try:
        rows = [row for row in load_monster_rows() if row["name"] == "Sahuagin Warrior"]
        if len(rows) != 1:
            raise ValueError(f"Expected one Sahuagin Warrior source row; found {len(rows)}.")
        return rows[0]
    except Exception:
        logger.exception("Failed to load Sahuagin Warrior SRD source row.")
        raise


def test_sahuagin_profile_is_exact_and_standard_arena_eligible() -> None:
    template = _sahuagin()
    attack = template.weapon_attack
    assert (template.armor_class, template.max_hp, template.speed_ft) == (12, 22, 30)
    assert template.movement_modes.swim_ft == 40
    assert (attack.attack_bonus, attack.weapon.dice_count, attack.weapon.dice_size, attack.damage_bonus) == (3, 1, 6, 1)
    assert template.attack_action is not None
    assert len(template.attack_action.slots) == 2
    assert template.attack_roll_advantage_triggers == ["target_missing_hit_points"]
    assert is_flat_standard_arena_eligible(template) is True


def test_sahuagin_profile_passes_full_srd_source_audit() -> None:
    assert audit_monster_source(_sahuagin(), _source_row()) == []


def test_blood_frenzy_uses_missing_hp_not_bloodied_threshold() -> None:
    attacker = _sahuagin().model_copy(deep=True)
    defender = _sahuagin().model_copy(deep=True)
    from app.domain.models import CombatantState

    attacker_state = CombatantState(template=attacker, current_hp=attacker.max_hp)
    defender_state = CombatantState(template=defender, current_hp=defender.max_hp - 1)
    advantage, disadvantage = attack_roll_condition_sources(attacker_state, defender_state, 5)
    assert (advantage, disadvantage) == (1, 0)
    assert defender_state.current_hp * 2 > defender_state.template.max_hp
