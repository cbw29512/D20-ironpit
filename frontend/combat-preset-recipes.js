(() => {
  "use strict";

  const A = (kind, value) => Object.freeze({ kind, value });
  const R = (id, ruleset, title, level, classes, monsters, purpose, seed, aspects) => Object.freeze({
    id, ruleset, title, level, seed, purpose,
    classes: Object.freeze(classes), monsters: Object.freeze(monsters), aspects: Object.freeze(aspects),
  });

  const recipes = Object.freeze([
    R("duel", "2014", "1v1 · Monk discipline", 5, ["monk"], ["brown-bear"],
      "Stunning Strike and the Stunned condition.", 1701, [A("feature", "stunning-strike"), A("condition", "stunned")]),
    R("legendary", "2014", "1v1 · Legendary Unicorn", 5, ["fighter"], ["unicorn"],
      "A printed legendary action fires after another creature's turn.", 1, [A("text", "Legendary Action")]),
    R("goblins", "2014", "1v2 · Barbarian vs two Goblins", 3, ["barbarian"], ["goblin", "goblin"],
      "Barbarian Rage.", 1701, [A("feature", "rage")]),
    R("partners", "2014", "2v2 · Steel and healing", 5, ["fighter", "cleric"], ["brown-bear", "dire-wolf"],
      "Action Surge, healing, and Pack Tactics.", 11, [A("feature", "action-surge"), A("event", "healing"), A("feature", "pack-tactics")]),
    R("casters", "2014", "3v3 · Fireproof opposition", 7, ["wizard", "sorcerer", "bard"], ["hell-hound", "hell-hound", "hell-hound"],
      "Hell Hound fire breath and a damaging spell.", 7, [A("feature", "fire-breath"), A("anyFeature", ["lightning-bolt", "shatter", "magic-missile", "fireball"])]),
    R("auras", "2014", "4v4 · Mixed arms", 9, ["paladin", "ranger", "druid", "warlock"], ["minotaur", "hell-hound", "owlbear", "blue-dragon-wyrmling"],
      "Extra Attack, healing, and a dragon breath.", 1701, [A("feature", "extra-attack"), A("event", "healing"), A("anyFeature", ["lightning-breath", "fire-breath"])]),
    R("pressure", "2014", "5v5 · Breath and trampling", 11, ["barbarian", "rogue", "cleric", "monk", "wizard"], ["elephant", "elephant", "red-dragon-wyrmling", "red-dragon-wyrmling", "red-dragon-wyrmling"],
      "Rage, Sneak Attack, and healing.", 13, [A("feature", "rage"), A("source", "Sneak Attack"), A("event", "healing")]),
    R("party", "2014", "6v6 · Full party stress test", 15, ["fighter", "paladin", "cleric", "rogue", "sorcerer", "warlock"], ["young-black-dragon", "young-black-dragon", "young-black-dragon", "giant-ape", "giant-ape", "giant-ape"],
      "Acid breath, Extra Attack, and healing.", 1702, [A("feature", "acid-breath"), A("feature", "extra-attack"), A("event", "healing")]),
    R("grapple", "2014", "2v2 · Escape the coils", 4, ["monk", "rogue"], ["giant-constrictor-snake", "giant-constrictor-snake"],
      "Grappled, Restrained, and a grapple escape.", 1701, [A("condition", "grappled"), A("condition", "restrained"), A("feature", "escape-grapple")]),
    R("poison", "2014", "3v3 · Poison and recovery", 6, ["paladin", "cleric", "ranger"], ["giant-scorpion", "giant-scorpion", "giant-scorpion"],
      "Healing and a Giant Scorpion grapple.", 1701, [A("event", "healing"), A("condition", "grappled")]),
    R("undead", "2014", "2v2 · Undead endurance", 2, ["cleric", "fighter"], ["zombie", "skeleton"],
      "Healing and Undead Fortitude.", 131, [A("event", "healing"), A("text", "Undead Fortitude")]),
    R("capstones", "2014", "6v6 · Level 20 martial abilities", 20, ["barbarian", "fighter", "monk", "paladin", "rogue", "ranger"], ["roc", "roc", "roc", "roc", "roc", "roc"],
      "Rage or Extra Attack and a Gargantuan grapple.", 1701, [A("anyFeature", ["rage", "extra-attack"]), A("condition", "grappled")]),
    R("archmages", "2014", "6v6 · Level 20 spell abilities", 20, ["bard", "cleric", "druid", "sorcerer", "warlock", "wizard"], ["young-red-dragon", "young-red-dragon", "young-red-dragon", "young-red-dragon", "young-red-dragon", "young-red-dragon"],
      "Concentration and healing or a leveled spell.", 1701, [A("concentration", true), A("anyFeature", ["mass-cure-wounds", "mass-healing-word", "healing-word", "cure-wounds", "fireball", "cone-of-cold", "spirit-guardians"])]),

    R("2024-duel", "2024", "2024 1v1 · Monk discipline", 5, ["monk"], ["brown-bear"],
      "Stunning Strike and the Stunned condition.", 4, [A("feature", "stunning-strike"), A("condition", "stunned")]),
    R("2024-goblins", "2024", "2024 1v2 · Barbarian vs two Goblin Warriors", 3, ["barbarian"], ["goblin-warrior", "goblin-warrior"],
      "Barbarian Rage.", 1701, [A("feature", "rage")]),
    R("2024-partners", "2024", "2024 2v2 · Steel and healing", 5, ["fighter", "cleric"], ["brown-bear", "dire-wolf"],
      "Action Surge, Extra Attack, and Prone.", 1701, [A("feature", "action-surge"), A("feature", "extra-attack"), A("condition", "prone")]),
    R("2024-casters", "2024", "2024 3v3 · Fireproof opposition", 7, ["wizard", "sorcerer", "bard"], ["hell-hound", "blue-dragon-wyrmling", "owlbear"],
      "Dragon or Hell Hound breath and Bard healing.", 7, [A("anyFeature", ["fire-breath", "srd-hell-hound-fire-breath", "lightning-breath", "srd-blue-dragon-wyrmling-lightning-breath"]), A("event", "healing")]),
    R("2024-auras", "2024", "2024 4v4 · Mixed arms", 9, ["ranger", "druid", "warlock", "bard"], ["owlbear", "hell-hound", "manticore", "blue-dragon-wyrmling"],
      "Extra Attack, healing, and a dragon breath.", 1701, [A("feature", "extra-attack"), A("event", "healing"), A("anyFeature", ["lightning-breath", "fire-breath", "srd-blue-dragon-wyrmling-lightning-breath", "srd-hell-hound-fire-breath"])]),
    R("2024-pressure", "2024", "2024 5v5 · Breath and trampling", 11, ["barbarian", "rogue", "cleric", "monk", "wizard"], ["hippopotamus", "triceratops", "red-dragon-wyrmling", "red-dragon-wyrmling", "red-dragon-wyrmling"],
      "Rage, Sneak Attack, and healing.", 11, [A("feature", "rage"), A("source", "Sneak Attack"), A("event", "healing")]),
    R("2024-party", "2024", "2024 6v6 · Full party stress test", 15, ["ranger", "cleric", "bard", "sorcerer", "warlock", "wizard"], ["blue-dragon-wyrmling", "blue-dragon-wyrmling", "blue-dragon-wyrmling", "blue-dragon-wyrmling", "blue-dragon-wyrmling", "blue-dragon-wyrmling"],
      "Dragon breath, Extra Attack, and healing.", 1701, [A("anyFeature", ["lightning-breath", "srd-blue-dragon-wyrmling-lightning-breath"]), A("feature", "extra-attack"), A("event", "healing")]),
    R("2024-grapple", "2024", "2024 2v2 · Escape the jaws", 4, ["monk", "rogue"], ["crocodile", "crocodile"],
      "Grappled, Restrained, and a grapple escape.", 7, [A("condition", "grappled"), A("condition", "restrained"), A("feature", "escape-grapple")]),
    R("2024-poison", "2024", "2024 3v3 · Poison and recovery", 6, ["paladin", "cleric", "ranger"], ["giant-scorpion", "giant-scorpion", "giant-scorpion"],
      "Healing and a Giant Scorpion grapple.", 1701, [A("event", "healing"), A("condition", "grappled")]),
    R("2024-undead", "2024", "2024 2v2 · Undead endurance", 2, ["cleric", "fighter"], ["zombie", "skeleton"],
      "Healing and Undead Fortitude.", 263, [A("event", "healing"), A("text", "Undead Fortitude")]),
    R("2024-capstones", "2024", "2024 6v6 · Level 20 martial abilities", 20, ["barbarian", "fighter", "monk", "paladin", "rogue", "ranger"], ["wyvern", "wyvern", "wyvern", "tyrannosaurus-rex", "tyrannosaurus-rex", "tyrannosaurus-rex"],
      "Rage or Extra Attack and Action Surge.", 1701, [A("anyFeature", ["rage", "extra-attack"]), A("feature", "action-surge")]),
    R("2024-archmages", "2024", "2024 6v6 · Level 20 spell abilities", 20, ["bard", "cleric", "druid", "sorcerer", "warlock", "wizard"], ["young-red-dragon", "young-red-dragon", "young-red-dragon", "young-red-dragon", "young-red-dragon", "young-red-dragon"],
      "Concentration and healing or a leveled spell.", 1701, [A("concentration", true), A("anyFeature", ["mass-heal", "mass-cure-wounds", "mass-healing-word", "healing-word", "fireball", "cone-of-cold", "spirit-guardians"])]),
  ]);

  window.IRON_PIT_COMBAT_PRESET_RECIPES = { recipes };
})();
