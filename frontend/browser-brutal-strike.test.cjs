const fs = require("fs");
const vm = require("vm");
const assert = require("assert");

global.window = global;
window.IRON_PIT_BROWSER_BARBARIAN2 = { active: (state) => state.active_effect_ids.includes("reckless-attack") };
window.IRON_PIT_BROWSER_MODIFIERS = {
  add(state, modifier) { state.active_modifiers.push(modifier); },
  nextAttackAgainstFlat(state, attackerId) { return state.active_modifiers.filter((item) => item.kind === "next-attack-against-flat" && item.source_id !== attackerId).reduce((sum, item) => sum + (item.flat_bonus || 0), 0); },
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
  template: { ruleset: "2024", level: 9, brutal_strike_damage_dice: 1, speed_ft: 40 },
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

B.staggering(state, "rokhan");
assert.deepStrictEqual(
  state.active_modifiers.filter((item) => item.source_effect_id === "staggering-blow").map((item) => item.kind).sort(),
  ["opportunity-attack-suppressed", "saving-throw-disadvantage"],
);

B.sundering(state, "rokhan");
assert.strictEqual(window.IRON_PIT_BROWSER_MODIFIERS.nextAttackAgainstFlat(state, "rokhan"), 0);
assert.strictEqual(window.IRON_PIT_BROWSER_MODIFIERS.nextAttackAgainstFlat(state, "ally"), 5);
B.sundering(state, "other-barbarian");
assert.strictEqual(state.active_modifiers.filter((item) => item.source_effect_id === "sundering-blow").length, 1);

console.log("browser brutal strike tests passed");

state.active_modifiers = [];
state.feature_last_turn_keys = { "brutal-strike": "9:rokhan" };
assert.deepStrictEqual(B.applyEffects(state, state, "rokhan", "9:rokhan"), ["hamstring-blow"]);

state.active_modifiers = [];
state.template.level = 13;
state.feature_last_turn_keys = { "brutal-strike": "13:rokhan" };
assert.deepStrictEqual(B.applyEffects(state, state, "rokhan", "13:rokhan"), ["staggering-blow"]);

state.active_modifiers = [];
state.template.level = 17;
state.feature_last_turn_keys = { "brutal-strike": "17:rokhan" };
assert.deepStrictEqual(B.applyEffects(state, state, "rokhan", "17:rokhan"), ["staggering-blow", "hamstring-blow"]);
