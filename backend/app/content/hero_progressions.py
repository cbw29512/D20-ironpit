from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CanonicalHero:
    class_id: str
    class_name: str
    hero_name: str
    subclass_id: str
    subclass_name: str


CANONICAL_HEROES = (
    CanonicalHero("barbarian", "Barbarian", "Rokhan Stonefury", "path-berserker", "Path of the Berserker"),
    CanonicalHero("bard", "Bard", "Lyra Silverstring", "college-lore", "College of Lore"),
    CanonicalHero("cleric", "Cleric", "Seraphine Dawnshield", "life-domain", "Life Domain"),
    CanonicalHero("druid", "Druid", "Thalen Greenbough", "circle-land", "Circle of the Land"),
    CanonicalHero("fighter", "Fighter", "Karnok Stoneward", "champion", "Champion"),
    CanonicalHero("monk", "Monk", "Kael Stillwater", "warrior-open-hand", "Warrior of the Open Hand"),
    CanonicalHero("paladin", "Paladin", "Aurelia Brightshield", "oath-devotion", "Oath of Devotion"),
    CanonicalHero("ranger", "Ranger", "Rowan Ashtrail", "hunter", "Hunter"),
    CanonicalHero("rogue", "Rogue", "Mara Quickstep", "thief", "Thief"),
    CanonicalHero("sorcerer", "Sorcerer", "Nyra Emberveil", "draconic-sorcery", "Draconic Sorcery"),
    CanonicalHero("warlock", "Warlock", "Varek Ashenmark", "fiend-patron", "Fiend Patron"),
    CanonicalHero("wizard", "Wizard", "Elian Starweaver", "evoker", "Evoker"),
)

HERO_BY_CLASS = {hero.class_id: hero for hero in CANONICAL_HEROES}
CANONICAL_BUILD_ID = "canonical"
CANONICAL_BUILD_NAME = "Canonical RAW Progression"
