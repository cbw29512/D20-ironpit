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

window.IRON_PIT_DICE = {
  roll: (sides) => {
    assert.equal(sides, 6);
    return 5;
  },
};

load("browser-ability-hooks.js");
load("browser-recharge.js");

const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
const registered = hooks.abilitiesFor(hooks.PHASES.TURN_START);
assert.equal(registered.some((ability) => ability.id === "recharge"), true);

const member = {
  combatant_id: "recharge-monster",
  state: {
    resources: { breath: 0 },
    template: {
      name: "Recharge Monster",
      ruleset: "2024",
      recharge_rules: [{ resourceId: "breath", minimumRoll: 5, dieSize: 6 }],
    },
  },
};
const result = hooks.runPhase(hooks.PHASES.TURN_START, {
  sequence: 10,
  round: 2,
  member,
  setup: { heroes: [], monsters: [member] },
  turnKey: "2:recharge-monster",
  events: [],
});

assert.equal(result.events.length, 1);
assert.equal(result.events[0].recharge_succeeded, true);
assert.equal(result.sequence, 11);
assert.equal(result.claimed, false);
assert.equal(member.state.resources.breath, 1);

const turnSource = fs.readFileSync(path.join(__dirname, "browser-turn.js"), "utf8");
assert.equal(turnSource.includes("resolveStartOfTurn"), false);
assert.match(turnSource, /PHASES\.TURN_START/);

console.log("Browser turnStart Recharge hook migration passed.");
