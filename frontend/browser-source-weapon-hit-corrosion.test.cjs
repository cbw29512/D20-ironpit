"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
global.window = globalThis;
const load = (file) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, file), "utf8"), {filename:file});
load("browser-weapon-corrosion.js");
load("browser-weapon-hit-corrosion.js");
const hook = window.IRON_PIT_BROWSER_WEAPON_HIT_CORROSION;
const defender = {template:{weaponHitCorrosion:{
  sourceName:"Corrode Metal", qualifyingMaterials:["metal"],
  requiresNonmagical:true, penaltyPerHit:1, unusableAtPenalty:5,
}}};
const original = Object.freeze({id:"weapon-one",weaponId:"steel-one",kind:"melee",
  weaponMaterial:"metal",weaponMagical:false});
const attacker={weapon_corrosion_penalties:{}};
for (let n=1;n<=5;n++)
  assert.equal(hook.afterHit(attacker,defender,original),-n);
assert.equal(attacker.weapon_corrosion_penalties["steel-one"],5);
assert.equal(attacker.weapon_corrosion_penalties["other"],undefined);
assert.equal(hook.afterHit({weapon_corrosion_penalties:{}},{
  template:{}},original),null);
for (const changes of [
  {weaponMaterial:null}, {weaponMagical:null}, {weaponMagical:true},
  {weaponMaterial:"wood"}, {weaponMaterial:"other"}, {kind:"ranged"},
]) {
  const testState={weapon_corrosion_penalties:{}};
  assert.equal(hook.afterHit(testState,defender,{...original,...changes}),null);
  assert.deepEqual(testState.weapon_corrosion_penalties,{});
}
const nextFight={weapon_corrosion_penalties:{}};
assert.equal(window.IRON_PIT_BROWSER_WEAPON_CORROSION.modifier(nextFight,"steel-one"),0);
const entrypoints=["index.html","frontend/index.html"];
for(const file of entrypoints){
  const markup=fs.readFileSync(path.join(__dirname,"..",file),"utf8");
  assert.ok(markup.includes('src="browser-weapon-hit-corrosion.js"'));
}
assert.match(fs.readFileSync(path.join(__dirname,"browser-attack.js"),"utf8"),
  /corrosion\.afterHit\(attacker\.state, actualTarget\.state, attack\)/);
assert.equal(original.weaponMagical,false);
console.log("Source-owned post-hit corrosion excludes unproven equipment in browser.");
