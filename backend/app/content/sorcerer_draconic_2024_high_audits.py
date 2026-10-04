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


def build_nyra_2024_high_audits(level: int) -> list[FeatureAudit]:
    audits: list[FeatureAudit] = []
    if level >= 6:
        audits += [
            _audit(
                "elemental-affinity", "Elemental Affinity", "subclass",
                notes="Fire affinity grants permanent Fire Resistance and adds Charisma to one fire-spell damage roll.",
            ),
            _audit(
                "lightning-bolt", "Lightning Bolt", "class",
                notes="Uses the 2024 8d6 Lightning line fingerprint.",
            ),
        ]
    if level >= 7:
        audits.append(_audit(
            "sorcery-incarnate", "Sorcery Incarnate", "class",
            notes="When Innate Sorcery uses are empty, spend 2 Sorcery Points as the Bonus Action cost to activate it.",
        ))
    if level >= 8:
        audits += [
            _audit(
                "ability-score-improvement-l8", "Ability Score Improvement", "class",
                notes="Raises Charisma 19→20 and Wisdom 15→16 through the certified build profile.",
            ),
            _audit(
                "greater-invisibility", "Greater Invisibility", "class",
                notes="Uses the universal 2024 Greater Invisibility fingerprint.",
            ),
        ]
    if level >= 9:
        audits.append(_audit(
            "dispel-magic", "Dispel Magic", "class",
            notes="Reuses the universal effect-removal action with Charisma.",
        ))
    if level >= 10:
        audits.append(_audit(
            "distant-spell", "Metamagic: Distant Spell", "class",
            notes="Spends 1 Sorcery Point to double a spell's range of at least 5 feet.",
        ))
    if level >= 12:
        audits.append(_audit(
            "ability-score-improvement-l12", "Ability Score Improvement", "class",
            notes="Raises Wisdom 16→18 through the certified build profile.",
        ))
    if level >= 14:
        audits.append(_audit(
            "dragon-wings", "Dragon Wings", "subclass",
            notes="Bonus Action Fly Speed 60 feet for 1 hour. Empty uses restore by spending 3 Sorcery Points.",
        ))
    if level >= 16:
        audits.append(_audit(
            "ability-score-improvement-l16", "Ability Score Improvement", "class",
            notes="Raises Wisdom 18→20 through the certified build profile.",
        ))
    if level >= 18:
        audits.append(_audit(
            "dragon-companion", "Dragon Companion", "subclass",
            combat_relevant=False,
            notes="Summon Dragon is arena-unavailable and does not block certification.",
        ))
    if level >= 19:
        audits.append(_audit(
            "boon-of-fate", "Boon of Fate", "feat",
            notes="Epic Boon recommended by the 2024 Sorcerer table; +1 Intelligence and the shared 2d4 adjustment.",
        ))
    if level >= 20:
        audits.append(_audit(
            "arcane-apotheosis", "Arcane Apotheosis", "class",
            notes="While Innate Sorcery is active, Heightened Spell may be used once per turn without spending Sorcery Points.",
        ))
    return audits
