from __future__ import annotations

from dataclasses import dataclass

from app.domain.class_loadouts import CanonicalCombatPlan


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
COMBAT_PLAN_BY_CLASS = {
    "barbarian": CanonicalCombatPlan(
        class_id="barbarian", mode="melee", shield_trained=True,
        power_build=True, dual_wield_trained=False,
    ),
    "bard": CanonicalCombatPlan(class_id="bard", mode="caster"),
    "cleric": CanonicalCombatPlan(class_id="cleric", mode="caster"),
    "druid": CanonicalCombatPlan(class_id="druid", mode="caster"),
    "fighter": CanonicalCombatPlan(
        class_id="fighter", mode="melee", shield_trained=True,
        power_build=True, dual_wield_trained=False,
    ),
    "monk": CanonicalCombatPlan(
        class_id="monk", mode="melee", dual_wield_trained=False,
        forced_melee_kind="unarmed",
    ),
    "paladin": CanonicalCombatPlan(
        class_id="paladin", mode="hybrid", shield_trained=True,
        dual_wield_trained=False,
    ),
    "ranger": CanonicalCombatPlan(
        class_id="ranger", mode="hybrid", shield_trained=True,
        dual_wield_trained=True,
    ),
    "rogue": CanonicalCombatPlan(
        class_id="rogue", mode="melee", dual_wield_trained=True,
    ),
    "sorcerer": CanonicalCombatPlan(class_id="sorcerer", mode="caster"),
    "warlock": CanonicalCombatPlan(class_id="warlock", mode="caster"),
    "wizard": CanonicalCombatPlan(class_id="wizard", mode="caster"),
}
COMBAT_MODE_BY_CLASS = {class_id: plan.mode for class_id, plan in COMBAT_PLAN_BY_CLASS.items()}
CANONICAL_BUILD_ID = "canonical"
CANONICAL_BUILD_NAME = "Canonical RAW Progression"
