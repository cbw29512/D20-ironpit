"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters-generated.js", "browser-condition-immunity.js",
  "browser-condition-rules.js", "browser-action-economy.js", "browser-modifiers.js",
  "browser-grapple.js", "browser-grid-geometry.js", "browser-state.js", "browser-rolls.js",
  "browser-timed-conditions.js", "browser-source-bound-effects.js", "browser-undead-fortitude.js",
  "browser-zero-hp.js", "browser-ability-hooks.js", "browser-attack-outcome.js", "browser-attack.js",
  "browser-saves.js", "browser-spellcasting.js", "browser-healing.js",
  "browser-turn-creature-effects.js", "browser-cleric-channel.js",
]) load(file);

const HEROES = window.IRON_PIT_BROWSER_HEROES;
const MONSTERS = window.IRON_PIT_BROWSER_MONSTERS;
const STATE = window.IRON_PIT_BROWSER_STATE;
const HEALING = window.IRON_PIT_BROWSER_HEALING;
const CHANNEL = window.IRON_PIT_BROWSER_CLERIC_CHANNEL;

const member = (template, id, side, position) => ({
  combatant_id: id,
  side,
  position_ft: position,
  state: STATE.buildState(structuredClone(template)),
});
const fixedDice = (values) => {
  const queue = [...values];
  window.IRON_PIT_DICE = {
    roll: (sides) => {
      assert.ok(queue.length, `fixed dice exhausted before d${sides}`);
      const value = queue.shift();
      assert.ok(value >= 1 && value <= sides);
      return value;
    },
    rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
  };
};
const emptySlots = (state) => {
  for (const id of Object.keys(state.resources)) {
    if (id.startsWith("spell-slot-")) state.resources[id] = 0;
  }
};

const cleric17 = HEROES["seraphine-dawnshield-l17"];
const cleric18 = HEROES["seraphine-dawnshield-l18"];
assert.ok(cleric17 && cleric18);
assert.equal(cleric17.feature_dice_counts["divine-spark"], 3);
assert.equal(cleric18.feature_dice_counts["divine-spark"], 4);
assert.equal(cleric17.healing_dice_maximizer.source_id, "supreme-healing");
assert.equal(cleric17.canonical_prepared_spells.at(-1).id, "astral-projection");
assert.equal(cleric18.canonical_prepared_spells.at(-1).id, "word-of-recall");

{
  const cleric = member(cleric17, "cleric", "heroes", 0);
  const ally = member(HEROES["karnok-stoneward-l1"], "ally", "heroes", 5);
  ally.state.current_hp = 1;
  const action = cleric.state.template.healingActions.find((item) => item.id === "cure-wounds");
  fixedDice([1, 1]);
  const event = HEALING.resolve(1, 1, cleric, ally, action, "1:cleric");
  assert.deepEqual(event.healing_roll.rolls, [8, 8]);
  assert.equal(event.healing_roll.total, 24);
}

{
  const cleric = member(cleric17, "cleric", "heroes", 0);
  const ally = member(HEROES["karnok-stoneward-l1"], "ally", "heroes", 5);
  ally.state.current_hp = 0;
  ally.state.is_unconscious = true;
  cleric.state.template.traits = cleric.state.template.traits.filter((item) => item !== "life-domain");
  emptySlots(cleric.state);
  fixedDice([]);
  const result = CHANNEL.resolve(1, 1, cleric, { heroes: [cleric, ally], monsters: [] });
  assert.equal(result.events[0].feature_id, "divine-spark");
  assert.deepEqual(result.events[0].healing_roll.rolls, [8, 8, 8]);
  assert.equal(result.events[0].healing_roll.total, 29);
}

{
  const cleric = member(cleric18, "cleric", "heroes", 0);
  const goblin = member(MONSTERS["srd-goblin-warrior"], "goblin", "monsters", 10);
  cleric.state.template.traits = cleric.state.template.traits.filter((item) => item !== "life-domain");
  emptySlots(cleric.state);
  fixedDice([1, 2, 3, 4, 1]);
  const result = CHANNEL.resolve(1, 1, cleric, { heroes: [cleric], monsters: [goblin] });
  assert.equal(result.events[0].feature_id, "divine-spark");
  assert.equal(result.events[0].damage_roll.notation, "4d8+5");
  assert.deepEqual(result.events[0].damage_roll.rolls, [1, 2, 3, 4]);
}

console.log("Browser Cleric 17-18 Supreme Healing and Divine Spark scaling regressions passed.");
