const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const attackRuntime = {
  resolveAttack: (_sequence, _round, _attacker, target) => ({ hit: true, target_id: target.combatant_id, description: "hit" }),
  adjustedDamage: (_state, amount) => amount,
  applyDamage: (state, amount) => { state.current_hp -= amount; },
};
global.window = {
  IRON_PIT_BROWSER_ATTACK: attackRuntime,
  IRON_PIT_DICE: { rollMany: (count, size) => { assert.equal(count, 1); assert.equal(size, 10); return [7]; } },
  IRON_PIT_BROWSER_STATE: { distance: () => 5 },
};
vm.runInThisContext(fs.readFileSync(require.resolve("./browser-reactive-damage.js"), "utf8"), { filename: "browser-reactive-damage.js" });

const attacker = { combatant_id: "hero-1", state: { current_hp: 20, is_dead: false, template: { name: "Hero" } } };
const defender = { combatant_id: "azer-1", state: { template: { name: "Azer", meleeHitReactiveDamage: [
  { id: "heated-body", rangeFt: 5, diceCount: 1, diceSize: 10, damageBonus: 0, damageType: "fire" },
] } } };
const setup = { heroes: [attacker], monsters: [defender] };
const event = attackRuntime.resolveAttack(1, 1, attacker, defender, { kind: "melee" }, 5, { setup });
assert.equal(attacker.state.current_hp, 13);
assert.equal(event.actor_hp_before, 20);
assert.equal(event.actor_hp_after, 13);
assert.equal(event.reactive_damage_roll.total, 7);
assert.equal(event.reactive_damage_components[0].damage_type, "fire");
console.log("Browser 2014 Heated Body parity regression passed.");
