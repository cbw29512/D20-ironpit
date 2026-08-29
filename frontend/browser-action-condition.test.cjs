"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-timed-conditions.js",
  "browser-attack.js", "browser-saves.js",
]) load(file);

const Q = window.IRON_PIT_BROWSER_CONDITION_RULES;
const E = window.IRON_PIT_ACTION_ECONOMY;
const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const V = window.IRON_PIT_BROWSER_SAVES;
const template = () => structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
const member = (id) => ({ combatant_id: id, side: "heroes", position_ft: 0, state: S.buildState(template()) });
window.IRON_PIT_DICE = { roll: (sides) => sides === 20 ? 19 : 1, rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? 19 : 1) };

{
  const stunned = member("stunned"); stunned.state.active_effect_ids.push("stunned"); stunned.state.reaction_available = false;
  S.beginTurn(stunned.state);
  assert.equal(stunned.state.reaction_available, true, "Reaction resource refreshes at start of turn");
  for (const cost of ["action", "bonus_action", "reaction"]) assert.equal(E.available(stunned.state, cost), false);
  assert.equal(Q.speedZero(stunned.state), false, "Stunned does not itself set Speed to 0 in the supported 2024 core");
  assert.equal(stunned.state.movement_remaining_ft, stunned.state.template.speed_ft);
  assert.equal(V.resolveSavingThrow(stunned.state, "strength", 1).succeeded, false);
}
{
  const paralyzed = member("paralyzed"); paralyzed.state.active_effect_ids.push("paralyzed"); S.beginTurn(paralyzed.state);
  assert.equal(Q.speedZero(paralyzed.state), true); assert.equal(paralyzed.state.movement_remaining_ft, 0);
  for (const cost of ["action", "bonus_action", "reaction"]) assert.equal(E.available(paralyzed.state, cost), false);
  assert.equal(V.resolveSavingThrow(paralyzed.state, "dexterity", 1).succeeded, false);
}
{
  const attacker = member("attacker"), stunned = member("stunned-target"); stunned.state.active_effect_ids.push("stunned");
  const attack = attacker.state.template.attacks.find((item) => item.kind === "melee");
  const event = A.resolveAttack(1, 1, attacker, stunned, attack, 5, { spendAction: false });
  assert.equal(event.attack_roll.mode, "advantage"); assert.equal(event.critical, false, "Stunned is not an automatic critical");
}
{
  const attacker = member("attacker-2"), paralyzed = member("paralyzed-target"); paralyzed.state.active_effect_ids.push("paralyzed");
  const attack = attacker.state.template.attacks.find((item) => item.kind === "melee");
  const event = A.resolveAttack(1, 1, attacker, paralyzed, attack, 5, { spendAction: false });
  assert.equal(event.attack_roll.mode, "advantage"); assert.equal(event.critical, true, "Paralyzed close hit is an automatic critical");
}
console.log("Browser condition/action-economy integration regressions passed.");
