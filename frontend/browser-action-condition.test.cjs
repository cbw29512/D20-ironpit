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
  const petrified = member("petrified"); petrified.state.active_effect_ids.push("petrified"); S.beginTurn(petrified.state);
  assert.equal(Q.speedZero(petrified.state), true); assert.equal(petrified.state.movement_remaining_ft, 0);
  for (const cost of ["action", "bonus_action", "reaction"]) assert.equal(E.available(petrified.state, cost), false);
  assert.equal(V.resolveSavingThrow(petrified.state, "strength", 1).succeeded, false);
  assert.equal(V.resolveSavingThrow(petrified.state, "dexterity", 1).succeeded, false);
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
{
  for (const condition of ["incapacitated", "paralyzed", "petrified", "stunned"]) {
    const attacker = member(`monster-${condition}`); attacker.side = "monsters"; attacker.position_ft = 30;
    const disabled = member(`${condition}-target`); disabled.position_ft = 25; disabled.state.active_effect_ids.push(condition);
    const active = member("active-target"); active.position_ft = 0;
    const setup = { heroes: [disabled, active], monsters: [attacker] };
    assert.equal(S.nearestTarget(attacker, setup), active, `${condition} target must be deferred while an active threat remains`);
    active.state.current_hp = 0; active.state.is_unconscious = true;
    assert.equal(S.nearestTarget(attacker, setup), disabled, `${condition} target becomes priority when no active threat remains`);
  }
}
{
  for (const condition of ["blinded", "frightened", "poisoned", "prone", "restrained"]) {
    const attacker = member(`monster-partial-${condition}`); attacker.side = "monsters"; attacker.position_ft = 30;
    const debuffed = member(`${condition}-target`); debuffed.position_ft = 25; debuffed.state.active_effect_ids.push(condition);
    const healthy = member("healthy-target"); healthy.position_ft = 0;
    const setup = { heroes: [debuffed, healthy], monsters: [attacker] };
    assert.equal(S.nearestTarget(attacker, setup), debuffed, `${condition} must remain an active-threat condition`);
  }
}
{
  const attacker = member("pack-attacker"); attacker.side = "monsters";
  attacker.state.template.traits = ["pack-tactics"];
  const ally = member("pack-ally"); ally.side = "monsters"; ally.state.active_effect_ids.push("stunned");
  const target = member("pack-target");
  const setup = { heroes: [target], monsters: [attacker, ally] };
  assert.equal(S.active(ally), false, "Incapacitated ally is not an active combatant");
  assert.equal(S.packTactics(attacker, setup), false, "Incapacitated ally cannot enable Pack Tactics");
  ally.state.active_effect_ids = ["poisoned"];
  assert.equal(S.active(ally), true, "partially debuffed ally remains active");
  assert.equal(S.packTactics(attacker, setup), true, "partially debuffed ally can still enable Pack Tactics");
}
console.log("Browser condition/action-economy integration regressions passed.");

// Keep newer condition subsystems inside an already mandatory CI entry point.
require("./browser-condition-removal.test.cjs");
require("./browser-condition-lifecycle.test.cjs");
