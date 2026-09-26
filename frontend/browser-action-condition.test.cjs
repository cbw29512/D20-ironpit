"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js", "browser-d20-bonus-dice.js", "browser-ability-checks.js",
  "browser-grapple.js", "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-timed-conditions.js",
  "browser-zero-hp.js", "browser-ability-hooks.js", "browser-attack-outcome.js", "browser-d20-test-override.js", "browser-miss-to-hit-override.js", "browser-attack.js", "browser-saving-throws.js", "browser-saves.js",
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
  assert.equal(S.packTactics(attacker, target, setup), false, "Incapacitated ally cannot enable Pack Tactics");
  ally.state.active_effect_ids = ["poisoned"];
  assert.equal(S.active(ally), true, "partially debuffed ally remains active");
  assert.equal(S.packTactics(attacker, target, setup), true, "partially debuffed ally can still enable Pack Tactics");
}
{
  const elusiveTemplate = structuredClone(window.IRON_PIT_BROWSER_HEROES["mara-quickstep-2014-l18"]);
  assert.ok(elusiveTemplate, "Level-18 2014 Mara must be present in the generated browser roster");
  const attacker = member("elusive-attacker");
  const elusive = { combatant_id: "mara-elusive", side: "monsters", position_ft: 0, state: S.buildState(elusiveTemplate) };
  const attack = attacker.state.template.attacks.find((item) => item.kind === "melee");

  const normal = A.resolveAttack(20, 1, attacker, elusive, attack, 5, { spendAction: false, advantage: 1 });
  assert.equal(normal.attack_roll.mode, "normal", "Elusive suppresses attack Advantage while Mara is not incapacitated");

  const attacker2 = member("elusive-attacker-2");
  const incapacitated = { combatant_id: "mara-stunned", side: "monsters", position_ft: 0, state: S.buildState(elusiveTemplate) };
  incapacitated.state.active_effect_ids.push("stunned");
  const advantaged = A.resolveAttack(21, 1, attacker2, incapacitated, attack, 5, { spendAction: false, advantage: 1 });
  assert.equal(advantaged.attack_roll.mode, "advantage", "Elusive stops suppressing Advantage while Mara is incapacitated");
}

{
  const attacker = member("stroke-attacker");
  attacker.state.template.miss_to_hit_override_resource_id = "stroke-of-luck";
  attacker.state.template.miss_to_hit_override_source_name = "Stroke of Luck";
  attacker.state.resources["stroke-of-luck"] = 1;
  const target = member("stroke-target");
  const attack = attacker.state.template.attacks.find((item) => item.kind === "melee");
  const values = [1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4];
  window.IRON_PIT_DICE = {
    roll: () => values.shift() ?? 4,
    rollMany: (count) => Array.from({ length: count }, () => values.shift() ?? 4),
  };
  const event = A.resolveAttack(30, 1, attacker, target, attack, 5, { spendAction: false });
  assert.equal(event.attack_roll.selected_roll, 1);
  assert.equal(event.hit, true);
  assert.equal(event.critical, false);
  assert.equal(event.turn_terminated, false);
  assert.equal(event.feature_id, "stroke-of-luck");
  assert.equal(attacker.state.resources["stroke-of-luck"], 0);
  assert.match(event.description, /Stroke of Luck turns the miss into a hit/);
}


{
  const attacker = member("stroke-2024-attacker");
  attacker.state.template.failed_d20_test_override_grants = [{
    source_id: "stroke-of-luck", source_name: "Stroke of Luck",
    resource_id: "stroke-of-luck", replacement_roll: 20,
    test_kinds: ["attack", "saving_throw", "ability_check"],
  }];
  attacker.state.resources["stroke-of-luck"] = 1;
  const target = member("stroke-2024-target");
  target.state.template.armor_class = 99;
  const attack = attacker.state.template.attacks.find((item) => item.kind === "melee");
  const values = [1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4];
  window.IRON_PIT_DICE = {
    roll: () => values.shift() ?? 4,
    rollMany: (count) => Array.from({ length: count }, () => values.shift() ?? 4),
  };
  const event = A.resolveAttack(31, 1, attacker, target, attack, 5, { spendAction: false });
  assert.equal(event.attack_roll.selected_roll, 20);
  assert.equal(event.hit, true, "replacement natural 20 automatically hits");
  assert.equal(event.critical, true, "replacement natural 20 is a critical hit");
  assert.equal(event.feature_id, "stroke-of-luck");
  assert.equal(attacker.state.resources["stroke-of-luck"], 0);
  assert.match(event.description, /Stroke of Luck turns the failed attack roll into a 20/);
}
{
  const saving = member("stroke-2024-save");
  saving.state.template.failed_d20_test_override_grants = [{
    source_id: "stroke-of-luck", source_name: "Stroke of Luck",
    resource_id: "stroke-of-luck", replacement_roll: 20,
    test_kinds: ["attack", "saving_throw", "ability_check"],
  }];
  saving.state.resources["stroke-of-luck"] = 1;
  window.IRON_PIT_DICE = { roll: () => 1, rollMany: (count) => Array.from({ length: count }, () => 1) };
  const save = V.resolveSavingThrow(saving.state, "strength", 20);
  assert.equal(save.roll.selected_roll, 20);
  assert.equal(save.succeeded, true);
  assert.equal(saving.state.resources["stroke-of-luck"], 0);
  assert.equal(window.IRON_PIT_BROWSER_D20_TEST_OVERRIDE.sourceNameForRoll(saving.state, save.roll), "Stroke of Luck");
}


{
  const checking = member("stroke-2024-check");
  checking.state.template.failed_d20_test_override_grants = [{
    source_id: "stroke-of-luck", source_name: "Stroke of Luck",
    resource_id: "stroke-of-luck", replacement_roll: 20,
    test_kinds: ["attack", "saving_throw", "ability_check"],
  }];
  checking.state.resources["stroke-of-luck"] = 1;
  const original = { notation: "1d20+2", rolls: [3], selected_roll: 3, modifier: 2, total: 5, mode: "normal", revisions: [] };
  const resolved = window.IRON_PIT_BROWSER_ABILITY_CHECKS.resolve(checking.state, "strength", original, 20);
  assert.equal(resolved.roll.selected_roll, 20);
  assert.equal(resolved.roll.total, 22);
  assert.equal(resolved.succeeded, true);
  assert.equal(checking.state.resources["stroke-of-luck"], 0);
}


{
  const checking = member("stroke-bonus-die-safety");
  checking.state.template.failed_d20_test_override_grants = [{
    source_id: "stroke-of-luck", source_name: "Stroke of Luck",
    resource_id: "stroke-of-luck", replacement_roll: 20,
    test_kinds: ["attack", "saving_throw", "ability_check"],
  }];
  checking.state.resources["stroke-of-luck"] = 1;
  const roll = {
    notation: "2d20 + 1d4", rolls: [1, 2, 4], selected_roll: 2,
    modifier: 0, total: 6, mode: "advantage", revisions: [],
  };
  const result = window.IRON_PIT_BROWSER_D20_TEST_OVERRIDE.apply(
    checking.state, roll, true, "attack",
  );
  assert.deepEqual(result.roll.rolls, [1, 20, 4], "replacement must target the selected d20, not the appended bonus die");
  assert.equal(result.roll.selected_roll, 20);
  assert.equal(result.roll.total, 24);
  assert.equal(result.roll.revisions.at(-1).replaced_die_index, 1);
}

console.log("Browser condition/action-economy integration regressions passed.");

// Keep newer condition/class subsystems inside an already mandatory CI entry point.
require("./browser-condition-removal.test.cjs");
require("./browser-condition-lifecycle.test.cjs");
require("./browser-fighter-progression.test.cjs");


{
  const checking = member("resource-backed-d20-check");
  checking.state.template.resource_backed_d20_bonus_dice = [{
    source_id: "peerless-skill",
    source_name: "Peerless Skill",
    resource_id: "bardic-inspiration",
    resource_cost: 1,
    dice_count: 1,
    dice_size: 10,
    test_kinds: ["ability_check"],
  }];
  checking.state.resources["bardic-inspiration"] = 5;
  window.IRON_PIT_DICE = { roll: () => 6, rollMany: (count) => Array.from({ length: count }, () => 6) };
  const original = { notation: "1d20+3", rolls: [7], selected_roll: 7, modifier: 3, total: 10, mode: "normal", revisions: [] };
  const resolved = window.IRON_PIT_BROWSER_ABILITY_CHECKS.resolve(checking.state, "dexterity", original, 16);
  assert.equal(resolved.succeeded, true);
  assert.equal(resolved.roll.total, 16);
  assert.deepEqual(resolved.roll.rolls, [7, 6]);
  assert.match(resolved.roll.notation, /Peerless Skill/);
  assert.equal(checking.state.resources["bardic-inspiration"], 4);
}
