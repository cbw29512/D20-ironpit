from __future__ import annotations

from app.domain.character_builds import FeatureAudit


def _audit(
    feature_id: str,
    feature_name: str,
    category: str,
    *,
    combat_relevant: bool = True,
    automated: bool = True,
    notes: str | None = None,
) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=feature_name,
        source_reference="D&D Beyond Basic Rules 2024",
        category=category,
        combat_relevant=combat_relevant,
        automated=automated,
        notes=notes,
    )


def build_elian_2024_high_audits(level: int) -> list[FeatureAudit]:
    audits: list[FeatureAudit] = []
    if level >= 6:
        audits.append(_audit(
            "sculpt-spells", "Sculpt Spells", "subclass",
            notes=(
                "Uses the universal area-spell ally-protection grant. The per-cast cap is "
                "1 + slot level, and protected creatures take no damage."
            ),
        ))
    if level >= 8:
        audits += [
            _audit(
                "ability-score-improvement-l8", "Ability Score Improvement", "class",
                notes="Raises Intelligence 19→20 and Wisdom 15→16 through the certified build profile.",
            ),
            _audit(
                "greater-invisibility", "Greater Invisibility", "class",
                notes="Uses the universal 2024 Greater Invisibility fingerprint.",
            ),
        ]
    if level >= 9:
        audits.append(_audit(
            "dispel-magic", "Dispel Magic", "class",
            notes="Reuses the universal effect-removal action with Intelligence.",
        ))
    if level >= 10:
        audits.append(_audit(
            "empowered-evocation", "Empowered Evocation", "subclass",
            notes="Adds Intelligence modifier once to a Wizard Evocation spell damage roll.",
        ))
    if level >= 12:
        audits.append(_audit(
            "ability-score-improvement-l12", "Ability Score Improvement", "class",
            notes="Raises Wisdom 16→18 through the certified build profile.",
        ))
    if level >= 14:
        audits.append(_audit(
            "overchannel", "Overchannel", "subclass",
            notes=(
                "Declared 1st-5th-level damaging Wizard spells use maximum damage dice. "
                "The first use is safe; later uses deal escalating d12 necrotic self-damage."
            ),
        ))
    if level >= 16:
        audits.append(_audit(
            "ability-score-improvement-l16", "Ability Score Improvement", "class",
            notes="Raises Wisdom 18→20 through the certified build profile.",
        ))
    if level >= 18:
        audits.append(_audit(
            "spell-mastery", "Spell Mastery", "class",
            notes="Burning Hands and Shatter bind to reusable lowest-level casts that do not expend a slot.",
        ))
    if level >= 19:
        audits.append(_audit(
            "boon-of-fate", "Boon of Fate", "feat",
            notes="Epic Boon selected in place of Spell Recall; +1 Charisma and the shared 2d4 adjustment.",
        ))
    if level >= 20:
        audits.append(_audit(
            "signature-spells", "Signature Spells", "class",
            notes="Fireball and Lightning Bolt each bind to one free 3rd-level cast per Short or Long Rest.",
        ))
    return audits
