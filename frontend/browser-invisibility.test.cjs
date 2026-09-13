const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

for (const file of [
  "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-modifiers.js", "browser-state.js", "browser-timed-conditions.js", "browser-concentration.js",
  "browser-invisibility.js", "browser-attack.js",
]) load(file);

const baseTemplate = (overrides = {}) => ({
  id: "test", name: "Test", kind: "monster", max_hp: 20, armor_class: 12, speed_ft: 30,
  movement_modes: { walk_ft: 30, fly_ft: 0, climb_ft: 0, swim_ft: 0, burrow_ft: 0 },
  primary_attack_id: "claw", attacks: [{ id: "claw" }], traits: [], condition_immunities: [], resources: {},
  ...overrides,
});

function member(id, side, template) {
  return { combatant_id: id, side, position_ft: 0, state: window.IRON_PIT_BROWSER_STATE.buildState(template) };
}

function testPermanentInvisibility() {
  const invisible = member("monster-1", "monsters", baseTemplate({ startsInvisible: true }));
  const visible = member("hero-1", "heroes", baseTemplate());
  assert.deepEqual(invisible.state.active_effect_ids, ["invisible"]);
  assert.deepEqual(window.IRON_PIT_BROWSER_ATTACK.conditionSources(invisible.state, visible.state, 5, visible.combatant_id), { advantage: 1, disadvantage: 0 });
  assert.deepEqual(window.IRON_PIT_BROWSER_ATTACK.conditionSources(visible.state, invisible.state, 5, invisible.combatant_id), { advantage: 0, disadvantage: 1 });
  assert.equal(window.IRON_PIT_BROWSER_INVISIBILITY.breakAfterAttack(invisible.state, { heroes: [visible], monsters: [invisible] }), false);
  assert.ok(invisible.state.active_effect_ids.includes("invisible"));
}

function testActionInvisibility() {
  const profile = { id: "invisibility", name: "Invisibility", actionCost: "action", concentration: true, endsOnAttack: true };
  const actor = member("monster-1", "monsters", baseTemplate({ invisibilityAction: profile }));
  const target = member("hero-1", "heroes", baseTemplate());
  const setup = { heroes: [target], monsters: [actor] };
  const event = window.IRON_PIT_BROWSER_INVISIBILITY.take(1, 1, actor, setup);
  assert.deepEqual(event.applied_condition_ids, ["invisible"]);
  assert.equal(actor.state.concentration.effect_id, "invisibility");
  assert.equal(actor.state.action_available, false);
  assert.equal(window.IRON_PIT_BROWSER_ATTACK.conditionSources(actor.state, target.state, 5, target.combatant_id).advantage, 1);
  assert.equal(window.IRON_PIT_BROWSER_INVISIBILITY.breakAfterAttack(actor.state, setup), true);
  assert.equal(actor.state.concentration, null);
  assert.ok(!actor.state.active_effect_ids.includes("invisible"));
}

try {
  testPermanentInvisibility();
  testActionInvisibility();
  console.log("browser invisibility parity tests passed");
} catch (error) {
  console.error("browser invisibility parity tests failed", error);
  process.exitCode = 1;
}
