"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
require("./browser-test-runtime.cjs").loadWebsite();
const {makeDefinition} = require("./combatant-builder.js");
const {compile,decorate} = require("./custom-monster-runtime.js");

function fields(ruleset) {
  return {
    id:"combat-dummy",name:"Combat Dummy",kind:"monster",ruleset,archetype:"training construct",size:"medium",
    challenge_rating:"1/4",armor_class:"0",max_hp:"50",speed_ft:"30",initiative_bonus:"0",
    attack_id:"claw",attack_name:"Claw",attack_kind:"melee",attack_bonus:"5",
    damage_count:"1",damage_size:"6",damage_bonus:"2",damage_type:"slashing",
    on_hit_effects:[
      {kind:"damage",damage_type:"fire",count:"1",size:"4",bonus:"0"},
      {kind:"prone"},
      {kind:"save_condition",save_ability:"constitution",dc:"11",condition:"poisoned",duration_rounds:"2"},
    ],
  };
}
for(const [edition,heroId] of [["2014","karnok-stoneward-2014-l1"],["2024","karnok-stoneward-l1"]]) {
  const source=makeDefinition(fields(edition));
  const before=JSON.stringify(source);
  const card=decorate({...source,custom:true,coverage_status:"custom_draft",runnable_template_id:null});
  assert.equal(card.coverage_status,"custom_ready",edition);
  assert.equal(card.compiled_template.armor_class,0);
  assert.equal(card.compiled_template.challenge_rating,"1/4");
  assert.equal(card.compiled_template.attacks[0].onHitDamage[0].damageType,"fire");
  assert.equal(card.compiled_template.attacks[0].proneMaxSize,"gargantuan");
  assert.equal(card.compiled_template.attacks[0].onHitConditionSave.conditionId,"poisoned");
  assert.equal(card.compiled_template.primary_attack_id,"claw");
  const selection={ruleset:edition,hero_ids:[heroId],monster_ids:[card.runnable_template_id],
    compiled_monsters:{[card.runnable_template_id]:card.compiled_template}};
  const fight=window.IRON_PIT_BROWSER_ENGINE.runEncounter(selection);
  assert.ok(fight.events.length>0,edition+" custom fight should resolve");
  assert.ok(["heroes_win","monsters_win","draw"].includes(fight.outcome),edition);
  assert.equal(fight.setup.monsters[0].state.template.armor_class,0);
  assert.equal(JSON.stringify(source),before,"fight must not mutate source custom card");
}
const invalid=makeDefinition(fields("2014"));
invalid.attacks[0].effects.reverse();
assert.equal(decorate(invalid).coverage_status,"custom_draft");
assert.match(decorate(invalid).compile_error,/effect/);
assert.throws(()=>compile({...makeDefinition(fields("2014")),unknown_innate_spell:"fireball"}),/unsupported field/);
assert.throws(()=>compile({...makeDefinition(fields("2014")),kind:"character"}),/unsupported schema/);
assert.throws(()=>compile({...makeDefinition(fields("2014")),challenge_rating:"100"}),/Challenge Rating/);
for(const page of ["index.html","../index.html"]) {
  const html=fs.readFileSync(path.join(__dirname,page),"utf8");
  assert.ok(html.includes('src="custom-monster-runtime.js"'));
  assert.ok(html.indexOf('src="custom-monster-runtime.js"')<html.indexOf('src="battlefield-picker.js"'));
}
console.log("Saved custom monster homebrew browser runtime fights passed 2014 and 2024.");
