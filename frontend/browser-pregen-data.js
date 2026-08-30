(() => {
  "use strict";

  const CLASS_ROWS = [
    ["barbarian", "Barbarian", "path-berserker", "Path of the Berserker"],
    ["bard", "Bard", "college-lore", "College of Lore"],
    ["cleric", "Cleric", "life-domain", "Life Domain"],
    ["druid", "Druid", "circle-land", "Circle of the Land"],
    ["fighter", "Fighter", "champion", "Champion"],
    ["monk", "Monk", "warrior-open-hand", "Warrior of the Open Hand"],
    ["paladin", "Paladin", "oath-devotion", "Oath of Devotion"],
    ["ranger", "Ranger", "hunter", "Hunter"],
    ["rogue", "Rogue", "thief", "Thief"],
    ["sorcerer", "Sorcerer", "draconic-sorcery", "Draconic Sorcery"],
    ["warlock", "Warlock", "fiend-patron", "Fiend Patron"],
    ["wizard", "Wizard", "evoker", "Evoker"],
  ];

  const BUILD_ROWS = {
    barbarian: [["great-weapon", "Great Weapon"], ["axe-shield", "Axe & Shield"], ["dual-wielder", "Dual Wielder"]],
    bard: [["support", "Support"], ["duelist", "Duelist"], ["controller", "Controller"]],
    cleric: [["guardian", "Guardian"], ["healer", "Healer"], ["war-priest", "War Priest"]],
    druid: [["wild-shaper", "Wild Shaper"], ["primal-caster", "Primal Caster"], ["warden", "Warden"]],
    fighter: [["guardian", "Sword & Shield"], ["great-weapon", "Great Weapon"], ["archer", "Archer"]],
    monk: [["striker", "Striker"], ["skirmisher", "Skirmisher"], ["defender", "Defender"]],
    paladin: [["guardian", "Guardian"], ["great-weapon", "Great Weapon"], ["avenger", "Avenger"]],
    ranger: [["archer", "Archer"], ["dual-wielder", "Dual Wielder"], ["warden", "Warden"]],
    rogue: [["skirmisher", "Skirmisher"], ["archer", "Archer"], ["duelist", "Duelist"]],
    sorcerer: [["blaster", "Blaster"], ["controller", "Controller"], ["survivor", "Survivor"]],
    warlock: [["eldritch-blaster", "Eldritch Blaster"], ["blade", "Blade"], ["controller", "Controller"]],
    wizard: [["evoker", "Evoker"], ["controller", "Controller"], ["defender", "Defender"]],
  };

  const CLASSES = {
    barbarian: { hitDie: 12, primary: "strength", secondary: "constitution", saves: ["strength", "constitution"], scores: [17,14,15,8,10,12] },
    bard: { hitDie: 8, primary: "charisma", secondary: "dexterity", saves: ["dexterity", "charisma"], scores: [8,14,13,10,13,17], caster: "charisma" },
    cleric: { hitDie: 8, primary: "wisdom", secondary: "constitution", saves: ["wisdom", "charisma"], scores: [13,10,14,8,17,13], caster: "wisdom" },
    druid: { hitDie: 8, primary: "wisdom", secondary: "constitution", saves: ["intelligence", "wisdom"], scores: [10,14,15,12,17,8], caster: "wisdom" },
    fighter: { hitDie: 10, primary: "strength", secondary: "constitution", saves: ["strength", "constitution"], scores: [17,14,15,10,12,8] },
    monk: { hitDie: 8, primary: "dexterity", secondary: "wisdom", saves: ["strength", "dexterity"], scores: [10,17,14,8,15,12] },
    paladin: { hitDie: 10, primary: "strength", secondary: "charisma", saves: ["wisdom", "charisma"], scores: [17,12,14,8,10,14], caster: "charisma" },
    ranger: { hitDie: 10, primary: "dexterity", secondary: "wisdom", saves: ["strength", "dexterity"], scores: [12,17,14,10,14,8], caster: "wisdom" },
    rogue: { hitDie: 8, primary: "dexterity", secondary: "constitution", saves: ["dexterity", "intelligence"], scores: [8,17,14,14,12,10] },
    sorcerer: { hitDie: 6, primary: "charisma", secondary: "constitution", saves: ["constitution", "charisma"], scores: [8,14,13,10,13,17], caster: "charisma" },
    warlock: { hitDie: 8, primary: "charisma", secondary: "constitution", saves: ["wisdom", "charisma"], scores: [8,14,13,10,13,17], caster: "charisma" },
    wizard: { hitDie: 6, primary: "intelligence", secondary: "constitution", saves: ["intelligence", "wisdom"], scores: [8,14,14,17,12,10], caster: "intelligence" },
  };

  window.IRON_PIT_PREGEN_DATA = { BUILD_ROWS, CLASSES, CLASS_ROWS };
})();
