from __future__ import annotations

from app.domain.character_builds import FeatureAudit


def paladin_2024_feature(
    feature_id: str,
    name: str,
    category: str,
    *,
    combat: bool,
    automated: bool,
    weapon_id: str | None = None,
    notes: str | None = None,
) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=name,
        source_reference="D&D Beyond Basic Rules 2024",
        category=category,
        combat_relevant=combat,
        automated=automated,
        runtime_attack_weapon_id=weapon_id,
        notes=notes,
    )


def paladin_2024_level5_audits() -> list[FeatureAudit]:
    return [
        paladin_2024_feature(
            "extra-attack",
            "Extra Attack",
            "class",
            combat=True,
            automated=True,
            notes="The universal Attack action resolves two legal weapon attacks.",
        ),
        paladin_2024_feature(
            "faithful-steed",
            "Faithful Steed",
            "class",
            combat=False,
            automated=False,
            notes=(
                "Find Steed is always prepared and retains its one free Long-Rest cast resource, "
                "but Iron Pit's no-summons rule keeps the summon arena-unavailable."
            ),
        ),
        paladin_2024_feature(
            "oath-spells-level5",
            "Oath of Devotion Spells",
            "subclass",
            combat=True,
            automated=True,
            notes=(
                "Aid uses the certified 2024 defensive-spell fingerprint; "
                "Zone of Truth is always prepared but arena-neutral."
            ),
        ),
    ]


def paladin_2024_level6_audits() -> list[FeatureAudit]:
    return [
        paladin_2024_feature(
            "aura-of-protection",
            "Aura of Protection",
            "class",
            combat=True,
            automated=True,
            notes=(
                "Universal friendly saving-throw aura: 10-foot Emanation, "
                "Charisma-modifier flat save bonus, inactive while the source is Incapacitated."
            ),
        ),
    ]



def paladin_2024_level7_audits() -> list[FeatureAudit]:
    return [
        paladin_2024_feature(
            "aura-of-devotion",
            "Aura of Devotion",
            "subclass",
            combat=True,
            automated=True,
            notes=(
                "Universal friendly condition-immunity aura: Charmed immunity inside "
                "Aura of Protection's 10-foot Emanation, inactive while the source is Incapacitated."
            ),
        ),
        paladin_2024_feature(
            "lesser-restoration",
            "Lesser Restoration",
            "spell",
            combat=True,
            automated=True,
            notes=(
                "Seventh ordinary preparation reuses the certified 2024 universal "
                "condition-removal action."
            ),
        ),
    ]

def paladin_2024_source_references(level: int) -> list[str]:
    try:
        references = [
            "Basic Rules 2024: Paladin — Lay On Hands, Spellcasting, Weapon Mastery",
        ]
        if level >= 2:
            references.append(
                "Basic Rules 2024: Paladin level 2 — Fighting Style and Paladin's Smite"
            )
        if level >= 3:
            references.extend([
                "Basic Rules 2024: Paladin level 3 — Channel Divinity and Divine Sense",
                "Basic Rules 2024: Oath of Devotion level 3 — Sacred Weapon and Oath Spells",
            ])
        if level >= 4:
            references.append(
                "Basic Rules 2024: Paladin level 4 — Ability Score Improvement; "
                "Feats — Ability Score Improvement (+2 Strength)"
            )
        if level >= 5:
            references.extend([
                "Basic Rules 2024: Paladin level 5 — Extra Attack and Faithful Steed",
                "Basic Rules 2024: Oath of Devotion level 5 — Aid and Zone of Truth",
            ])
        if level >= 6:
            references.append("Basic Rules 2024: Paladin level 6 — Aura of Protection")
        if level >= 7:
            references.append("Basic Rules 2024: Oath of Devotion level 7 — Aura of Devotion")
        references.extend([
            "Basic Rules 2024: Character Origins — Human and Soldier",
            (
                "Basic Rules 2024: Spells — Cure Wounds, Divine Favor, Bless, Divine Smite, "
                "Searing Smite, Thunderous Smite, Shining Smite, Find Steed, Aid, Zone of Truth, "
                "Protection from Evil and Good, Shield of Faith, Lesser Restoration"
            ),
            (
                "Basic Rules 2024: Equipment — Chain Mail, Shield, Longsword, Javelin, "
                "Sap, Slow"
            ),
        ])
        return references
    except Exception:
        import logging
        logging.getLogger(__name__).exception(
            "Failed to build 2024 Paladin source references at level %s.",
            level,
        )
        raise
