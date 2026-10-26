"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
global.window=globalThis;
const load=(file)=>vm.runInThisContext(fs.readFileSync(path.join(__dirname,file),"utf8"),{filename:file});
load("browser-grapple.js");load("browser-swallow.js");
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
assert.ok(fs.readFileSync(path.join(__dirname,"browser-turn.js"),"utf8").includes("window.IRON_PIT_BROWSER_SWALLOW?.cleanup(setup)"));
for(const page of ["../index.html","index.html"]) {
  const text=fs.readFileSync(path.join(__dirname,page),"utf8");
  assert.ok(text.includes('src="browser-swallow.js"'));
}
console.log("Browser Swallow state parity and source-owned size/capacity checks pass.");
