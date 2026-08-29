"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-monsters-control.js",
  "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-timed-conditions.js",
  "browser-attack.js", "browser-reactions.js", "browser-reaction-movement.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const W = window.IRON_PIT_BROWSER_REACTION_MOVEMENT;
const member = (id, side, template, position) => ({ combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)) });
const heroTemplate = () => window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
const monsterTemplate = (id) => window.IRON_PIT_BROWSER_MONSTERS[id];
const dice = (roll20 = 2) => { window.IRON_PIT_DICE = { roll: (sides) => sides === 20 ? roll20 : 1, rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? roll20 : 1) }; };

function threeWay(reactorId = "srd-commoner") {
  const mover = member("hero-1", "heroes", heroTemplate(), 5);
  const reactor = member("monster-1", "monsters", monsterTemplate(reactorId), 0);
  const target = member("monster-2", "monsters", monsterTemplate("srd-commoner"), 30);
  const fight = { heroes: [mover], monsters: [reactor, target] }; S.beginTurn(mover.state);
  return { mover, reactor, target, fight };
}

{
  dice(); const { mover, reactor, target, fight } = threeWay();
  const result = W.moveToward(1, 1, mover, target, fight, 5);
  assert.equal(result.events.length, 1); assert.equal(result.events[0].feature_id, "opportunity-attack");
  assert.equal(result.sequence, 2); assert.ok(result.movement); assert.equal(mover.position_ft, 25);
  assert.equal(reactor.state.reaction_available, false);
}
{
  dice(); const mover = member("hero-1", "heroes", heroTemplate(), 0);
  const target = member("monster-1", "monsters", monsterTemplate("srd-commoner"), 30);
  const fight = { heroes: [mover], monsters: [target] }; S.beginTurn(mover.state);
  const result = W.moveToward(1, 1, mover, target, fight, 5);
  assert.equal(result.events.length, 0); assert.ok(result.movement); assert.equal(target.state.reaction_available, true);
}
{
  dice(19); const { mover, reactor, target, fight } = threeWay("srd-crocodile"), before = mover.position_ft;
  const result = W.moveToward(1, 1, mover, target, fight, 5);
  assert.equal(result.events.length, 1); assert.equal(result.events[0].feature_id, "opportunity-attack");
  assert.equal(result.movement, null); assert.equal(mover.position_ft, before);
  assert.ok(mover.state.active_effect_ids.includes("grappled")); assert.ok(mover.state.active_effect_ids.includes("restrained"));
}
{
  dice(); const { mover, reactor, target, fight } = threeWay();
  const result = W.moveToward(1, 1, mover, target, fight, 5, "forced");
  assert.equal(result.events.length, 0); assert.ok(result.movement); assert.equal(reactor.state.reaction_available, true);
}
console.log("Browser reaction-aware movement regressions passed.");
