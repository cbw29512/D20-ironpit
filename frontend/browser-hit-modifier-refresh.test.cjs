"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const hero = window.IRON_PIT_BROWSER_HEROES["thalen-greenbough-l4"];
  const monster = window.IRON_PIT_BROWSER_MONSTERS["srd-lemure"];
  assert.ok(hero && monster, "Use actual 2024 matrix card sources.");
  const spell = (hero.spell_attack_actions || []).find(item => item.id === "starry-wisp");
  assert.ok(spell && spell.onHitModifierEffects?.length);
  const source = JSON.stringify(hero);
  const state = window.IRON_PIT_BROWSER_STATE.buildState(monster);
  const effect = spell.onHitModifierEffects[0];
  const sm = window.IRON_PIT_BROWSER_SPELL_MODIFIERS;
  const mods = window.IRON_PIT_BROWSER_MODIFIERS;
  const first = sm.build("hero-1","monster-1",spell,effect,0,1);
  const second = sm.build("hero-1","monster-1",spell,effect,0,2);
  assert.equal(first.id,second.id);
  assert.equal(first.expires_source_turn_end_round,2);
  assert.equal(second.expires_source_turn_end_round,3);
  mods.add(state,first);
  assert.throws(()=>mods.add(state,second),/different data/);
  mods.add(state,second,{refreshExpiry:true});
  assert.equal(state.active_modifiers.length,1);
  assert.deepEqual(state.active_modifiers[0],second);
  mods.add(state,second,{refreshExpiry:true});
  assert.equal(state.active_modifiers.length,1);
  assert.throws(()=>mods.add(state,{...second,source_name:"Different"},
    {refreshExpiry:true}),/different data/);
  assert.throws(()=>mods.add(state,first,{refreshExpiry:true}),/different data/);
  assert.equal(JSON.stringify(hero),source);
  console.log("2024 repeat-hit Starry Wisp refreshes one owner-scoped modifier.");
} catch (error) {
  console.error("Repeat-hit modifier refresh browser regression failed",error);
  process.exitCode=1;
}
