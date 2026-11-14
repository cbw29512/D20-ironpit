"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const source = window.IRON_PIT_BROWSER_HEROES["seraphine-dawnshield-2014-l3"];
  assert.ok(source, "The 2014 Cleric L3 source must be loaded.");
  const before = JSON.stringify(source);
  const state = window.IRON_PIT_BROWSER_STATE.buildState(source);
  state.current_hp = 1;
  const cleric = {combatant_id:"hero-1",side:"heroes",position_ft:0,state};
  const enemySource = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-mummy"];
  assert.ok(enemySource);
  const enemy = {combatant_id:"monster-1",side:"monsters",position_ft:5,
    state:window.IRON_PIT_BROWSER_STATE.buildState(enemySource)};
  const setup = {heroes:[cleric],monsters:[enemy]};
  const pooled = window.IRON_PIT_BROWSER_POOLED_HEALING;
  const channel = window.IRON_PIT_BROWSER_CLERIC_CHANNEL;
  assert.ok(pooled.capacity(cleric,1,2)>0);
  state.timed_effects.push({effect_id:"source-neutral-curse",
    source_id:"monster-1",cannot_regain_hit_points:true});
  assert.equal(pooled.capacity(cleric,1,2),0);
  assert.deepEqual(channel.preserveTargets(cleric,setup),[]);
  assert.notEqual(channel.choose(cleric,setup)?.kind,"preserve-life");
  state.timed_effects.pop();
  assert.ok(pooled.capacity(cleric,1,2)>0);
  assert.equal(JSON.stringify(source),before);
  console.log("2014 Preserve Life honors generic healing block eligibility.");
} catch (error) {
  console.error("Pooled healing with cursed target regression failed",error);
  process.exitCode=1;
}
