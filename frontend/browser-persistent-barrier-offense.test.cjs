"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
global.window = globalThis;
const load = (filename) => vm.runInThisContext(
  fs.readFileSync(`frontend/${filename}`, "utf8"), {filename},
);

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
  spend: (state) => { state.action_available = false; },
};
window.IRON_PIT_BROWSER_GRID_GEOMETRY = {
  occupiedCells: (position) => [[position.x, position.y]],
};
window.IRON_PIT_BROWSER_GRID_BARRIERS = {
  edgeKey: (first, second) => [first,second].map((p) => `${p.x},${p.y}`).sort().join("|"),
  cleanup: () => [],
};
window.IRON_PIT_BROWSER_FORMATION = {
  saveDistance: (source, target) => Math.max(
    Math.abs(source.state.position.x - target.state.position.x),
    Math.abs(source.state.position.y - target.state.position.y),
  ) * 5,
};
window.IRON_PIT_BROWSER_SAVES = {
  resolveAction: (seq, round, actor, target, save, distance, options) => {
    assert.equal(save.dc, 17);
    assert.equal(save.damageDiceCount, 10);
    assert.equal(save.saveAbility, "dexterity");
    assert.equal(options.spendAction, false);
    assert.equal(options.spendResource, false);
    assert.equal(options.checkResource, false);
    assert.ok(distance <= 60);
    const before = target.state.current_hp;
    target.state.current_hp = Math.max(0, before - 10);
    return {
      sequence: seq, round_number: round, actor_id: actor.combatant_id,
      target_id: target.combatant_id, save_dc: save.dc, event_type: "saving_throw",
    };
  },
};
window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH = {
  chain: (sequence, _round, _actor, event) => ({events:[event], sequence}),
};
load("browser-main-action-profiles.js");
load("browser-main-action-selection.js");
load("browser-persistent-barriers.js");
load("browser-persistent-barrier-offense.js");
load("browser-persistent-barrier-offense-provider.js");

const action = {
  id: "wall-of-ice", name: "Wall of Ice", level: 0, actionCost: "action",
  resourceId: "wall-of-ice", resourceCost: 1, castRangeFt: 60,
  minSections: 1, maxSections: 3, sectionsMustBeContiguous: true,
  sectionLengthFt: 10, sectionHeightFt: 10, armorClass: 5,
  hitPointsPerSection: 30, durationRounds: 10, concentration: false,
  damageImmunities: ["cold"], damageVulnerabilities: ["fire"],
  onCreationSave: {
    id: "wall-of-ice", name: "Wall of Ice", saveAbility: "dexterity",
    dc: 17, damageDiceCount: 10, damageDiceSize: 6, damageType: "cold",
    successDamage: "half", range: 60, targetScope: "all-other-creatures",
  },
  endsOnSourceIncapacitated: true, endsOnSourceDeath: true,
};
const actor = {
  combatant_id: "owner", side: "monsters",
  state: {
    position: {x:2,y:7}, action_available: true, current_hp: 180, is_alive: true,
    resources: {"wall-of-ice":1},
    template: {ruleset:"2014", name:"Generic Wall Owner", size:"large",
      persistent_barrier_actions:[action]},
  },
};
const target = {
  combatant_id: "target", side: "heroes",
  state: {position:{x:8,y:5}, current_hp:35, is_alive:true, is_dead:false,
    template:{name:"Target",size:"medium",ruleset:"2014"}},
};
const setup = {heroes:[target], monsters:[actor],
  map_definition: {width_squares:24,height_squares:16,support_materials:[]},
  persistent_barriers: []};
const selector = window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
const ctx = {sequence:1, round:1, turnKey:"1:owner", member:actor, setup};
const unchanged = JSON.stringify(action);
const choices = selector.discoverCandidates("normalPostMove",ctx);
assert.equal(choices.length,1);
assert.equal(choices[0].category,"barrier");
const selected = selector.selectCandidate("normalPostMove",choices);
const resolved = selector.resolveCandidate("normalPostMove",selected,ctx);
assert.equal(resolved.events[0].feature_id,"wall-of-ice");
assert.equal(resolved.events.filter((e) => e.event_type === "saving_throw").length,1);
assert.equal(target.state.current_hp,25);
assert.equal(actor.state.resources["wall-of-ice"],0);
assert.equal(actor.state.action_available,false);
assert.equal(setup.persistent_barriers[0].sections[0].current_hp,30);
assert.equal(JSON.stringify(action),unchanged);

actor.state.action_available = true;
target.state.position = {x:23,y:15};
actor.state.position = {x:20,y:13};
actor.state.resources["wall-of-ice"] = 1;
assert.ok(window.IRON_PIT_BROWSER_BARRIER_OFFENSE.choose(actor,setup));
actor.state.resources["wall-of-ice"] = 0;
assert.equal(window.IRON_PIT_BROWSER_BARRIER_OFFENSE.choose(actor,setup),null);
console.log("Browser source-neutral offensive barrier cast and save provider passed.");
