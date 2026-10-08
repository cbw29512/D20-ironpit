"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-opening-modifiers.js");
load("browser-defensive-modifier-rules.js");
load("browser-state.js");
load("browser-condition-immunity.js");
const template = {id:"ally-ward-test",name:"Ally Ward Test",passive_modifier_grants:[
  {source_id:"ally-ward",source_name:"Ally Ward",kind:"condition-immunity",
    condition_id:"frightened",requires_active_ally:true},
]};
const state = {template,active_modifiers:window.IRON_PIT_BROWSER_OPENING_MODIFIERS.build(template),active_effect_ids:[]};
const rules = window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS;
assert.equal(state.active_modifiers[0].requires_active_ally,true);
assert.equal(rules.conditionImmune(state,"frightened"),false);
assert.equal(rules.conditionImmune(state,"frightened",null,{activeAllyPresent:true}),true);
assert.equal(rules.conditionImmune(state,"frightened",null,{activeAllyPresent:false}),false);
assert.equal(rules.conditionImmune(state,"charmed",null,{activeAllyPresent:true}),false);
const owner = { combatant_id: "owner", side: "monsters", state: {
  ...state, current_hp: 30, is_alive: true, is_dead: false, is_unconscious: false,
}};
const ally = { combatant_id: "ally", side: "monsters", state: {
  template: { kind: "monster" }, active_effect_ids: [], current_hp: 20,
  is_alive: true, is_dead: false, is_unconscious: false,
}};
const setup = { monsters: [owner, ally], heroes: [] };
const immunity = window.IRON_PIT_BROWSER_CONDITION_IMMUNITY;
assert.equal(immunity.immune(state, "frightened", null, { member: owner, setup }), true);
ally.state.current_hp = 0;
assert.equal(immunity.immune(state, "frightened", null, { member: owner, setup }), false);
ally.state.current_hp = 20;
assert.equal(immunity.immune(state, "frightened", null, { member: owner, setup }), true);
assert.equal(immunity.immune(state, "charmed", null, { member: owner, setup }), false);
console.log("Conditional active-ally immunity parity passed.");
