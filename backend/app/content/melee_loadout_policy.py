from __future__ import annotations

from app.domain.class_loadouts import MeleeLoadoutSelection


def choose_melee_loadout(
    strength: int,
    dexterity: int,
    *,
    shield_trained: bool,
    power_build: bool = False,
    dual_wield_trained: bool = True,
) -> MeleeLoadoutSelection:
    """Choose one repeatable melee package from the build's physical emphasis."""
    if not 1 <= strength <= 30 or not 1 <= dexterity <= 30:
        raise ValueError("Strength and Dexterity must be between 1 and 30.")

    if dexterity > strength and dual_wield_trained:
        return MeleeLoadoutSelection(kind="dual-wield", primary_ability="dexterity")
    if power_build:
        return MeleeLoadoutSelection(kind="two-handed", primary_ability="strength")
    if shield_trained:
        return MeleeLoadoutSelection(kind="one-hander-shield", primary_ability="strength")
    return MeleeLoadoutSelection(kind="two-handed", primary_ability="strength")
