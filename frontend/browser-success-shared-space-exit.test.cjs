"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname,"browser-save-event.js"),"utf8"),
  {filename:"browser-save-event.js"},
);
const combatant = (id) => ({
  combatant_id:id, side:id==="Source"?"monsters":"heroes",
  state:{
    position:{x:1,y:1}, position_ft:0, current_hp:20,temporary_hp:0,
    death_save_successes:0,death_save_failures:0,is_stable:false,is_dead:false,
    template:{name:id,creature_type:"elemental",evasion:false},
  },
});
const source = combatant("Source"), target = combatant("Victim");
const action = {
  id:"generic",name:"Ebb Wave",dc:17,saveAbility:"strength",
  successDamage:"none",successfulSaveExitsSourceSpace:true,
};
const attempt=(succeeded)=>({
  automaticallyFails:false,advantageSources:[],saveContext:{disadvantageSources:[]},
  save:{succeeded,roll:null},
});
const damage={damageOutcome:null,roll:null,components:[]};
const effects={appliedConditions:[],pushedFt:0};
const snapshot={
  hpBefore:20,temporaryHpBefore:0,deathSuccessBefore:0,
  deathFailureBefore:0,resourceRemaining:null,concentrationBefore:null,
};
const build=(succeeded)=>window.IRON_PIT_BROWSER_SAVE_EVENT.build(
  1,2,source,target,action,attempt(succeeded),damage,effects,snapshot,
);
const initial=JSON.stringify([source.state.position,target.state.position]);
assert.match(build(true).description,/pushed out of Source's space/);
assert.match(build(true).description,/position unchanged by arena rule/);
assert.doesNotMatch(build(false).description,/pushed out/);
assert.equal(JSON.stringify([source.state.position,target.state.position]),initial);
action.successfulSaveExitsSourceSpace=false;
assert.doesNotMatch(build(true).description,/pushed out/);
console.log("Universal successful shared-space exit logs without movement.");
