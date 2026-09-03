from __future__ import annotations

WizardSpellChoice = tuple[int, int, str]


WIZARD_SUBCLASS_SPELL_PACKAGES: dict[str, tuple[WizardSpellChoice, ...]] = {
    "evoker": (
        (1, 1, "mage-armor"), (1, 1, "magic-missile"),
        (1, 1, "shield"), (1, 1, "burning-hands"),
        (2, 1, "chromatic-orb"), (3, 2, "scorching-ray"),
        (4, 2, "misty-step"), (5, 3, "fireball"), (5, 3, "counterspell"),
        (6, 3, "fly"), (7, 4, "wall-of-fire"), (8, 4, "dimension-door"),
        (9, 5, "cone-of-cold"), (9, 5, "wall-of-force"),
        (10, 5, "telekinesis"), (11, 6, "chain-lightning"),
        (13, 7, "delayed-blast-fireball"), (14, 7, "forcecage"),
        (15, 8, "incendiary-cloud"), (16, 8, "maze"),
        (16, 8, "power-word-stun"), (17, 9, "meteor-swarm"),
        (18, 9, "wish"), (19, 9, "prismatic-wall"), (20, 9, "time-stop"),
    ),
    "illusionist": (
        (1, 1, "mage-armor"), (1, 1, "shield"),
        (1, 1, "disguise-self"), (1, 1, "silent-image"),
        (2, 1, "sleep"), (3, 2, "invisibility"),
        (4, 2, "mirror-image"), (5, 3, "hypnotic-pattern"), (5, 3, "counterspell"),
        (6, 3, "major-image"), (7, 4, "greater-invisibility"),
        (8, 4, "phantasmal-killer"), (9, 5, "creation"), (9, 5, "seeming"),
        (10, 5, "modify-memory"), (11, 6, "programmed-illusion"),
        (13, 7, "project-image"), (14, 7, "forcecage"),
        (15, 8, "maze"), (16, 8, "mind-blank"),
        (16, 8, "power-word-stun"), (17, 9, "weird"),
        (18, 9, "wish"), (19, 9, "prismatic-wall"), (20, 9, "time-stop"),
    ),
    "abjurer": (
        (1, 1, "mage-armor"), (1, 1, "shield"),
        (1, 1, "protection-from-evil-and-good"), (1, 1, "alarm"),
        (2, 1, "feather-fall"), (3, 2, "arcane-lock"),
        (4, 2, "misty-step"), (5, 3, "counterspell"), (5, 3, "dispel-magic"),
        (6, 3, "protection-from-energy"), (7, 4, "banishment"),
        (8, 4, "stoneskin"), (9, 5, "wall-of-force"), (9, 5, "telekinesis"),
        (10, 5, "hold-monster"), (11, 6, "globe-of-invulnerability"),
        (13, 7, "forcecage"), (14, 7, "plane-shift"),
        (15, 8, "mind-blank"), (16, 8, "maze"),
        (16, 8, "antimagic-field"), (17, 9, "wish"),
        (18, 9, "invulnerability"), (19, 9, "prismatic-wall"), (20, 9, "time-stop"),
    ),
}


def wizard_specialization_spells(subclass_id: str, character_level: int) -> tuple[str, ...]:
    try:
        package = WIZARD_SUBCLASS_SPELL_PACKAGES[subclass_id]
    except KeyError as exc:
        raise ValueError(f"Unknown Wizard spell specialization: {subclass_id}.") from exc
    if not 1 <= character_level <= 20:
        raise ValueError("Character level must be between 1 and 20.")
    return tuple(spell_id for unlock, _, spell_id in package if unlock <= character_level)
