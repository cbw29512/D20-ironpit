from __future__ import annotations

import logging

from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def _audit(
    feature_id: str,
    feature_name: str,
    category: str,
    *,
    combat: bool,
    automated: bool,
    weapon_id: str | None = None,
    notes: str | None = None,
) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=feature_name,
        source_reference="D&D Beyond Basic Rules 2024",
        category=category,
        combat_relevant=combat,
        automated=automated,
        runtime_attack_weapon_id=weapon_id,
        notes=notes,
    )


def build_ranger_2024_audits(level: int) -> list[FeatureAudit]:
    try:
        from app.content.ranger_hunter_2024_audits_high import ranger_2024_high_audits

        audits = [
            _audit("spellcasting", "Spellcasting", "class", combat=True, automated=True,
                   notes="Half-caster from level 1. Wisdom. Favored Enemy Hunter's Mark does not count."),
            _audit("favored-enemy", "Favored Enemy", "class", combat=True, automated=True,
                   notes="Always prepares Hunter's Mark and grants free casts from the Favored Enemy column."),
            _audit("weapon-mastery", "Weapon Mastery", "class", combat=True, automated=True,
                   notes="Longbow Slow and Shortsword Vex."),
            _audit("wood-elf-lineage", "Wood Elf Lineage", "species", combat=True, automated=True,
                   notes=(
                       "35-foot Speed. Druidcraft is arena-neutral. Printed L5 Pass without Trace "
                       "grants +10 Stealth (concentration); the pit landing-damage Action policy "
                       "never selects Hide and no Stealth check is made during a fight, so the "
                       "spell cannot change a combat outcome."
                   )),
            _audit("fey-ancestry", "Fey Ancestry", "species", combat=True, automated=True,
                   notes="Advantage on saves against the Charmed condition."),
            _audit("alert", "Alert", "feat", combat=True, automated=True,
                   notes="Adds Proficiency Bonus to Initiative."),
            _audit("ensnaring-strike", "Ensnaring Strike", "class", combat=True, automated=True,
                   notes="Post-hit Bonus Action, Strength save, Restrained, start-of-turn Piercing."),
            _audit("cure-wounds", "Cure Wounds", "class", combat=True, automated=True),
            _audit("hunters-mark", "Hunter's Mark", "class", combat=True, automated=True,
                   notes="Bonus Action, 1d6 Force, retarget at 0 HP. Foe Slayer makes the die a d10."),
            _audit("studded-leather", "Studded Leather Armor", "equipment", combat=True, automated=True),
            _audit("longbow", "Longbow", "equipment", combat=True, automated=True, weapon_id="longbow"),
            _audit("shortsword", "Shortsword", "equipment", combat=True, automated=True, weapon_id="shortsword"),
            _audit("scimitar", "Scimitar", "equipment", combat=True, automated=True, weapon_id="scimitar"),
        ]
        if level >= 2:
            audits += [
                _audit("deft-explorer", "Deft Explorer", "class", combat=True, automated=True,
                       notes="Expertise in Perception. Languages are arena-neutral."),
                _audit("fighting-style", "Fighting Style — Archery", "class", combat=True, automated=True,
                       notes="+2 to attack rolls with Ranged weapons."),
                _audit("longstrider", "Longstrider", "class", combat=True, automated=True),
            ]
        if level >= 3:
            audits += [
                _audit("hunters-lore", "Hunter's Lore", "subclass", combat=False, automated=True,
                       notes="Knows marked immunities/resistances/vulnerabilities. Engine already applies typed defenses."),
                _audit("hunters-prey", "Hunter's Prey — Colossus Slayer", "subclass", combat=True, automated=True,
                       notes="Once per turn +1d8 when the target is missing Hit Points."),
            ]
        audits.extend(ranger_2024_high_audits(level))
        return audits
    except Exception:
        logger.exception("Failed to compile 2024 Ranger feature audits at level %s.", level)
        raise
