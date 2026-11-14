"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

try {
  const ctx = {console};
  ctx.window = ctx;
  const target = {combatant_id:"target",state:{current_hp:50}};
  const caster = {combatant_id:"caster",
    state:{template:{spell_save_actions:[]},concentration:null}};
  const setup = {heroes:[caster],monsters:[target]};
  const verbal = {id:"verbal",name:"Verbal Spell",level:0,
    actionCost:"action",range:60,score:10,verbalComponent:true};
  const silent = {...verbal,id:"silent",name:"Silent Spell",
    score:1,verbalComponent:false};
  caster.state.template.spell_save_actions = [verbal,silent];
  let blocking = true;
  ctx.IRON_PIT_BROWSER_SUPPRESSION_ZONES = {
    verbalBlocked:() => blocking,
  };
  ctx.IRON_PIT_ACTION_ECONOMY = {available:() => true};
  ctx.IRON_PIT_BROWSER_STATE = {distance:() => 5};
  ctx.IRON_PIT_BROWSER_OFFENSE_VALUE = {
    saveSpell:(_target,action) => action.score,
  };
  ctx.IRON_PIT_BROWSER_SPELLCASTING = {
    safeDamageMaximizer:() => null,
  };
  ctx.IRON_PIT_BROWSER_SPELL_POLICY_SUPPORT = {
    castOptions:() => [{castLevel:0,alternateCast:null}],
    scaledSpell:action => action,
    effectiveRange:()=>60,
    legalSingleTargets:() => [target],
    rankedSaveTargets:eligible => eligible,
    availableRangeModifier:() => null,
  };
  vm.runInNewContext(fs.readFileSync(
    path.join(__dirname,"browser-spell-policy.js"),"utf8"),
    ctx,{filename:"browser-spell-policy.js"});
  const policy = ctx.IRON_PIT_BROWSER_SPELL_POLICY;
  assert.equal(policy.choose(caster,setup,"1:caster").action.id,"silent");
  assert.equal(policy.chooseActionAtSlot(caster,setup,verbal,0),null);
  assert.equal(policy.chooseById(caster,setup,"1:caster","verbal"),null);
  caster.state.template.spell_save_actions=[verbal];
  assert.equal(policy.choose(caster,setup,"1:caster"),null);
  blocking=false;
  caster.state.template.spell_save_actions=[verbal,silent];
  assert.equal(policy.choose(caster,setup,"1:caster").action.id,"verbal");
  console.log("Source-neutral browser Silence save-spell choice passed");
} catch (error) {
  console.error("Source-neutral browser Silence save-spell test failed",error);
  process.exitCode=1;
}
