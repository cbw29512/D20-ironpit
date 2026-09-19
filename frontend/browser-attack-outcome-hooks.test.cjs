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

const calls = [];
window.IRON_PIT_BROWSER_TOPPLE = {
  resolve() {
    calls.push("topple");
    return { saveRoll: { total: 9 }, saveDc: 15, saveSucceeded: false, applied: true };
  },
};
window.IRON_PIT_BROWSER_SAP = {
  applyWeapon() { calls.push("sap"); return true; },
};
window.IRON_PIT_BROWSER_TACTICAL_MASTER = {
  apply() { calls.push("tactical"); return true; },
};
window.IRON_PIT_BROWSER_VEX = {
  apply() { calls.push("vex"); return true; },
};
window.IRON_PIT_BROWSER_GRAZE = {
  rawDamage() { calls.push("graze"); return 4; },
};
window.IRON_PIT_BROWSER_STUDIED_ATTACKS = {
  apply() { calls.push("studied"); return true; },
};

load("browser-ability-hooks.js");
load("browser-attack-outcome-hooks.js");

const H = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
assert.deepEqual(
  H.abilitiesFor(H.PHASES.ON_HIT).map((item) => [item.id, item.priority, item.rulesets]),
  [
    ["topple-hit", 100, ["2024"]],
    ["sap-hit", 110, ["2024"]],
    ["vex-hit", 120, ["2024"]],
  ],
);
assert.deepEqual(
  H.abilitiesFor(H.PHASES.ON_MISS).map((item) => [item.id, item.priority, item.rulesets]),
  [
    ["graze-miss", 100, ["2024"]],
    ["studied-attacks-miss", 110, ["2024"]],
  ],
);

const state = (ruleset = "2024") => ({
  template: { ruleset, name: "Tester" },
  current_hp: 20,
  temporary_hp: 0,
});
const attacker = { combatant_id: "attacker", state: state() };
const target = { combatant_id: "target", state: state() };
const attack = { id: "test-weapon", name: "Test Weapon", damageType: "slashing" };

{
  calls.length = 0;
  const outcome = {
    applied: [], sapApplied: "", vexApplied: false,
    topple: { saveRoll: null, saveDc: null, saveSucceeded: null, applied: false },
  };
  const result = H.runPhase(H.PHASES.ON_HIT, {
    sequence: 7, member: attacker, attacker, target, originalTarget: target,
    attack, round: 2, living: true, damageRoll: { total: 8 }, outcome, events: [],
  });

  assert.deepEqual(calls, ["topple", "sap", "vex"]);
  assert.equal(result.sequence, 7);
  assert.equal(result.claimed, false);
  assert.deepEqual(result.events, []);
  assert.equal(outcome.topple.applied, true);
  assert.deepEqual(outcome.applied, ["prone"]);
  assert.equal(outcome.sapApplied, "weapon");
  assert.equal(outcome.vexApplied, true);
}

{
  calls.length = 0;
  const outcome = {
    damageRoll: null, damageComponents: [], damageOutcome: null, studiedApplied: false,
  };
  const result = H.runPhase(H.PHASES.ON_MISS, {
    sequence: 9, member: attacker, attacker, target, originalTarget: target,
    attack, round: 3, setup: { heroes: [attacker], monsters: [target] }, outcome,
    adjustedDamage: (_state, amount) => amount,
    applyDamage: (defender, amount) => {
      defender.current_hp -= amount;
      return "damaged";
    },
    events: [],
  });

  assert.deepEqual(calls, ["graze", "studied"]);
  assert.equal(result.sequence, 9);
  assert.equal(result.claimed, false);
  assert.deepEqual(result.events, []);
  assert.equal(outcome.damageRoll.total, 4);
  assert.equal(outcome.damageComponents[0].applied_total, 4);
  assert.equal(outcome.damageOutcome, "damaged");
  assert.equal(outcome.studiedApplied, true);
  assert.equal(target.state.current_hp, 16);
}

{
  const savedGraze = window.IRON_PIT_BROWSER_GRAZE;
  delete window.IRON_PIT_BROWSER_GRAZE;
  const grazer = { combatant_id: "grazer", state: state("2024") };
  grazer.state.template.weapon_masteries = ["greatsword"];
  const grazeAttack = { ...attack, weaponId: "greatsword", masteryProperty: "Graze" };
  assert.throws(() => H.runPhase(H.PHASES.ON_MISS, {
    sequence: 1, member: grazer, attacker: grazer, target, originalTarget: target,
    attack: grazeAttack, round: 1, setup: { heroes: [grazer], monsters: [target] },
    outcome: { damageRoll: null, damageComponents: [], damageOutcome: null, studiedApplied: false },
    adjustedDamage: (_state, amount) => amount, applyDamage: () => "damaged", events: [],
  }), (error) => {
    assert.match(error.message, /Ability hook "graze-miss" failed during resolve/);
    assert.match(error.cause?.message || "", /Applicable Graze attack outcome requires its browser runtime/);
    return true;
  });
  window.IRON_PIT_BROWSER_GRAZE = savedGraze;
}

{
  calls.length = 0;
  const legacy = { combatant_id: "legacy", state: state("2014") };
  const outcome = {
    applied: [], sapApplied: "", vexApplied: false,
    topple: { saveRoll: null, saveDc: null, saveSucceeded: null, applied: false },
  };
  H.runPhase(H.PHASES.ON_HIT, {
    sequence: 1, member: legacy, attacker: legacy, target, originalTarget: target,
    attack, round: 1, living: true, damageRoll: { total: 8 }, outcome, events: [],
  });
  assert.deepEqual(calls, [], "2024 post-roll hooks must not cross into the 2014 ruleset");
}

const attackSource = fs.readFileSync(path.join(__dirname, "browser-attack.js"), "utf8");
assert.match(attackSource, /runOutcomePhase\("ON_HIT"/);
assert.match(attackSource, /runOutcomePhase\("ON_MISS"/);
assert.doesNotMatch(attackSource, /TOP\(\)\.resolve/);
assert.doesNotMatch(attackSource, /GRZ\(\)\.rawDamage/);
assert.doesNotMatch(attackSource, /STUDY\(\)\.apply/);
assert.doesNotMatch(attackSource, /TACTICAL_MASTER.*\.apply/);
assert.doesNotMatch(attackSource, /BROWSER_VEX.*\.apply/);

for (const htmlPath of [path.join(__dirname, "index.html"), path.join(__dirname, "..", "index.html")]) {
  const html = fs.readFileSync(htmlPath, "utf8");
  assert.ok(html.indexOf("browser-ability-hooks.js") < html.indexOf("browser-attack-outcome-hooks.js"));
  assert.ok(html.indexOf("browser-topple.js") < html.indexOf("browser-attack-outcome-hooks.js"));
  assert.ok(html.indexOf("browser-attack-outcome-hooks.js") < html.indexOf("browser-turn.js"));
}

console.log("Browser attack hit/miss hook sequencing regressions passed.");
