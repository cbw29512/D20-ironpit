"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

try {
  global.window = globalThis;
  const file = path.join(__dirname, "battlefield-passive-states.js");
  vm.runInThisContext(fs.readFileSync(file, "utf8"), { filename: file });
  const member = {combatant_id:"2014-frog",state:{
    template:{source_trait_names:["Amphibious","Standing Leap"],passive_modifier_grants:[],
      environment_context_reactions:[]},active_modifiers:[],active_effect_ids:[],
  }};
  const projected = window.IRON_PIT_BATTLEFIELD_PASSIVE_STATES.permanentPassiveStates(
    member, {heroes:[],monsters:[member]});
  for (const name of ["Amphibious","Standing Leap"]) {
    const badge = projected.find(item => item.label === name);
    assert.ok(badge, "Printed arena-neutral trait must have a card status: " + name);
    assert.equal(badge.active, false);
    assert.equal(badge.lane, "buff");
  }
  const replay = fs.readFileSync(path.join(__dirname, "battlefield-replay.js"), "utf8");
  assert.match(replay, /passive\.active \? "" : " is-inactive"/,
    "Inactive source traits must render as greyed card badges");
  console.log("Arena-neutral trait badge projection and greying verified.");
} catch (error) {
  console.error("Arena-neutral card-renderer regression failed.", error);
  process.exitCode = 1;
}
