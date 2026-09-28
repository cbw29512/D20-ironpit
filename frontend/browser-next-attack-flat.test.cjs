const assert = require("node:assert/strict");
global.window = global;
window.IRON_PIT_DICE = { roll: () => 1 };
window.IRON_PIT_BROWSER_EXHAUSTION = { effectiveSpeed: (_state, speed) => speed, d20Modifier: () => 0 };
window.IRON_PIT_BROWSER_DEBUFF_COUNTERS = { prevented: () => false };
require("./browser-modifiers.js");

const M = window.IRON_PIT_BROWSER_MODIFIERS;
const target = {
  template: { armor_class: 10, speed_ft: 30 },
  active_modifiers: [],
};

M.add(target, {
  id: "barbarian:sundering:target",
  source_id: "barbarian",
  source_effect_id: "sundering-blow",
  source_name: "Sundering Blow",
  kind: "next-attack-against-flat",
  flat_bonus: 5,
  consume_on_attack_against: true,
  expires_at_start_of_source_turn: true,
});

assert.equal(M.nextAttackAgainstFlat(target, "barbarian"), 0);
assert.equal(M.consumeNextAttackAgainstFlat(target, "barbarian"), 0);
assert.equal(target.active_modifiers.length, 1);
assert.equal(M.nextAttackAgainstFlat(target, "ally"), 5);
assert.equal(M.consumeNextAttackAgainstFlat(target, "ally"), 1);
assert.equal(M.nextAttackAgainstFlat(target, "other"), 0);
console.log("browser next-attack flat modifier parity ok");
