"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname,name), "utf8"), {filename:name},
);
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = {immune:() => false};
const sizes = ["tiny","small","medium","large","huge","gargantuan"];
window.IRON_PIT_BROWSER_STATE = {
  sizeAtMost: (member,max) => sizes.indexOf(member.state.template.size) <= sizes.indexOf(max),
};
load("browser-grapple.js");
load("browser-save-action-effects.js");
const save = {succeeded:false,roll:null};
const action = {
  id:"generic-flood",name:"Generic Flood",
  grappleEscapeDc:14,restrainsWhileGrappled:true,
  grappleMaxTargetSize:"large",grappleMaxActiveGrapples:2,
  grappleLargeTargetSlotCost:2,grapplePreventsBreathing:true,range:0,
};
const member=(id,side,size)=>({
  combatant_id:id,side,state:{
    template:{id,name:id,size},is_alive:true,is_dead:false,current_hp:35,
    grapple_sources:[],active_effect_ids:[],timed_effects:[],swallowed:null,
  },
});
const owner=member("generic-owner","monsters","large");
const medium=member("medium","heroes","medium");
const large=member("large","heroes","large");
const huge=member("huge","heroes","huge");
const setup={heroes:[medium,large,huge],monsters:[owner]};
const apply=(victim)=>window.IRON_PIT_BROWSER_SAVE_ACTION_EFFECTS.apply(
  owner,victim,action,save,1,{setup},
);
assert.deepEqual(apply(huge).appliedConditions,[]);
assert.deepEqual(apply(large).appliedConditions,["grappled","restrained"]);
assert.equal(large.state.grapple_sources[0].prevents_breathing,true);
assert.deepEqual(apply(medium).appliedConditions,[]);
window.IRON_PIT_BROWSER_GRAPPLE.release(large.state,owner.combatant_id);
assert.deepEqual(apply(medium).appliedConditions,["grappled","restrained"]);
const second=member("second","heroes","medium");
setup.heroes.push(second);
assert.deepEqual(apply(second).appliedConditions,["grappled","restrained"]);
const third=member("third","heroes","small");
setup.heroes.push(third);
assert.deepEqual(apply(third).appliedConditions,[]);
const held=medium.state.grapple_sources[0];
assert.deepEqual(apply(medium).appliedConditions,[]);
assert.equal(medium.state.grapple_sources[0],held);
assert.throws(
  ()=>window.IRON_PIT_BROWSER_SAVE_ACTION_EFFECTS.apply(
    owner,third,action,save,1,{}),
  /encounter setup/i,
);
console.log("Universal save Grapple capacity and breathing parity passed.");
