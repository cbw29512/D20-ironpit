from __future__ import annotations

import logging

from app.domain.character_builds import FeatureAudit

logger = logging.getLogger(__name__)


def _audit(
    feature_id: str,
    name: str,
    category: str,
    *,
    combat: bool = True,
    automated: bool = True,
    weapon_id: str | None = None,
    notes: str | None = None,
) -> FeatureAudit:
    try:
        source = "D&D SRD 5.1 (2014): Oath of Devotion" if category == "subclass" else "D&D SRD 5.1 (2014): Paladin"
        return FeatureAudit(
            feature_id=feature_id,
            feature_name=name,
            source_reference=source,
            category=category,
            combat_relevant=combat,
            automated=automated,
            runtime_attack_weapon_id=weapon_id,
            notes=notes,
        )
    except Exception:
        logger.exception("Failed to build 2014 Paladin feature audit for %s", feature_id)
        raise


def build_paladin_2014_feature_audits(level: int) -> list[FeatureAudit]:
    try:
        audits = [
            _audit("human-ability-increase", "Human Ability Score Increase", "species", combat=False),
            _audit("lay-on-hands", "Lay on Hands", "class"),
            _audit("longsword", "Longsword", "equipment", weapon_id="longsword"),
            _audit("shield", "Shield", "equipment"),
            _audit(
                "divine-sense", "Divine Sense", "class", combat=False, automated=False,
                notes="Iron Pit exposes creature identity directly; active detection is outside combat resolution.",
            ),
        ]
        if level >= 2:
            audits.extend([
                _audit("fighting-style-defense", "Defense Fighting Style", "class"),
                _audit(
                    "spellcasting", "Spellcasting", "class",
                    notes=(
                        "Edition-correct prepared spell counts, slots, combat spell actions, Devotion oath spells, "
                        "concentration, condition removal, defensive wards, and Dispel Magic are automated. "
                        "Noncombat utility spells remain explicitly outside arena resolution."
                    ),
                ),
                _audit("divine-smite", "Divine Smite", "class"),
            ])
        if level >= 3:
            audits.extend([
                _audit(
                    "divine-health", "Divine Health", "class", combat=False, automated=False,
                    notes="The standard Iron Pit arena does not apply disease effects.",
                ),
                _audit(
                    "sacred-weapon", "Sacred Weapon", "subclass",
                    notes="Channel Divinity activates the timed Charisma attack-roll bonus through the shared modifier engine.",
                ),
                _audit(
                    "turn-the-unholy", "Turn the Unholy", "subclass",
                    notes="Fiends and Undead within 30 feet use the shared one-minute creature-turning engine.",
                ),
            ])
        if level >= 5:
            audits.append(_audit("extra-attack", "Extra Attack", "class"))
        if level >= 6:
            audits.append(_audit(
                "aura-of-protection", "Aura of Protection", "class",
                notes="The strongest 10-foot Paladin save bonus is recalculated from live encounter positions.",
            ))
        if level >= 7:
            audits.append(_audit(
                "aura-of-devotion", "Aura of Devotion", "subclass",
                notes="Charm immunity propagates dynamically to allies within 10 feet.",
            ))
        if level >= 10:
            audits.append(_audit(
                "aura-of-courage", "Aura of Courage", "class",
                notes="Fear immunity propagates dynamically to allies within 10 feet.",
            ))
        if level >= 11:
            audits.append(_audit(
                "improved-divine-smite", "Improved Divine Smite", "class",
                notes="Every hit with Aurelia's melee-weapon loadout carries a declarative 1d8 radiant on-hit rider.",
            ))
        if level >= 13:
            audits.append(_audit(
                "devotion-oath-spells-4", "Oath of Devotion 4th-level Spells", "subclass",
                notes=(
                    "Guardian of Faith uses the universal persistent-hazard engine. Freedom of Movement uses "
                    "source-owned magical Paralyzed/Restrained prevention, difficult-terrain bypass, magical "
                    "Speed-reduction prevention, and 5-foot nonmagical grapple escape. Its underwater clauses "
                    "remain source-recorded but arena-neutral in the standard dry Iron Pit."
                ),
            ))
        if level >= 14:
            audits.append(_audit(
                "cleansing-touch", "Cleansing Touch", "class",
                notes=(
                    "Uses the generic tracked-spell effect-removal action at touch range, backed by the "
                    "Charisma-modifier use resource and an automatic removal ceiling that covers spell levels 1-9."
                ),
            ))
        if level >= 15:
            audits.append(_audit(
                "purity-of-spirit", "Purity of Spirit", "subclass", automated=False,
                notes=(
                    "The existing Protection from Evil and Good typed attack Disadvantage and typed charm/fright "
                    "immunities are installed passively through the universal opening-modifier engine. Possession "
                    "prevention/termination is not yet represented by the universal control-state engine, so the "
                    "complete feature remains uncertified."
                ),
            ))
        if level >= 16:
            audits.append(_audit(
                "ability-score-improvement-16", "Ability Score Improvement", "class",
                notes="Prepared persistent choice: +2 Charisma.",
            ))
        if level >= 17:
            audits.append(_audit(
                "devotion-oath-spells-5", "Oath of Devotion 5th-level Spells", "subclass",
                notes=(
                    "Commune is noncombat. Flame Strike uses the universal one-save split fire/radiant "
                    "save-damage path with half damage on a successful Dexterity save."
                ),
            ))
        if level >= 18:
            audits.append(_audit(
                "aura-improvements", "Aura Improvements", "class",
                notes="The shared 2014 Paladin aura resolver reads a source-owned radius: 10 feet normally and 30 feet from level 18.",
            ))
        if level >= 19:
            audits.append(_audit(
                "ability-score-improvement-19", "Ability Score Improvement", "class",
                notes="Prepared persistent choice: +1 Charisma and +1 Constitution.",
            ))
        if level >= 20:
            audits.append(_audit(
                "holy-nimbus", "Holy Nimbus", "subclass", automated=False,
                notes=(
                    "The 1/long-rest resource is present. Activation, timed 30-foot start-turn radiant damage, "
                    "and fiend/undead spell-save Advantage still require universal composition."
                ),
            ))
        return audits
    except Exception:
        logger.exception("Failed to compile 2014 Paladin feature audits at level %s", level)
        raise
