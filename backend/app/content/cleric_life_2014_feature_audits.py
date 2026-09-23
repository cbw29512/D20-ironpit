from __future__ import annotations

from app.domain.character_builds import FeatureAudit

_CLERIC = "D&D Basic Rules 2014: Cleric"
_LIFE = "D&D Basic Rules 2014: Life Domain"
_DWARF = "D&D Basic Rules 2014: Hill Dwarf"
_EQUIPMENT = "D&D Basic Rules 2014: Equipment"


def _audit(
    feature_id: str, name: str, category: str, source: str,
    *, automated: bool = True, notes: str | None = None,
    weapon_id: str | None = None,
) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id, feature_name=name, source_reference=source,
        category=category, combat_relevant=True, automated=automated,
        runtime_attack_weapon_id=weapon_id, notes=notes,
    )


_BASE = (
    ("hill-dwarf-constitution", "Dwarf Ability Score Increase", "species", _DWARF),
    ("hill-dwarf-wisdom", "Hill Dwarf Ability Score Increase", "species", _DWARF),
    ("dwarven-resilience", "Dwarven Resilience", "species", _DWARF),
    ("dwarven-toughness", "Dwarven Toughness", "species", _DWARF),
    ("spellcasting", "Spellcasting", "class", _CLERIC),
    ("life-domain", "Life Domain", "subclass", _LIFE),
    ("life-domain-heavy-armor", "Bonus Proficiency", "subclass", _LIFE),
    ("disciple-of-life", "Disciple of Life", "subclass", _LIFE),
)

_UNLOCKS = (
    (2, "channel-divinity", "Channel Divinity", "class", _CLERIC, True, None),
    (2, "turn-undead", "Turn Undead", "class", _CLERIC, False, "Awaiting universal Turned/forced-retreat behavior."),
    (2, "preserve-life", "Channel Divinity: Preserve Life", "subclass", _LIFE, False, "Awaiting divisible capped healing-pool semantics."),
    (4, "asi-4", "Ability Score Improvement", "class", _CLERIC, True, None),
    (5, "destroy-undead-half", "Destroy Undead (CR 1/2)", "class", _CLERIC, False, "Depends on Turn Undead."),
    (6, "channel-divinity-2", "Channel Divinity (2/rest)", "class", _CLERIC, True, None),
    (6, "blessed-healer", "Blessed Healer", "subclass", _LIFE, True, None),
    (8, "asi-8", "Ability Score Improvement", "class", _CLERIC, True, None),
    (8, "destroy-undead-1", "Destroy Undead (CR 1)", "class", _CLERIC, False, "Depends on Turn Undead."),
    (8, "divine-strike", "Divine Strike", "subclass", _LIFE, False, "Needs generic once-per-turn weapon-hit damage rider binding."),
    (10, "divine-intervention", "Divine Intervention", "class", _CLERIC, False, "Needs deterministic Iron Pit policy over the RAW result."),
    (11, "destroy-undead-2", "Destroy Undead (CR 2)", "class", _CLERIC, False, "Depends on Turn Undead."),
    (12, "asi-12", "Ability Score Improvement", "class", _CLERIC, True, None),
    (14, "destroy-undead-3", "Destroy Undead (CR 3)", "class", _CLERIC, False, "Depends on Turn Undead."),
    (14, "divine-strike-2d8", "Divine Strike (2d8)", "subclass", _LIFE, False, "Scales the level-8 generic weapon-hit rider."),
    (16, "asi-16", "Ability Score Improvement", "class", _CLERIC, True, None),
    (17, "destroy-undead-4", "Destroy Undead (CR 4)", "class", _CLERIC, False, "Depends on Turn Undead."),
    (17, "supreme-healing", "Supreme Healing", "subclass", _LIFE, True, "Reuses universal healing-maximize semantics."),
    (18, "channel-divinity-3", "Channel Divinity (3/rest)", "class", _CLERIC, True, None),
    (19, "asi-19", "Ability Score Improvement", "class", _CLERIC, True, None),
    (20, "divine-intervention-improvement", "Divine Intervention Improvement", "class", _CLERIC, False, "Uses the level-10 Divine Intervention policy."),
)


def feature_audits_2014(level: int) -> list[FeatureAudit]:
    result = [_audit(fid, name, category, source) for fid, name, category, source in _BASE]
    result.extend([
        _audit("warhammer", "Warhammer", "equipment", _EQUIPMENT, weapon_id="warhammer"),
        _audit("scale-mail-shield", "Scale Mail and Shield", "equipment", _EQUIPMENT),
    ])
    for required, fid, name, category, source, automated, notes in _UNLOCKS:
        if level >= required:
            result.append(_audit(fid, name, category, source, automated=automated, notes=notes))
    return result
