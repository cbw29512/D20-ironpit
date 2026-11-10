"use strict";

// Deterministic browser contract for any save Action whose damage reduces max HP.
// Exercise the real shared maximum-HP runtime, not a monster-named resolver.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => Math.max(
    1, state.template.max_hp + (state.max_hp_bonus || 0)
      - (state.hit_point_maximum_reduction || 0),
  ),
};
window.IRON_PIT_BROWSER_ATTACK = {
  applyDamage(state, amount) {
    const soaked = Math.min(state.temporary_hp || 0, amount);
    state.temporary_hp -= soaked;
    state.current_hp = Math.max(0, state.current_hp - (amount - soaked));
    return "damaged";
  },
};
window.IRON_PIT_BROWSER_SAVE_DAMAGE = {
  resolve(_state, action, succeeded) {
    const applied = action.immune ? 0 : succeeded ? 7 : 15;
    return {
      appliedTotal: applied, components: [],
      damageTypes: applied ? ["psychic"] : [], roll: applied ? { total: applied } : null,
    };
  },
};
window.IRON_PIT_BROWSER_SAVE_DAMAGE_LEGACY = { resolve: () => null };
load("browser-maximum-hp.js");
load("browser-save-damage-apply.js");

const target = (hp = 40, temporaryHp = 0) => ({
  combatant_id: "synthetic-target",
  state: {
    template: { max_hp: hp }, current_hp: hp, temporary_hp: temporaryHp,
    max_hp_bonus: 0, hit_point_maximum_reduction: 0,
    timed_effects: [], is_alive: true, is_dead: false,
    is_unconscious: false, is_stable: false,
    death_save_successes: 0, death_save_failures: 0,
  },
});
const action = (extra = {}) => ({
  id: "renamed-save", name: "Renamed Source Action",
  reduceHitPointMaximumOnDamage: true, maxHpZeroKills: false,
  successDamage: "half", ...extra,
});

for (const [succeeded, expected] of [[false, 15], [true, 7]]) {
  const victim = target();
  window.IRON_PIT_BROWSER_SAVE_DAMAGE_APPLY.resolveAndApply(
    victim, action(), succeeded,
  );
  assert.equal(victim.state.current_hp, 40 - expected);
  assert.equal(victim.state.hit_point_maximum_reduction, expected);
  assert.equal(victim.state.template.max_hp, 40, "source template must not mutate");
}

{
  // HP-maximum-zero is terminal even if the typed attack only depleted temp HP.
  const victim = target(10, 100);
  window.IRON_PIT_BROWSER_SAVE_DAMAGE_APPLY.resolveAndApply(
    victim, action({ maxHpZeroKills: true }), false,
  );
  assert.equal(victim.state.hit_point_maximum_reduction, 15);
  assert.equal(victim.state.current_hp, 0);
  assert.equal(victim.state.is_dead, true);
  assert.equal(victim.state.is_alive, false);
  assert.equal(victim.state.template.max_hp, 10);
}

{
  const victim = target();
  window.IRON_PIT_BROWSER_SAVE_DAMAGE_APPLY.resolveAndApply(
    victim, action({ immune: true }), false,
  );
  assert.equal(victim.state.hit_point_maximum_reduction, 0);
  assert.equal(victim.state.current_hp, 40);
}

{
  const victim = target();
  victim.state.timed_effects.push({ prevent_hit_point_maximum_reduction: true });
  window.IRON_PIT_BROWSER_SAVE_DAMAGE_APPLY.resolveAndApply(
    victim, action(), false,
  );
  assert.equal(victim.state.hit_point_maximum_reduction, 0);
  assert.equal(victim.state.current_hp, 25);
}

console.log("Browser universal save-damage maximum-HP regressions passed.");
