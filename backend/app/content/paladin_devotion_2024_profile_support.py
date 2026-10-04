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
        if level >= 8:
            references.append(
                "Basic Rules 2024: Paladin level 8 — Ability Score Improvement; "
                "Feats — Ability Score Improvement (+1 Strength, +1 Charisma)"
            )
        if level >= 9:
            references.extend([
                "Basic Rules 2024: Paladin level 9 — Abjure Foes",
                "Basic Rules 2024: Oath of Devotion level 9 — Beacon of Hope and Dispel Magic",
            ])
        if level >= 10:
            references.append("Basic Rules 2024: Paladin level 10 — Aura of Courage")
        if level >= 11:
            references.extend([
                "Basic Rules 2024: Paladin level 11 — Radiant Strikes and third Channel Divinity use",
                "Basic Rules 2024: Spells — Crusader\'s Mantle",
            ])
        if level >= 12:
            references.append(
                "Basic Rules 2024: Paladin level 12 — Ability Score Improvement; "
                "Feats — Ability Score Improvement (+2 Charisma)"
            )
        if level >= 13:
            references.extend([
                "Basic Rules 2024: Paladin level 13 — fourth-level spells and Proficiency Bonus +5",
                "Basic Rules 2024: Oath of Devotion level 13 — Freedom of Movement and Guardian of Faith",
                "Basic Rules 2024: Spells — Staggering Smite",
            ])
        if level >= 14:
            references.append("Basic Rules 2024: Paladin level 14 — Restoring Touch")
        if level >= 15:
            references.extend([
                "Basic Rules 2024: Oath of Devotion level 15 — Smite of Protection",
                "Basic Rules 2024: Spells — Aura of Life",
            ])
        if level >= 16:
            references.append(
                "Basic Rules 2024: Paladin level 16 — Ability Score Improvement; "
                "Feats — Ability Score Improvement (+2 Charisma)"
            )
        if level >= 17:
            references.extend([
                "Basic Rules 2024: Paladin level 17 — Proficiency Bonus +6 and fifth-level spell slots",
                "Basic Rules 2024: Oath of Devotion level 17 — Commune and Flame Strike",
                "Basic Rules 2024: Spells — Destructive Wave and Greater Restoration",
            ])
        if level >= 18:
            references.append("Basic Rules 2024: Paladin level 18 — Aura Expansion")
        references.extend([
            "Basic Rules 2024: Character Origins — Human and Soldier",
            (
                "Basic Rules 2024: Spells — Cure Wounds, Divine Favor, Bless, Divine Smite, "
                "Searing Smite, Thunderous Smite, Shining Smite, Find Steed, Aid, Zone of Truth, "
                "Protection from Evil and Good, Shield of Faith, Lesser Restoration, "
                "Aura of Vitality, Blinding Smite, Crusader\'s Mantle, Beacon of Hope, Dispel Magic, "
                "Staggering Smite, Aura of Life, Destructive Wave, Greater Restoration, Commune, Flame Strike"
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
