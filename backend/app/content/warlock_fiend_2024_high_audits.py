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


def build_varek_fiend_2024_high_audits(level: int) -> list[FeatureAudit]:
    audits: list[FeatureAudit] = []
    if level >= 9:
        audits.append(_audit(
            "contact-patron", "Contact Patron", "class",
            combat_relevant=False, automated=True,
            notes="Always prepares Contact Other Plane. Arena-ignored by the Warlock combat spine.",
        ))
    if level >= 10:
        audits.append(_audit(
            "fiendish-resilience", "Fiendish Resilience", "subclass",
            notes="Selectable resistance to any damage type except Force after a Short or Long Rest.",
        ))
    if level >= 11:
        audits += [
            _audit("eldritch-blast-third-beam", "Eldritch Blast — Three Beams", "class",
                   notes="Uses the universal multi-spell-attack sequence."),
            _audit("mystic-arcanum-6", "Mystic Arcanum (6th Level)", "class",
                   notes="Circle of Death uses a separate one-use resource and the 2024 8d8 fingerprint."),
        ]
    if level >= 12:
        audits.append(_audit(
            "ability-score-improvement-l12", "Ability Score Improvement", "class",
            notes="Raises Wisdom 16→18 through the certified build profile.",
        ))
    if level >= 13:
        audits.append(_audit(
            "mystic-arcanum-7", "Mystic Arcanum (7th Level)", "class",
            notes="Finger of Death uses the 2024 save-damage fingerprint; zombie creation is arena-inert.",
        ))
    if level >= 14:
        audits.append(_audit(
            "hurl-through-hell", "Hurl Through Hell", "subclass",
            notes="On-hit Charisma save, immediate 8d10 Psychic if not a Fiend, Incapacitated, then return.",
        ))
    if level >= 15:
        audits.append(_audit(
            "mystic-arcanum-8", "Mystic Arcanum (8th Level)", "class",
            notes="Power Word Stun uses the universal 150-HP threshold condition action.",
        ))
    if level >= 16:
        audits.append(_audit(
            "ability-score-improvement-l16", "Ability Score Improvement", "class",
            notes="Raises Wisdom 18→20 through the certified build profile.",
        ))
    if level >= 17:
        audits += [
            _audit("eldritch-blast-fourth-beam", "Eldritch Blast — Four Beams", "class",
                   notes="The universal multi-spell-attack sequence resolves four independent beams."),
            _audit("mystic-arcanum-9", "Mystic Arcanum (9th Level)", "class",
                   notes="Power Word Kill uses the 2024 100-HP threshold plus 12d12 Psychic fallback."),
        ]
    if level >= 19:
        audits.append(_audit(
            "boon-of-fate", "Boon of Fate", "feat",
            notes="Epic Boon recommended by the 2024 Warlock table; +1 Intelligence and the shared 2d4 adjustment.",
        ))
    if level >= 20:
        audits.append(_audit(
            "eldritch-master", "Eldritch Master", "class",
            notes="Magical Cunning restores all expended Pact slots instead of half.",
        ))
    return audits
