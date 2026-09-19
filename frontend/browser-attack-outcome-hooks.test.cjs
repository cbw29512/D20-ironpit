"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

const callOrder = [];
window.IRON_PIT_BROWSER_WEAPON_MASTERY = {
  mastered: (state, attack) => (state.template.weapon_masteries || []).includes(attack.weaponId),
  active(state, attack, mastery) {
    const replaced = (state.template.tactical_master_sap_weapon_ids || []).includes(attack.weaponId);
    return attack.masteryProperty === mastery
      && (state.template.weapon_masteries || []).includes(attack.weaponId)
      && !replaced;
  },
};
window.IRON_PIT_BROWSER_SAVES = {
  resolveSavingThrow: () => {
    callOrder.push("topple");
    return { roll: { total: 5 }, succeeded: false };
  },
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_TIMED = {
  apply: () => { callOrder.push("sap"); return true; },
  removeEffect: () => {},
};
window.IRON_PIT_BROWSER_MODIFIERS = {
  add: (_state, modifier) => { callOrder.push(modifier.source_effect_id); },
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_target, amount) => amount,
  applyDamage: (target, amount) => {
    callOrder.push("graze");
    target.current_hp -= amount;
    return "applied";
  },
};

load("browser-ability-hooks.js");
load("browser-attack-outcome.js");
load("browser-graze.js");
load("browser-studied-attacks.js");
load("browser-tactical-master.js");
load("browser-topple.js");
load("browser-vex.js");

for (const moduleName of [
  "IRON_PIT_BROWSER_GRAZE",
  "IRON_PIT_BROWSER_STUDIED_ATTACKS",
  "IRON_PIT_BROWSER_SAP",
  "IRON_PIT_BROWSER_TOPPLE",
  "IRON_PIT_BROWSER_VEX",
]) window[moduleName].installAbilityHooks();

const H = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
const O = window.IRON_PIT_BROWSER_ATTACK_OUTCOME;
const member = (id, template = {}) => ({
  combatant_id: id,
  state: {
    template: {
      name: id, ruleset: "2024", level: 9, weapon_masteries: [],
      tactical_master_sap_weapon_ids: [], studied_attacks: false, ...template,
    },
    current_hp: 30, is_alive: true, is_dead: false,
    active_effect_ids: [], timed_effects: [], active_modifiers: [],
  },
});

assert.deepEqual(
  H.abilitiesFor(H.PHASES.ON_HIT).map((item) => [item.id, item.priority]),
  [["topple-mastery", 10], ["sap-outcome", 20], ["weapon-mastery-vex", 30]],
);
assert.deepEqual(
  H.abilitiesFor(H.PHASES.ON_MISS).map((item) => [item.id, item.priority]),
  [["graze-mastery", 10], ["studied-attacks", 20]],
);

{
  callOrder.length = 0;
  const attacker = member("miss-attacker", { studied_attacks: true, weapon_masteries: ["greatsword"] });
  const target = member("miss-target");
  const attack = {
    id: "greatsword", weaponId: "greatsword", name: "Greatsword",
    masteryProperty: "Graze", attackAbilityModifier: 4, damageType: "slashing",
  };
  const outcome = O.create();
  const result = H.runPhase(H.PHASES.ON_MISS, {
    sequence: 7, round: 2, member: attacker, target, originalTarget: target,
    attack, setup: { heroes: [attacker], monsters: [target] }, attackOutcome: outcome, events: [],
  });
  assert.equal(result.sequence, 7);
  assert.deepEqual(result.events, [], "outcome hooks stay inside the aggregate attack event");
  assert.deepEqual(callOrder, ["graze", "studied-attacks"], "Graze must resolve before Studied Attacks");
  assert.equal(outcome.damageRoll.total, 4);
  assert.equal(outcome.damageOutcome, "applied");
  assert.equal(outcome.studiedApplied, true);
  assert.equal(target.state.current_hp, 26);
}

{
  callOrder.length = 0;
  const attacker = member("hit-attacker", {
    weapon_masteries: ["shortsword"],
    tactical_master_sap_weapon_ids: ["shortsword"],
  });
  const target = member("hit-target");
  const attack = {
    id: "shortsword", weaponId: "shortsword", name: "Shortsword",
    masteryProperty: "Vex", attackAbilityModifier: 4, damageType: "piercing",
  };
  const outcome = O.create();
  outcome.damageRoll = { total: 8 };
  const result = H.runPhase(H.PHASES.ON_HIT, {
    sequence: 4, round: 1, member: attacker, target, originalTarget: target,
    attack, setup: { heroes: [attacker], monsters: [target] }, attackOutcome: outcome, events: [],
  });
  assert.deepEqual(result.events, []);
  assert.deepEqual(callOrder, ["sap"], "Tactical Master replacement suppresses the weapon's normal Vex mastery");
  assert.equal(outcome.sapApplied, "tactical");
  assert.equal(outcome.vexApplied, false);
}

{
  callOrder.length = 0;
  const attacker = member("vex-attacker", { weapon_masteries: ["shortsword"] });
  const target = member("vex-target");
  const attack = {
    id: "shortsword", weaponId: "shortsword", name: "Shortsword",
    masteryProperty: "Vex", attackAbilityModifier: 4, damageType: "piercing",
  };
  const outcome = O.create();
  outcome.damageRoll = { total: 8 };
  H.runPhase(H.PHASES.ON_HIT, {
    sequence: 5, round: 1, member: attacker, target, originalTarget: target,
    attack, setup: { heroes: [attacker], monsters: [target] }, attackOutcome: outcome, events: [],
  });
  assert.deepEqual(callOrder, ["weapon-mastery-vex"]);
  assert.equal(outcome.sapApplied, "");
  assert.equal(outcome.vexApplied, true);
}

{
  callOrder.length = 0;
  const attacker = member("topple-attacker", { weapon_masteries: ["maul"] });
  const target = member("topple-target");
  const attack = {
    id: "maul", weaponId: "maul", name: "Maul",
    masteryProperty: "Topple", attackAbilityModifier: 4, damageType: "bludgeoning",
  };
  const outcome = O.create();
  outcome.damageRoll = { total: 9 };
  H.runPhase(H.PHASES.ON_HIT, {
    sequence: 1, round: 1, member: attacker, target, originalTarget: target,
    attack, setup: { heroes: [attacker], monsters: [target] }, attackOutcome: outcome, events: [],
  });
  assert.deepEqual(callOrder, ["topple"]);
  assert.equal(outcome.topple.applied, true);
  assert.deepEqual(outcome.appliedConditions, ["prone"]);
}

const attackSource = fs.readFileSync(path.join(__dirname, "browser-attack.js"), "utf8");
for (const forbidden of [
  "rawGraze", "STUDY().apply", "TOP().resolve", "TM().apply",
  "IRON_PIT_BROWSER_VEX?.apply",
]) assert.equal(attackSource.includes(forbidden), false, "browser-attack.js still contains named outcome branch: " + forbidden);

console.log("Browser attack outcome hook regressions passed.");
