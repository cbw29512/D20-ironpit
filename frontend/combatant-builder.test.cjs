const test = require("node:test");
const assert = require("node:assert/strict");
const {makeDefinition} = require("./combatant-builder.js");

function fields() {
  return {
    id:"test-beast",name:"Test Beast",kind:"monster",ruleset:"2014",archetype:"beast",size:"medium",
    armor_class:"13",max_hp:"24",speed_ft:"30",initiative_bonus:"2",
    attack_id:"claw",attack_name:"Claw",attack_kind:"melee",attack_bonus:"5",
    damage_count:"2",damage_size:"6",damage_bonus:"3",damage_type:"slashing"
  };
}
test("monster form exports universal immutable combatant declaration", () => {
  const result=makeDefinition(fields());
  assert.equal(result.kind,"monster");
  assert.equal(result.primary_attack_id,"claw");
  assert.deepEqual(result.attacks[0].damage,{count:2,size:6,bonus:3});
  assert.equal(result.attacks[0].attack_bonus,5);
  assert.equal(result.ability_scores,undefined);
});
test("pregen uses the same schema with explicit edition, level and ability scores", () => {
  const input={...fields(),kind:"character",ruleset:"2024",archetype:"fighter",level:"6",
    strength:"18",dexterity:"12",constitution:"16",intelligence:"8",wisdom:"10",charisma:"11"};
  const result=makeDefinition(input);
  assert.equal(result.kind,"character");
  assert.equal(result.level,6);
  assert.equal(result.ability_scores.strength,18);
  assert.equal(result.attacks.length,1);
});
test("invalid identifiers and damage math fail closed", () => {
  assert.throws(()=>makeDefinition({...fields(),id:"Werewolf!"}),/IDs/);
  assert.throws(()=>makeDefinition({...fields(),damage_count:"-1"}),/damage_count/);
  assert.throws(()=>makeDefinition({...fields(),max_hp:""}),/max_hp/);
});
test("unknown kind and ruleset cannot change the runtime contract",()=>{
  assert.throws(()=>makeDefinition({...fields(),kind:"npc"}),/mode/);
  assert.throws(()=>makeDefinition({...fields(),ruleset:"3e"}),/ruleset/);
});
