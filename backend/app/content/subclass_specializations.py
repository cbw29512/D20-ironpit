from __future__ import annotations

from app.content.barbarian_subclass_specialization_data import BARBARIAN_SPECIALIZATIONS
from app.content.bard_subclass_specialization_data import BARD_SPECIALIZATIONS
from app.content.fighter_subclass_specialization_data import FIGHTER_SPECIALIZATIONS
from app.content.monk_subclass_specialization_data import MONK_SPECIALIZATIONS
from app.content.paladin_subclass_specialization_data import PALADIN_SPECIALIZATIONS
from app.content.ranger_subclass_specialization_data import RANGER_SPECIALIZATIONS
from app.content.rogue_subclass_specialization_data import ROGUE_SPECIALIZATIONS
from app.content.sorcerer_subclass_specialization_data import SORCERER_SPECIALIZATIONS
from app.content.wizard_subclass_specialization_data import WIZARD_SPECIALIZATIONS
from app.content.warlock_subclass_specialization_data import WARLOCK_SPECIALIZATIONS
from app.content.subclass_specialization_schema import SubclassSpecialization


def _specialization_registry() -> dict[str, SubclassSpecialization]:
    registry: dict[str, SubclassSpecialization] = {}
    for item in (
        *FIGHTER_SPECIALIZATIONS,
        *BARBARIAN_SPECIALIZATIONS,
        *BARD_SPECIALIZATIONS,
        *MONK_SPECIALIZATIONS,
        *PALADIN_SPECIALIZATIONS,
        *RANGER_SPECIALIZATIONS,
        *ROGUE_SPECIALIZATIONS,
        *SORCERER_SPECIALIZATIONS,
        *WIZARD_SPECIALIZATIONS,
        *WARLOCK_SPECIALIZATIONS,
    ):
        if item.subclass_id in registry:
            raise ValueError(f"Duplicate subclass specialization: {item.subclass_id}.")
        registry[item.subclass_id] = item
    return registry


_SPECIALIZATIONS = _specialization_registry()


def subclass_specialization(subclass_id: str) -> SubclassSpecialization:
    try:
        return _SPECIALIZATIONS[subclass_id]
    except KeyError as exc:
        raise ValueError(f"No audited combat specialization for subclass: {subclass_id}.") from exc


def specializations_for_class(class_id: str) -> tuple[SubclassSpecialization, ...]:
    return tuple(item for item in _SPECIALIZATIONS.values() if item.class_id == class_id)
