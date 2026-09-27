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
    if level >= 16:
        audits.append(
            FeatureAudit(
                feature_id="ability-score-improvement-l16", feature_name="Ability Score Improvement",
                source_reference="D&D Basic Rules 2014: Warlock 16",
                category="class", combat_relevant=True, automated=True,
                notes="Constitution 16→18 improves HP and concentration durability while Charisma is already capped at 20.",
            )
        )
    if level >= 17:
        audits.extend([
            FeatureAudit(
                feature_id="eldritch-blast-fourth-beam", feature_name="Eldritch Blast — Four Beams",
                source_reference="D&D Basic Rules 2014: Eldritch Blast",
                category="class", combat_relevant=True, automated=True,
                notes="The universal multi-spell-attack sequence resolves four independent Eldritch Blast beams.",
            ),
            FeatureAudit(
                feature_id="pact-magic-fourth-slot", feature_name="Pact Magic — Four Slots",
                source_reference="D&D Basic Rules 2014: Warlock 17",
                category="class", combat_relevant=True, automated=True,
                notes="The edition-correct Pact Magic progression supplies four 5th-level slots.",
            ),
            FeatureAudit(
                feature_id="mystic-arcanum-9", feature_name="Mystic Arcanum (9th Level)",
                source_reference="D&D Basic Rules 2014: Warlock 17; Power Word Kill",
                category="class", combat_relevant=True, automated=True,
                notes="Power Word Kill uses the universal 100-HP threshold instant-death action and honors instant-death prevention such as Death Ward.",
            ),
        ])
    return audits
