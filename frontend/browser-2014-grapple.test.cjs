"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-condition-immunity.js");
load("browser-condition-rules.js");
load("browser-grapple.js");

const G = window.IRON_PIT_BROWSER_GRAPPLE;
const state = (ruleset) => ({
  template: { name: `${ruleset} test`, ruleset, speed_ft: 30, size: "medium", skill_bonuses: {} },
  active_effect_ids: [], grapple_sources: [], is_dead: false, is_unconscious: false,
});

{
  const victim2014 = state("2014");
  G.apply(victim2014, "grappler", 12, 5);
  assert.equal(G.speedIsZero(victim2014), true);
  assert.equal(G.attackDisadvantage(victim2014, "other"), 0, "2014 Grappled must not impose a generic attack penalty");

  const victim2024 = state("2024");
  G.apply(victim2024, "grappler", 12, 5);
  assert.equal(G.attackDisadvantage(victim2024, "other"), 1, "2024 Grappled retains its non-grappler attack penalty");
}

{
  const victim = { combatant_id: "victim", position_ft: 0, state: state("2014") };
  const grappler = { combatant_id: "grappler", position_ft: 5, state: state("2014") };
  G.apply(victim.state, grappler.combatant_id, 12, 5);
  grappler.state.active_effect_ids.push("stunned");
  G.cleanup({ heroes: [victim], monsters: [grappler] });
  assert.equal(victim.state.grapple_sources.length, 0, "2014 grapple must end when the grappler is Incapacitated");
  assert.equal(victim.state.active_effect_ids.includes("grappled"), false);
}

console.log("Browser 2014 Grappled RAW parity regressions passed.");
