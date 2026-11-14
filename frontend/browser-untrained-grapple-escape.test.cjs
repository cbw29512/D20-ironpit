"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const source = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-animated-armor"];
  assert.ok(source, "Use the actual 2014 failing source card.");
  const original = JSON.stringify(source);
  const state = window.IRON_PIT_BROWSER_STATE.buildState(source);
  assert.ok(state.template.ability_scores, "Source must declare ability scores.");
  assert.equal(state.template.skill_bonuses?.athletics, undefined);
  assert.equal(state.template.skill_bonuses?.acrobatics, undefined);
  const member = {combatant_id:"monster-1",side:"monsters",position_ft:5,state};
  const expectedStr = Math.floor((state.template.ability_scores.strength - 10) / 2);
  const expectedDex = Math.floor((state.template.ability_scores.dexterity - 10) / 2);
  const expected = Math.max(expectedStr,expectedDex);
  const grapple = window.IRON_PIT_BROWSER_GRAPPLE;
  grapple.apply(state,"hero-1",10,5,true);
  const dice = window.IRON_PIT_DICE, old = dice.roll;
  try {
    dice.roll = () => 20;
    const event = grapple.escape(1,1,member);
    assert.equal(event.ability_check_roll.modifier,expected);
    assert.equal(event.check_succeeded,true);
    assert.equal(event.feature_id,"escape-grapple");
    assert.equal(state.action_available,false);
    assert.equal(state.grapple_sources.length,0);
  } finally { dice.roll = old; }
  assert.equal(JSON.stringify(source),original,"The source card cannot mutate.");
  console.log("2014 untrained monster Grapple escape uses canonical ability math.");
} catch (error) {
  console.error("Untrained 2014 Grapple escape regression failed",error);
  process.exitCode = 1;
}
