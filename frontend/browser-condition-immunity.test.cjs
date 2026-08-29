"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-grapple.js", "browser-timed-conditions.js",
  "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-attack.js",
]) load(file);

const queuedDice = (values, fallback = 10) => {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
};
const S = window.IRON_PIT_BROWSER_STATE;
const G = window.IRON_PIT_BROWSER_GRAPPLE;
const T = window.IRON_PIT_BROWSER_TIMED;
const A = window.IRON_PIT_BROWSER_ATTACK;
const heroTemplate = window.IRON_PIT_BROWSER_HEROES["aldric-vane-l1"];
const member = (id, template, position = 0) => ({ combatant_id: id, side: "heroes", position_ft: position, state: S.buildState(structuredClone(template)) });

{
  const target = member("hero-1", heroTemplate);
  target.state.template.condition_immunities = ["poisoned"];
  assert.equal(T.apply(target.state, "poisoned", "centipede"), null);
  assert.equal(target.state.active_effect_ids.includes("poisoned"), false);
  assert.equal(target.state.timed_effects.length, 0);
}

{
  const target = member("hero-1", heroTemplate);
  target.state.template.condition_immunities = ["grappled"];
  assert.deepEqual(G.apply(target.state, "crocodile", 12, 5, true), []);
  assert.equal(target.state.grapple_sources.length, 0);
  assert.equal(target.state.active_effect_ids.includes("restrained"), false);
}

{
  const target = member("hero-1", heroTemplate);
  target.state.template.condition_immunities = ["restrained"];
  assert.deepEqual(G.apply(target.state, "crocodile", 12, 5, true), ["grappled"]);
  assert.equal(target.state.grapple_sources[0].restrains, false);
  assert.equal(target.state.active_effect_ids.includes("grappled"), true);
  assert.equal(target.state.active_effect_ids.includes("restrained"), false);
}

{
  const attacker = member("attacker", heroTemplate, 5);
  const target = member("target", heroTemplate, 0);
  target.state.template.condition_immunities = ["prone"];
  const knockdown = { ...attacker.state.template.attacks[0], proneMaxSize: "large", bonus: 20 };
  window.IRON_PIT_DICE = queuedDice([10, 1, 1, 1, 1]);
  const event = A.resolveAttack(1, 1, attacker, target, knockdown, 5);
  assert.equal(event.hit, true);
  assert.equal(event.applied_condition_ids.includes("prone"), false);
  assert.equal(target.state.active_effect_ids.includes("prone"), false);
}

{
  const target = member("target", heroTemplate);
  target.state.template.condition_immunities = ["prone"];
  const outcome = A.applyDamage(target.state, target.state.current_hp, false);
  assert.equal(outcome, "unconscious");
  assert.equal(target.state.is_unconscious, true);
  assert.equal(target.state.active_effect_ids.includes("prone"), false);
}

console.log("Browser condition immunity regressions passed.");
