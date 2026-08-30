"use strict";

// Exact-head certification: every public pregen must complete a real browser fight.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

for (const file of [
  "browser-pregen-data.js", "browser-pregen-math.js", "browser-pregen-attacks.js",
  "browser-pregen-spells.js", "browser-pregen-factory.js", "browser-heroes.js",
  "browser-monsters.js", "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-grapple.js", "browser-timed-conditions.js",
  "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-attack.js",
  "browser-reactions.js", "browser-reaction-movement.js", "browser-saves.js",
  "browser-charge.js", "browser-multiattack.js", "browser-healing.js",
  "browser-turn.js", "browser-engine.js",
]) load(file);

function fixedDice() {
  const roll = (sides) => Math.max(1, Math.ceil(sides * 0.6));
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
}

const heroes = Object.values(window.IRON_PIT_BROWSER_HEROES);
assert.equal(heroes.length, 720);
const classCounts = new Map();
let fights = 0;

for (const hero of heroes) {
  classCounts.set(hero.class_id, (classCounts.get(hero.class_id) || 0) + 1);
  window.IRON_PIT_DICE = fixedDice();
  const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
    hero_ids: [hero.id], monster_ids: ["srd-commoner"], starting_distance_ft: 30,
  });
  assert.notEqual(battle.outcome, "active", `${hero.id} did not resolve`);
  assert.notEqual(battle.outcome, "draw", `${hero.id} reached the round limit`);
  assert.ok(battle.rounds <= 100, `${hero.id} exceeded the round limit`);
  assert.ok(battle.events.some((event) => event.event_type === "attack" || event.event_type === "saving_throw"),
    `${hero.id} never produced an offensive event`);
  fights += 1;
}

assert.equal(fights, 720);
for (const [classId] of window.IRON_PIT_PREGEN_DATA.CLASS_ROWS) {
  assert.equal(classCounts.get(classId), 60, `${classId} should have 60 tested pregens`);
}
assert.ok(heroes.some((hero) => hero.id === "pregen-2024-wizard-l1-evoker"),
  "Wizard 1 Evoker must be in all-pregen fight certification");

const commoner = window.IRON_PIT_BROWSER_MONSTERS["srd-commoner"];
const originalSaves = commoner.saving_throw_bonuses;
commoner.saving_throw_bonuses = {
  strength: 0, dexterity: 0, constitution: 0, intelligence: 0, wisdom: 0, charisma: 0,
};
window.IRON_PIT_DICE = fixedDice();
const clericBattle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
  hero_ids: ["pregen-2024-cleric-l1-healer"], monster_ids: ["srd-commoner"], starting_distance_ft: 5,
});
commoner.saving_throw_bonuses = originalSaves;
assert.ok(clericBattle.events.some((event) => event.event_type === "saving_throw" && event.feature_id === "sacred-flame"),
  "Cleric should use Sacred Flame when the target has a certified Dexterity save");

console.log(`All ${fights} pregen browser fights resolved across 12 classes.`);
