"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
global.window=globalThis;
const load=(name)=>vm.runInThisContext(fs.readFileSync(path.join(__dirname,name),"utf8"),{filename:name});
load("browser-grapple.js");
load("browser-multi-hit-grapple.js");
load("browser-grapple-upgrade-action.js");
const runtime=window.IRON_PIT_BROWSER_MULTI_HIT_GRAPPLE;
window.IRON_PIT_BROWSER_STATE={distance:(a,b)=>Math.abs(a.position_ft-b.position_ft)};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY={immune:()=>false};
const owner={combatant_id:"holder",side:"monsters",position_ft:0,state:{
  is_alive:true,is_dead:false,current_hp:60,grapple_sources:[],
  template:{name:"Renamed Holder",size:"large",multiHitGrappleEffects:[{
    sourceName:"Renamed Engulf",effectId:"engulf",standaloneAction:true,attackId:"slam",hitsRequired:2,maxTargetSize:"medium",
    escapeDc:14,rangeFt:5,maxActiveGrapples:1,restrains:true,blinds:true,preventsBreathing:true
  }]}
}};
const target={combatant_id:"hero",side:"heroes",position_ft:5,state:{
  is_alive:true,is_dead:false,current_hp:50,grapple_sources:[],timed_effects:[],
  active_effect_ids:[],template:{size:"medium",name:"Hero"},
}};
const setup={heroes:[target],monsters:[owner]};
const hit=(id,landed=true,attackId="slam")=>({
  event_type:"attack",attack_id:attackId,hit:landed,target_id:id,
});
assert.equal(runtime.resolve(1,1,owner,setup,[hit("hero")]).events.length,0);
assert.equal(runtime.resolve(1,1,owner,setup,[hit("hero"),hit("hero",false)]).events.length,0);
assert.equal(runtime.resolve(1,1,owner,setup,[hit("hero"),hit("hero",true,"bite")]).events.length,0);
const result=runtime.resolve(1,1,owner,setup,[hit("hero"),hit("hero")]);
assert.equal(result.sequence,2);
assert.equal(result.events[0].feature_id,"Renamed Engulf");
assert.deepEqual(result.events[0].applied_condition_ids,["grappled","restrained","blinded"]);
assert.equal(target.state.grapple_sources[0].escape_dc,14);
assert.equal(target.state.grapple_sources[0].prevents_breathing,true);
assert.ok(target.state.active_effect_ids.includes("blinded"));
assert.equal(runtime.resolve(2,2,owner,setup,[hit("hero"),hit("hero")]).events.length,0);
window.IRON_PIT_BROWSER_GRAPPLE.release(target.state,"holder");
assert.equal(target.state.grapple_sources.length,0);
for (const effect of ["grappled","restrained","blinded"])
  assert.ok(!target.state.active_effect_ids.includes(effect));
target.state.template.size="large";
assert.equal(runtime.resolve(3,3,owner,setup,[hit("hero"),hit("hero")]).events.length,0);
target.state.template.size="medium";
target.state.active_effect_ids=["blinded"];
const preblind=runtime.resolve(4,4,owner,setup,[hit("hero"),hit("hero")]);
assert.equal(preblind.events.length,1);
window.IRON_PIT_BROWSER_GRAPPLE.release(target.state,"holder");
assert.ok(target.state.active_effect_ids.includes("blinded"),
  "Independent blindness must survive grapple release");
for (const page of ["../index.html","index.html"]) {
  assert.ok(fs.readFileSync(path.join(__dirname,page),"utf8").includes(
    'src="browser-multi-hit-grapple.js"'));
}
// Separate Engulf Action: requires a preexisting source-owned grapple.
window.IRON_PIT_ACTION_ECONOMY={
  available:(state,cost)=>cost==="action" && state.action_available,
  spend:(state,cost)=>{assert.equal(cost,"action");state.action_available=false;},
};
owner.state.action_available=true;
target.state.active_effect_ids=[];
target.state.grapple_sources=[];
assert.equal(window.IRON_PIT_BROWSER_GRAPPLE_UPGRADE_ACTION.choose(owner,setup),null);
window.IRON_PIT_BROWSER_GRAPPLE.apply(target.state,"holder",14,5);
const upgrade=window.IRON_PIT_BROWSER_GRAPPLE_UPGRADE_ACTION.choose(owner,setup);
assert.equal(upgrade.target,target);
const activated=window.IRON_PIT_BROWSER_GRAPPLE_UPGRADE_ACTION.resolve(
  1,1,owner,setup,"hero","engulf");
assert.equal(activated.events[0].feature_id,"Renamed Engulf");
assert.equal(target.state.grapple_sources[0].linked_effect_id,"engulf");
assert.equal(owner.state.action_available,false);
assert.equal(window.IRON_PIT_BROWSER_GRAPPLE_UPGRADE_ACTION.choose(owner,setup),null);
console.log("Generic same-target Multiattack and separate linked-grapple Action pass.");
