"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
global.window=globalThis;
const load=(file)=>vm.runInThisContext(fs.readFileSync(path.join(__dirname,file),"utf8"),{filename:file});
load("browser-grapple.js");load("browser-swallow.js");load("browser-swallow-regurgitation.js");
const swallow=window.IRON_PIT_BROWSER_SWALLOW;
const frog={is_alive:true,is_dead:false,current_hp:20,template:{
  size:"medium",attacks:[{id:"bite"}]},swallowed_target_ids:[]};
const tiny={is_alive:true,is_dead:false,current_hp:30,template:{size:"small"},
  active_effect_ids:[],grapple_sources:[],timed_effects:[],swallowed:null};
const action={sourceName:"Swallow",attackId:"bite",requiresExistingGrapple:true,maxTargetSize:"small",
  damageDiceCount:2,damageDiceSize:4,damageType:"acid",maxSwallowed:1,exitMovementFt:5};
assert.equal(swallow.swallowAfterBite("frog",frog,"victim",tiny,action,true),false);
window.IRON_PIT_BROWSER_GRAPPLE.apply(tiny,"frog",11,5,true);
assert.equal(swallow.swallowAfterBite("frog",frog,"victim",tiny,action,false),false);
assert.equal(swallow.swallowAfterBite("frog",frog,"victim",tiny,action,true),true);
assert.equal(tiny.swallowed.source_id,"frog");
assert.deepEqual(tiny.grapple_sources,[]);
assert.ok(tiny.active_effect_ids.includes("restrained"));
assert.ok(tiny.active_effect_ids.includes("blinded"));
assert.deepEqual(frog.swallowed_target_ids,["victim"]);
assert.equal(swallow.swallowAfterBite("frog",frog,"victim",tiny,action,true),false);
assert.equal(swallow.release("frog",frog,"victim",tiny),true);
assert.equal(tiny.swallowed,null);
assert.deepEqual(frog.swallowed_target_ids,[]);
assert.ok(tiny.active_effect_ids.includes("prone"));
assert.ok(!tiny.active_effect_ids.includes("restrained"));
const medium={...tiny,template:{size:"medium"},active_effect_ids:[],grapple_sources:[],swallowed:null};
window.IRON_PIT_BROWSER_GRAPPLE.apply(medium,"frog",11,5,true);
assert.equal(swallow.swallowAfterBite("frog",frog,"medium",medium,action,true),false);
const toad={...frog,swallowed_target_ids:[]};
assert.equal(swallow.swallowAfterBite("toad",toad,"medium",medium,{...action,maxTargetSize:"medium",damageDiceCount:3,damageDiceSize:6},true),false);
window.IRON_PIT_BROWSER_GRAPPLE.apply(medium,"toad",13,5,true);
assert.equal(swallow.swallowAfterBite("toad",toad,"medium",medium,{...action,maxTargetSize:"medium",damageDiceCount:3,damageDiceSize:6},true),true);
assert.equal(medium.swallowed.damage_dice_count,3);
window.IRON_PIT_DICE={rollMany:(count,size)=>Array.from({length:count},()=>size)};
window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES={resolveDamage:(_state,total,type)=>{
  assert.equal(type,"acid"); return {applied:total};
}};
window.IRON_PIT_BROWSER_ATTACK={applyDamage:(state,total)=>{state.current_hp=Math.max(0,state.current_hp-total);}};
const swallowedSetup={heroes:[{combatant_id:"medium",state:medium}],monsters:[{combatant_id:"toad",state:toad}]};
const acid=swallow.sourceTurnDamage(3,2,swallowedSetup.monsters[0],swallowedSetup);
assert.equal(acid.sequence,4);
assert.equal(acid.events[0].damage_components[0].notation,"3d6");
assert.equal(acid.events[0].damage_components[0].applied_total,18);
assert.equal(medium.current_hp,12);
medium.current_hp=0;
assert.deepEqual(swallow.cleanup(swallowedSetup),[],"0 HP is not actual character death");
assert.equal(medium.swallowed.source_id,"toad");
assert.equal(swallow.sourceTurnDamage(4,3,swallowedSetup.monsters[0],swallowedSetup).events.length,1);
medium.is_alive=false; medium.is_dead=true;
assert.deepEqual(swallow.cleanup(swallowedSetup),["medium"]);
medium.is_alive=true; medium.is_dead=false; medium.current_hp=12;

const deadOwner={...frog,is_alive:false,is_dead:true,current_hp:0,swallowed_target_ids:["held"]};
const heldVictim={...tiny,is_alive:true,is_dead:false,current_hp:15,
  active_effect_ids:["blinded","restrained"],grapple_sources:[],timed_effects:[],
  swallowed:{source_id:"dead-owner",source_name:"Swallow"}};
const deadSetup={heroes:[{combatant_id:"held",state:heldVictim}],
  monsters:[{combatant_id:"dead-owner",state:deadOwner}]};
assert.deepEqual(swallow.cleanup(deadSetup),["held"]);
assert.equal(heldVictim.swallowed,null);
assert.ok(heldVictim.active_effect_ids.includes("prone"));
assert.ok(!heldVictim.active_effect_ids.includes("blinded"));
assert.ok(!heldVictim.active_effect_ids.includes("restrained"));
assert.deepEqual(deadOwner.swallowed_target_ids,[]);
assert.deepEqual(swallow.cleanup(deadSetup),[]);

// Verify the real browser Swallow selector uses a held target and the generic Bite resolver.
let resolvedBite=null;
window.IRON_PIT_ACTION_ECONOMY={available:(state,cost)=>cost==="action" && state.action_available};
window.IRON_PIT_BROWSER_STATE={distance:(a,b)=>Math.abs(a.position_ft-b.position_ft)};
window.IRON_PIT_BROWSER_ATTACK={resolveAttack:(sequence,round,attacker,target,attack,distance,options)=>{
  resolvedBite={attack,distance,options};
  attacker.state.action_available=false;
  return {sequence,round_number:round,event_type:"attack",hit:true,description:"Bite hits.",
    applied_condition_ids:[]};
}};
const runtimeAction={...action,attackId:"2014-giant-frog-bite"};
const combatFrog={combatant_id:"frog-combat",side:"monsters",position_ft:5,state:{
  is_alive:true,is_dead:false,current_hp:20,action_available:true,swallowed_target_ids:[],
  template:{size:"medium",name:"Giant Frog",attacks:[{id:"2014-giant-frog-bite",kind:"melee",reach:5,
    controlEffect:{grappleEscapeDc:11},grappleTargetPolicy:"forbid-grappled-by-self"}],
    swallowActions:[runtimeAction]},
}};
const combatVictim={combatant_id:"target-combat",side:"heroes",position_ft:10,state:{
  is_alive:true,is_dead:false,current_hp:30,template:{size:"small",name:"Hero"},
  grapple_sources:[],swallowed:null,active_effect_ids:[],timed_effects:[],
}};
const combatSetup={heroes:[combatVictim],monsters:[combatFrog]};
assert.equal(swallow.choose(combatFrog,combatSetup),null);
window.IRON_PIT_BROWSER_GRAPPLE.apply(combatVictim.state,"frog-combat",11,5,true);
assert.equal(swallow.choose(combatFrog,combatSetup).target,combatVictim);
const attackResult=swallow.resolve(1,1,combatFrog,combatSetup,"1:frog-combat","target-combat","2014-giant-frog-bite");
assert.equal(attackResult.sequence,2);
assert.equal(attackResult.events[0].feature_id,undefined);
assert.equal(resolvedBite.attack.controlEffect,null);
assert.equal(resolvedBite.attack.grappleTargetPolicy,"normal");
assert.equal(resolvedBite.options.featureId,"swallow");
assert.equal(combatVictim.state.swallowed.source_id,"frog-combat");
assert.equal(combatFrog.state.action_available,false);
assert.equal(swallow.choose(combatFrog,combatSetup),null);
assert.ok(fs.readFileSync(path.join(__dirname,"browser-turn.js"),"utf8").includes("window.IRON_PIT_BROWSER_SWALLOW?.cleanup(setup)"));
assert.ok(fs.readFileSync(path.join(__dirname,"browser-turn.js"),"utf8").includes("window.IRON_PIT_BROWSER_SWALLOW?.sourceTurnDamage"));
for(const page of ["../index.html","index.html"]) {
  const text=fs.readFileSync(path.join(__dirname,page),"utf8");
  assert.ok(text.includes('src="browser-swallow.js"'));
}
for(const [file,needle] of [
  ["browser-state.js","candidate.state.swallowed == null"],
  ["browser-formation.js","target.state.swallowed == null"],
  ["browser-spell-offense.js","candidate.state.swallowed == null"],
]) assert.ok(fs.readFileSync(path.join(__dirname,file),"utf8").includes(needle),`${file} must enforce total external cover`);

// Threshold regurgitation uses only damage attributed to the swallowed creature.
const regurgOwner={is_alive:true,is_dead:false,current_hp:150,template:{name:"Container",size:"huge",attacks:[{id:"bite"}]},
  swallowed_target_ids:[],damage_taken_this_turn_by_source:{}};
const regurgA={is_alive:true,is_dead:false,current_hp:40,template:{name:"Inside A",size:"medium"},
  active_effect_ids:[],grapple_sources:[],timed_effects:[],swallowed:null};
const regurgB={is_alive:true,is_dead:false,current_hp:40,template:{name:"Inside B",size:"medium"},
  active_effect_ids:[],grapple_sources:[],timed_effects:[],swallowed:null};
const regurgAction={sourceName:"Swallow",attackId:"bite",requiresExistingGrapple:true,maxTargetSize:"medium",
  damageDiceCount:6,damageDiceSize:6,damageType:"acid",maxSwallowed:2,exitMovementFt:15,
  regurgitationDamageThreshold:30,regurgitationSaveAbility:"constitution",regurgitationSaveDc:15,
  regurgitationRangeFt:10,regurgitationAllSwallowed:true};
window.IRON_PIT_BROWSER_GRAPPLE.apply(regurgA,"container",15,5,true);
window.IRON_PIT_BROWSER_GRAPPLE.apply(regurgB,"container",15,5,true);
assert.equal(swallow.swallowAfterBite("container",regurgOwner,"inside-a",regurgA,regurgAction,true),true);
assert.equal(swallow.swallowAfterBite("container",regurgOwner,"inside-b",regurgB,regurgAction,true),true);
const regurgSetup={heroes:[
  {combatant_id:"inside-a",state:regurgA},
  {combatant_id:"inside-b",state:regurgB},
],monsters:[{combatant_id:"container",state:regurgOwner}]};
let saveArgs=null;
window.IRON_PIT_BROWSER_SAVING_THROWS={resolveSavingThrow:(state,ability,dc)=>{
  saveArgs={state,ability,dc}; return {roll:{total:1},succeeded:false};
}};
regurgOwner.damage_taken_this_turn_by_source={"other":100,"inside-a":29};
let regurg=window.IRON_PIT_BROWSER_SWALLOW_REGURGITATION.resolveEndTurn(10,3,regurgSetup.heroes[0],regurgSetup);
assert.equal(regurg.events.length,0);
assert.ok(regurgA.swallowed && regurgB.swallowed);
regurgOwner.damage_taken_this_turn_by_source["inside-a"]=30;
regurg=window.IRON_PIT_BROWSER_SWALLOW_REGURGITATION.resolveEndTurn(10,3,regurgSetup.heroes[0],regurgSetup);
assert.equal(regurg.sequence,11);
assert.equal(regurg.events[0].save_succeeded,false);
assert.equal(saveArgs.state,regurgOwner);
assert.equal(saveArgs.ability,"constitution");
assert.equal(saveArgs.dc,15);
assert.equal(regurgA.swallowed,null);
assert.equal(regurgB.swallowed,null);
assert.ok(regurgA.active_effect_ids.includes("prone"));
assert.ok(regurgB.active_effect_ids.includes("prone"));

console.log("Browser Swallow state parity and source-owned size/capacity checks pass.");
