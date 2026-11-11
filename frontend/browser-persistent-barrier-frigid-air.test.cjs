"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
global.window = globalThis;
const load = (file) => vm.runInThisContext(
  fs.readFileSync(`frontend/${file}`, "utf8"), {filename:file},
);
const edgeKey = (a,b) => [a,b].map((p) => `${p.x},${p.y}`).sort().join("|");
window.IRON_PIT_BROWSER_GRID_BARRIERS = {edgeKey};
window.IRON_PIT_ACTION_ECONOMY = {
  isIncapacitated: (state) => Boolean(state.is_unconscious),
};
window.IRON_PIT_BROWSER_SAVES = {
  resolveAction: (seq, round, actor, target, save, distance, options) => {
    assert.equal(save.name,"Wall of Ice");
    assert.equal(save.saveAbility,"constitution");
    assert.equal(save.dc,17);
    assert.equal(save.damageDiceCount,5);
    assert.equal(save.damageDiceSize,6);
    assert.equal(save.damageType,"cold");
    assert.equal(save.successDamage,"half");
    assert.equal(distance,0);
    assert.equal(options.spendAction,false);
    assert.equal(options.spendResource,false);
    assert.equal(options.checkResource,false);
    target.state.current_hp -= 5;
    return {
      sequence:seq, round_number:round, event_type:"saving_throw",
      actor_id:actor.combatant_id, target_id:target.combatant_id,
      feature_id:save.id,save_ability:save.saveAbility,save_dc:save.dc,
    };
  },
};
window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH = {
  chain: (next,_round,_actor,event) => ({events:[event],sequence:next}),
};
load("browser-persistent-barrier-frigid-air.js");
const owner = {
  combatant_id:"owner",side:"monsters",
  state:{current_hp:180,is_dead:false,is_unconscious:false},
};
const mover = {
  combatant_id:"mover",side:"heroes",
  state:{current_hp:35,is_alive:true,is_dead:false,position:{x:8,y:6}},
};
const save = {
  id:"wall-of-ice",name:"Wall of Ice",saveAbility:"constitution",
  dc:17,damageDiceCount:5,damageDiceSize:6,damageType:"cold",
  successDamage:"half",targetScope:"all-other-creatures",range:0,
};
const intact = {
  destroyed:false,current_hp:30,
  edges:[{first:{x:6,y:5},second:{x:6,y:6}}],
};
const destroyed = {
  destroyed:true,current_hp:0,
  edges:[{first:{x:8,y:5},second:{x:8,y:6}}],
  destroyed_section_crossing_save:save,
};
const wall = {
  barrier_id:"barrier:1",source_id:"owner",source_side:"monsters",
  ends_on_source_incapacitated:true,ends_on_source_death:true,expires_round:11,
  sections:[intact,destroyed],
};
const setup = {heroes:[mover],monsters:[owner],persistent_barriers:[wall]};
const runtime = window.IRON_PIT_BROWSER_BARRIER_AIR_CROSSING;
const before = {x:8,y:5}, after = {x:8,y:6};
const unchanged = JSON.stringify(save);
let result = runtime.resolveCrossing(1,1,mover,setup,before,after,"1:mover");
assert.equal(result.events.length,1);
assert.equal(result.events[0].feature_id,"wall-of-ice");
assert.equal(mover.state.current_hp,30);
assert.equal(JSON.stringify(save),unchanged);
result = runtime.resolveCrossing(2,1,mover,setup,{x:7,y:6},after,"1:mover");
assert.equal(result.events.length,0);
owner.state.is_unconscious=true;
result = runtime.resolveCrossing(3,1,mover,setup,before,after,"1:mover");
assert.equal(result.events.length,0);
owner.state.is_unconscious=false;
intact.destroyed=true; intact.current_hp=0;
result = runtime.resolveCrossing(4,1,mover,setup,before,after,"1:mover");
assert.equal(result.events.length,0);
intact.destroyed=false; intact.current_hp=30;
result = runtime.resolveCrossing(5,11,mover,setup,before,after,"11:mover");
assert.equal(result.events.length,0);
console.log("Browser source-neutral destroyed-wall crossing save parity passed.");
