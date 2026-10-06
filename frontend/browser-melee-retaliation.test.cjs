const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;

window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = {
  resolveDamage: (_state, raw) => ({ applied: raw }),
};
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
};
window.IRON_PIT_DICE = {
  rollMany: (count, size) => Array.from({ length: count }, () => size),
};
window.IRON_PIT_BROWSER_ATTACK = {
  applyDamage: (state, amount) => { state.current_hp -= amount; },
};

vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-melee-retaliation.js"), "utf8"),
  { filename: "browser-melee-retaliation.js" },
);

const R = window.IRON_PIT_BROWSER_MELEE_RETALIATION;
const passive = {
  id: "azer-heated-body",
  name: "Heated Body",
  activationTiming: "passive",
  meleeHitRetaliation: { rangeFt: 5, diceCount: 1, diceSize: 10, damageType: "fire" },
};
const activated = {
  id: "fire-shield",
  name: "Fire Shield",
  activationTiming: "action",
  meleeHitRetaliation: { rangeFt: 5, diceCount: 2, diceSize: 8, damageType: "fire" },
};
const defender = {
  combatant_id: "defender",
  position_ft: 5,
  state: {
    current_hp: 30,
    is_alive: true,
    is_dead: false,
    timed_effects: [],
    template: { timed_self_buff_actions: [passive] },
  },
};
const attacker = {
  combatant_id: "attacker",
  position_ft: 0,
  state: { current_hp: 30, is_alive: true, is_dead: false, template: {} },
};

assert.equal(R.active(defender).action.id, "azer-heated-body");
assert.equal(R.apply(attacker, defender, { melee: true }), 10);
assert.equal(attacker.state.current_hp, 20);

attacker.position_ft = -5;
assert.equal(R.apply(attacker, defender, { melee: true }), 0);
assert.equal(attacker.state.current_hp, 20);

defender.state.template.timed_self_buff_actions = [activated];
assert.equal(R.active(defender), null);
defender.state.timed_effects.push({ source_effect_id: "fire-shield" });
assert.equal(R.active(defender).action.id, "fire-shield");

console.log("browser passive melee retaliation: ok");
