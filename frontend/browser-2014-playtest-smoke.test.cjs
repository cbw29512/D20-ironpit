"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

// The playtest must start from generated 2014 data only. Do not load any of
// the production srd-* browser monster fixture files in this test.
load("browser-heroes.js");
load("browser-monsters-generated.js");

assert.equal(window.IRON_PIT_HERO_RULESET, "2014");
assert.equal(window.IRON_PIT_RULESET, "2014");
assert.equal(window.IRON_PIT_HERO_SCOPE, "srd-test-harness");
assert.equal(Object.keys(window.IRON_PIT_BROWSER_HEROES).length, 4);
assert.equal(
  Object.keys(window.IRON_PIT_BROWSER_MONSTERS).length,
  window.IRON_PIT_CERTIFIED_MONSTER_COUNT,
);
for (const hero of Object.values(window.IRON_PIT_BROWSER_HEROES)) {
  assert.equal(hero.ruleset, "2014");
  assert.equal(hero.test_harness, true);
  assert.ok(!String(hero.source).includes("2024"), `2024 hero source leaked: ${hero.source}`);
}
for (const monster of Object.values(window.IRON_PIT_BROWSER_MONSTERS)) {
  assert.ok(String(monster.id).startsWith("2014-"), `non-2014 monster leaked: ${monster.id}`);
  assert.ok(!String(monster.id).startsWith("srd-"), `2024 fixture leaked: ${monster.id}`);
}

for (const file of [
  "browser-condition-immunity.js", "browser-source-effect-immunity.js",
  "browser-condition-rules.js", "browser-action-economy.js", "browser-grapple.js",
  "browser-restraints.js", "browser-timed-conditions.js", "browser-damage-triggered-effects.js",
  "browser-save-control-effects.js", "browser-source-bound-effects.js",
  "browser-ongoing-spell-control.js", "browser-modifiers.js", "browser-state.js",
  "browser-rolls.js", "browser-zero-hp.js", "browser-attack-advantage.js",
  "browser-damage-absorption.js", "browser-attack.js", "browser-start-turn-damage.js",
  "browser-swallow.js", "browser-light-weapons.js", "browser-light-attack.js",
  "browser-standard-attack-action.js", "browser-reactions.js", "browser-reaction-movement.js",
  "browser-dodge.js", "browser-saves.js", "browser-death-triggers.js",
  "browser-on-hit-save-conditions.js", "browser-on-hit-saves.js", "browser-reactive-damage.js",
  "browser-attack-resources.js", "browser-topple.js", "browser-concentration.js",
  "browser-invisibility.js", "browser-spell-effects.js", "browser-spell-modifiers.js",
  "browser-condition-lifecycle.js", "browser-charge.js", "browser-multiattack.js",
  "browser-healing.js", "browser-spellcasting.js", "browser-spell-area.js",
  "browser-offense-value.js", "browser-spell-policy.js", "browser-spell-resolution.js",
  "browser-spell-attack-policy.js", "browser-spell-attack.js",
  "browser-automatic-damage-spell-policy.js", "browser-automatic-damage-spell.js",
  "browser-spell-offense.js", "browser-precombat-spells.js", "browser-condition-removal.js",
  "browser-support.js", "browser-rampage.js", "browser-turn.js", "browser-formation.js",
  "browser-arena-map.js", "browser-grid-geometry.js", "browser-area-shapes.js",
  "browser-area-targeting.js", "browser-area-save-actions.js", "browser-grid-movement-support.js",
  "browser-grid-path-search-support.js", "browser-grid-path-search.js", "browser-grid-movement.js",
  "browser-grid-reaction-support.js", "browser-offensive-ranges.js",
  "browser-offensive-movement.js", "browser-grid-placement.js", "browser-initiative.js",
  "browser-engine.js",
]) load(file);

function deterministicDice(seed = 2014) {
  let state = seed >>> 0;
  const roll = (sides) => {
    state = (1664525 * state + 1013904223) >>> 0;
    return (state % sides) + 1;
  };
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
}

const veteran = Object.values(window.IRON_PIT_BROWSER_HEROES).find((hero) => hero.name === "Veteran");
const commoner = Object.values(window.IRON_PIT_BROWSER_MONSTERS).find((monster) => monster.name === "Commoner");
assert.ok(veteran, "2014 Veteran harness must be generated");
assert.ok(commoner, "2014 Commoner must be generated");

window.IRON_PIT_DICE = deterministicDice();
const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
  hero_ids: [veteran.id],
  monster_ids: [commoner.id],
});
assert.notEqual(battle.outcome, "active");
assert.ok(battle.events.some((event) => event.event_type === "attack"));
assert.equal(battle.setup.heroes[0].state.template.source.includes("2024"), false);
assert.equal(battle.setup.monsters[0].state.template.source.includes("2024"), false);

console.log("Pure 2014 generated browser fight smoke passed.");
