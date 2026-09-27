from __future__ import annotations

from app.domain.character_builds import FeatureAudit


def build_varek_fiend_2014_high_audits(level: int) -> list[FeatureAudit]:
    audits: list[FeatureAudit] = []
    if level >= 15:
        audits.extend([
            FeatureAudit(
                feature_id="mystic-arcanum-8", feature_name="Mystic Arcanum (8th Level)",
                source_reference="D&D Basic Rules 2014: Warlock 15; Power Word Stun",
                category="class", combat_relevant=True, automated=True,
                notes="Power Word Stun uses the universal HP-threshold condition action: 150 HP or fewer, no initial save, Stunned, Constitution repeat save at each target turn end.",
            ),
            FeatureAudit(
                feature_id="visions-of-distant-realms", feature_name="Visions of Distant Realms",
                source_reference="D&D Basic Rules 2014: Eldritch Invocations",
                category="class", combat_relevant=False, automated=True,
                notes="Seventh invocation remains arena-neutral utility rather than displacing the optimized blaster package.",
            ),
        ])
    return audits
