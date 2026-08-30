"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-state.js", "browser-attack.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const E = window.IRON_PIT_ACTION_ECONOMY;
const heroTemplate = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];

function downedHero() {
  const state = S.buildState(structuredClone(heroTemplate));
  state.resources["relentless-endurance"] = 0;
  assert.equal(A.applyDamage(state, state.current_hp, false), "unconscious");
  assert.equal(state.current_hp, 0);
  return state;
}

{
  const state = downedHero();
  state.temporary_hp = 5;
  A.applyDamage(state, 1, false);
  assert.equal(state.temporary_hp, 4);
  assert.equal(state.death_save_failures, 1, "Temporary HP cannot hide damage-at-zero Death Save failure");
}

{
  const state = downedHero();
  state.temporary_hp = 20;
  A.applyDamage(state, 1, true);
  assert.equal(state.temporary_hp, 19);
  assert.equal(state.death_save_failures, 2, "critical damage at zero still causes two failures through Temporary HP");
}

{
  const state = downedHero();
  state.temporary_hp = state.template.max_hp;
  A.applyDamage(state, state.template.max_hp, false);
  assert.equal(state.is_dead, true, "Temporary HP cannot prevent instant death from damage at zero equal to max HP");
}

{
  const state = downedHero();
  state.reaction_available = false;
  S.refreshReaction(state);
  assert.equal(state.reaction_available, true, "Reaction refresh occurs at start of turn regardless of HP");
  assert.equal(E.available(state, "reaction"), false, "Incapacitated creature still cannot use the refreshed Reaction");
  state.current_hp = 1;
  state.is_unconscious = false;
  assert.equal(E.available(state, "reaction"), true, "after healing, the already-refreshed Reaction is usable before the next turn");
}

console.log("Browser zero-HP and start-turn lifecycle regressions passed.");
