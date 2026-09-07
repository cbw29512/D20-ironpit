from __future__ import annotations

import re

TEXT_FIELDS = ("traits", "actions", "bonusActions", "reactions", "legendaryActions")
SECTION_LABELS = {
    "traits": "trait",
    "actions": "action",
    "bonusActions": "bonus-action",
    "reactions": "reaction",
    "legendaryActions": "legendary-action",
}
CONDITIONS = (
    "blinded", "charmed", "deafened", "frightened", "grappled", "incapacitated",
    "invisible", "paralyzed", "petrified", "poisoned", "prone", "restrained",
    "stunned", "unconscious",
)
DAMAGE_TYPES = (
    "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic",
    "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
)
PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("attack-roll", re.compile(r"\b(?:melee|ranged|melee or ranged)\s+(?:spell\s+)?attack roll\b", re.I)),
    ("multiattack", re.compile(r"\bmultiattack\b", re.I)),
    ("saving-throw", re.compile(r"\bsaving throw\b|\bDC\s*\d+\s+(?:STR|DEX|CON|INT|WIS|CHA)\b", re.I)),
    ("advantage", re.compile(r"\badvantage\b", re.I)),
    ("disadvantage", re.compile(r"\bdisadvantage\b", re.I)),
    ("injured-target-advantage", re.compile(r"\badvantage\b[^.]{0,120}\b(?:doesn['’]t have all|has less than (?:its|the) maximum|missing)\b[^.]{0,80}\bhit points?\b", re.I)),
    ("flat-modifier", re.compile(r"\bbonus to\b|\bpenalty to\b|\bAC increases?\b|\bAC decreases?\b", re.I)),
    ("bonus-die", re.compile(r"\badd(?:s)?\s+\d*d\d+\b|\bsubtract(?:s)?\s+\d*d\d+\b", re.I)),
    ("ability-score-change", re.compile(r"\b(?:Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)\s+score\s+(?:decreases?|increases?|is reduced|is increased)\b", re.I)),
    ("ability-score-zero-death", re.compile(r"\bdies?\b[^.]{0,100}\b(?:Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)\b[^.]{0,80}\b0\b", re.I)),
    ("attachment-state", re.compile(r"\battaches?\s+to\b|\bwhile attached\b|\bdetach(?:es|ed|ing)?\b", re.I)),
    ("temporary-hp", re.compile(r"\btemporary hit points?\b", re.I)),
    ("healing", re.compile(r"\bregains?\s+\d+|\bregains? hit points?\b|\bheals?\b", re.I)),
    ("max-hp-change", re.compile(r"\bhit point maximum\b", re.I)),
    ("regeneration", re.compile(r"\bregeneration\b|\bregains?\s+\d+\s+hit points?\s+at the start\b", re.I)),
    ("recharge", re.compile(r"\brecharge\s+\d", re.I)),
    ("limited-use", re.compile(r"\b\d+\s*/\s*(?:day|rest)\b|\bonce per (?:day|rest)\b", re.I)),
    ("reaction", re.compile(r"\breaction\b", re.I)),
    ("bonus-action", re.compile(r"\bbonus action\b", re.I)),
    ("aura", re.compile(r"\baura\b|\bwithin\s+\d+\s+feet\b", re.I)),
    ("start-turn", re.compile(r"\bstart of (?:its|the|each|a creature'?s|target'?s) turn\b", re.I)),
    ("end-turn", re.compile(r"\bend of (?:its|the|each|a creature'?s|target'?s) turn\b", re.I)),
    ("repeat-save", re.compile(r"\brepeat(?:s)? the saving throw\b|\brepeats? the save\b", re.I)),
    ("concentration", re.compile(r"\bconcentration\b", re.I)),
    ("zero-hp-effect", re.compile(r"\b0 hit points\b|\breduced to 0\b|\bdrops? to 0\b", re.I)),
    ("death-trigger", re.compile(r"\bwhen (?:it|the creature) dies\b|\bupon death\b", re.I)),
    ("spellcasting", re.compile(r"\bspellcasting\b|\bspell attack\b|\bspell save DC\b", re.I)),
    ("summoning", re.compile(r"\bsummons?\b|\bcreates?\b[^.]{0,80}\b(?:creature|monster|specter|zombie|skeleton)\b", re.I)),
    ("transformation", re.compile(r"\bshapechanger\b|\bshapechange\b|\btransforms?\b|\bchanges? form\b", re.I)),
    ("legendary", re.compile(r"\blegendary action\b|\blegendary resistance\b", re.I)),
)
COMPLEXITY_WEIGHTS = {
    "attack-roll": 1, "multiattack": 1, "saving-throw": 2, "advantage": 1,
    "disadvantage": 1, "injured-target-advantage": 1, "flat-modifier": 2,
    "bonus-die": 2, "ability-score-change": 4, "ability-score-zero-death": 3,
    "attachment-state": 6, "temporary-hp": 2, "healing": 2, "max-hp-change": 3,
    "regeneration": 3, "recharge": 2, "limited-use": 2, "reaction": 2,
    "bonus-action": 1, "aura": 3, "start-turn": 2, "end-turn": 2,
    "repeat-save": 3, "concentration": 3, "zero-hp-effect": 3,
    "death-trigger": 3, "spellcasting": 4, "summoning": 7, "transformation": 7,
    "legendary": 6, "damage": 1, "resistance": 1, "vulnerability": 1,
    "immunity": 1, "source-parse-error": 10,
}
