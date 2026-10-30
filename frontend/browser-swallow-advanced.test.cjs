"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
global.window=globalThis;
function load(file) {
  try {
    return vm.runInThisContext(
      fs.readFileSync(path.join(__dirname,file),"utf8"),
      {filename:file},
    );
  } catch (error) {
    console.error("Failed to load advanced Swallow browser dependency.",{file,error});
    throw error;
  }
}
load("browser-grapple.js");
load("browser-swallow.js");
load("browser-swallow-hit-rider.js");
load("browser-swallow-regurgitation.js");

const swallow=window.IRON_PIT_BROWSER_SWALLOW;
window.IRON_PIT_BROWSER_ATTACK_OUTCOME={
  noEventResult:(sequence)=>({events:[],sequence,claimed:false}),
};

// Embedded Swallow must require a grapple that existed before this Bite.
const owner={is_alive:true,is_dead:false,current_hp:120,swallowed_target_ids:[],
  template:{name:"Container",size:"gargantuan",attacks:[{id:"bite"}],
    swallowActions:[{sourceName:"Swallow",attackId:"bite",deliveryMode:"attack_hit",
      requiresExistingGrapple:true,maxTargetSize:"large",damageDiceCount:12,
      damageDiceSize:6,damageType:"acid",maxSwallowed:2,exitMovementFt:15}]}
};
const victim={is_alive:true,is_dead:false,current_hp:60,template:{name:"Victim",size:"large"},
  active_effect_ids:[],grapple_sources:[],timed_effects:[],swallowed:null};
window.IRON_PIT_BROWSER_GRAPPLE.apply(victim,"owner",18,10,true);
const outcome={appliedConditions:[]};
let result=window.IRON_PIT_BROWSER_SWALLOW_HIT_RIDER.applyHit({
  sequence:1,member:{combatant_id:"owner",state:owner},
  target:{combatant_id:"victim",state:victim},
  attack:{id:"bite"},attackOutcome:outcome,preHitGrappledByAttacker:false,
});
assert.equal(result,null);
assert.equal(victim.swallowed,null);
assert.ok(victim.grapple_sources.some((item)=>item.source_id==="owner"));

result=window.IRON_PIT_BROWSER_SWALLOW_HIT_RIDER.applyHit({
  sequence:1,member:{combatant_id:"owner",state:owner},
  target:{combatant_id:"victim",state:victim},
  attack:{id:"bite"},attackOutcome:outcome,preHitGrappledByAttacker:true,
});
assert.deepEqual(result,{events:[],sequence:1,claimed:false});
assert.equal(victim.swallowed.source_id,"owner");
assert.deepEqual(victim.grapple_sources,[]);
assert.ok(outcome.appliedConditions.includes("blinded"));
assert.ok(outcome.appliedConditions.includes("restrained"));

// Threshold regurgitation counts only damage attributed to the swallowed creature.
const second={is_alive:true,is_dead:false,current_hp:40,template:{name:"Inside B",size:"medium"},
  active_effect_ids:[],grapple_sources:[],timed_effects:[],swallowed:null};
const threshold={sourceName:"Swallow",attackId:"bite",deliveryMode:"attack_hit",
  requiresExistingGrapple:true,maxTargetSize:"large",damageDiceCount:12,damageDiceSize:6,
  damageType:"acid",maxSwallowed:2,exitMovementFt:15,regurgitationDamageThreshold:50,
  regurgitationSaveAbility:"constitution",regurgitationSaveDc:25,regurgitationRangeFt:10,
  regurgitationAllSwallowed:true};
window.IRON_PIT_BROWSER_GRAPPLE.apply(second,"owner",18,10,true);
assert.equal(swallow.swallowAfterBite("owner",owner,"second",second,threshold,true),true);
const setup={heroes:[
  {combatant_id:"victim",state:victim},
  {combatant_id:"second",state:second},
],monsters:[{combatant_id:"owner",state:owner}]};
let saveArgs=null;
window.IRON_PIT_BROWSER_SAVING_THROWS={resolveSavingThrow:(state,ability,dc)=>{
  saveArgs={state,ability,dc};
  return {roll:{total:1},succeeded:false};
}};
owner.damage_taken_this_turn_by_source={other:100,victim:49};
let regurg=window.IRON_PIT_BROWSER_SWALLOW_REGURGITATION.resolveEndTurn(
  10,3,setup.heroes[0],setup,
);
assert.equal(regurg.events.length,0);
assert.ok(victim.swallowed && second.swallowed);
owner.damage_taken_this_turn_by_source.victim=50;
regurg=window.IRON_PIT_BROWSER_SWALLOW_REGURGITATION.resolveEndTurn(
  10,3,setup.heroes[0],setup,
);
assert.equal(regurg.sequence,11);
assert.equal(regurg.events[0].save_succeeded,false);
assert.equal(saveArgs.state,owner);
assert.equal(saveArgs.ability,"constitution");
assert.equal(saveArgs.dc,25);
assert.equal(victim.swallowed,null);
assert.equal(second.swallowed,null);
assert.ok(victim.active_effect_ids.includes("prone"));
assert.ok(second.active_effect_ids.includes("prone"));

for(const page of ["../index.html","index.html"]) {
  const text=fs.readFileSync(path.join(__dirname,page),"utf8");
  assert.ok(text.includes('src="browser-swallow-hit-rider.js"'));
  assert.ok(text.includes('src="browser-swallow-regurgitation.js"'));
}
console.log("Advanced browser Swallow delivery and regurgitation regressions passed.");
