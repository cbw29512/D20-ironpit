const fs = require("fs");
const vm = require("vm");
const assert = require("assert");

global.window = global;
window.IRON_PIT_BROWSER_BARBARIAN2 = { active: (state) => state.active_effect_ids.includes("reckless-attack") };
window.IRON_PIT_BROWSER_MODIFIERS = {
  add(state, modifier) { state.active_modifiers.push(modifier); },
  effectiveSpeed(state) {
    return Math.max(0, state.template.speed_ft + state.active_modifiers
      .filter((item) => item.kind === "speed").reduce((sum, item) => sum + item.flat_bonus, 0));
  },
  expireSourceTurnStart(states, sourceId) {
    let removed = 0;
    for (const state of states) {
      const before = state.active_modifiers.length;
      state.active_modifiers = state.active_modifiers.filter((item) => !(item.source_id === sourceId && item.expires_at_start_of_source_turn));
      removed += before - state.active_modifiers.length;
    }
    return removed;
  },
};
vm.runInThisContext(fs.readFileSync("frontend/browser-brutal-strike.js", "utf8"));

const B = window.IRON_PIT_BROWSER_BRUTAL_STRIKE;
const attack = { attackAbility: "strength", damageType: "slashing" };
const state = {
  template: { ruleset: "2024", brutal_strike_damage_dice: 1, brutal_strike_sundering: false, speed_ft: 40 },
  active_effect_ids: ["reckless-attack"], active_modifiers: [], feature_last_turn_keys: {},
};

assert.strictEqual(B.advantageSuppression(state, attack, "1:rokhan"), 1);
assert.deepStrictEqual(B.bonusDamage(state, attack, "1:rokhan"), {
  source: "Brutal Strike", diceCount: 1, diceSize: 10, damageType: "slashing",
});
assert.strictEqual(B.bonusDamage(state, attack, "1:rokhan"), null);

const disadvantaged = { ...state, feature_last_turn_keys: {} };
assert.strictEqual(B.advantageSuppression(disadvantaged, attack, "2:rokhan", true), 0);
assert.strictEqual(B.bonusDamage(disadvantaged, attack, "2:rokhan", true), null);

state.template.brutal_strike_damage_dice = 2;
state.feature_last_turn_keys = {};
assert.strictEqual(B.bonusDamage(state, attack, "3:rokhan").diceCount, 2);

B.hamstring(state, "rokhan");
assert.strictEqual(window.IRON_PIT_BROWSER_MODIFIERS.effectiveSpeed(state), 25);
assert.strictEqual(window.IRON_PIT_BROWSER_MODIFIERS.expireSourceTurnStart([state], "rokhan"), 1);
assert.strictEqual(window.IRON_PIT_BROWSER_MODIFIERS.effectiveSpeed(state), 40);

console.log("browser brutal strike tests passed");


{
  const attacker = {
    template: { ruleset: "2024", brutal_strike_damage_dice: 1, brutal_strike_sundering: true, speed_ft: 40 },
    active_effect_ids: ["reckless-attack"], active_modifiers: [], feature_last_turn_keys: {},
  };
  const defender = { template: { speed_ft: 30 }, active_modifiers: [] };
  assert.strictEqual(B.sundering(attacker, defender, "rokhan", "4:rokhan"), false);
  assert.ok(B.bonusDamage(attacker, attack, "4:rokhan"));
  assert.strictEqual(B.sundering(attacker, defender, "rokhan", "4:rokhan"), true);
  const modifier = defender.active_modifiers.find((item) => item.source_effect_id === "sundering-blow");
  assert.strictEqual(modifier.flat_bonus, 5);
  assert.strictEqual(modifier.source_id, "rokhan");
  assert.strictEqual(modifier.expires_at_start_of_source_turn, true);
}
