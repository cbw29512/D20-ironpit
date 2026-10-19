"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
let succeeds = false;
let damageCalls = 0, zeroCalls = 0;
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow: () => ({
    roll: { notation: "1d20", total: succeeds ? 20 : 1 },
    succeeded: succeeds,
  }),
};
window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = {
  resolveDamage: (_state, total) => ({ applied: total, healed: 0 }),
};
window.IRON_PIT_BROWSER_ROGUE_DEFENSES = {
  evasionDamage: (_state, _ability, _passed, _successDamage, total) => total,
};
window.IRON_PIT_BROWSER_ATTACK = {
  applyDamage: (state, amount) => {
    damageCalls += 1;
    state.current_hp = Math.max(0, state.current_hp - amount);
    return "damaged";
  },
};
window.IRON_PIT_BROWSER_ZERO_HP = {
  reduceToZero: (state) => {
    zeroCalls += 1;
    state.current_hp = 0;
    if (state.template.kind === "monster") {
      state.is_dead = true; state.is_alive = false;
    } else {
      state.is_unconscious = true;
    }
    return state.is_dead ? "dead" : "unconscious";
  },
};
window.IRON_PIT_BROWSER_DICE = { rollMany: () => [1, 2, 3] };
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = { saveAdvantageSourceNames: () => [] };
window.IRON_PIT_BROWSER_CONCENTRATION = { endIfIncapacitated: () => {} };
load("browser-saves.js");
const S = window.IRON_PIT_BROWSER_SAVES;

function member(id, side, kind) {
  return { combatant_id: id, side,
    state: {
      template: { id, name: id, kind, creature_type: "humanoid",
        saving_throw_bonuses: { constitution: 0 } },
      current_hp: 40, temporary_hp: 9, is_alive: true, is_dead: false,
      is_unconscious: false, is_stable: false, active_effect_ids: [],
      death_save_successes: 0, death_save_failures: 0,
      action_available: true, resources: {},
    },
  };
}
const caster = member("renamed-source", "monsters", "monster");
const ally = member("friend", "monsters", "monster");
const foe = member("foe", "heroes", "character");
const setup = { heroes: [foe], monsters: [caster, ally] };
const action = {
  id: "renamed-effect", name: "Any Homebrew Save",
  saveAbility: "constitution", dc: 13, range: 30,
  damageDiceCount: 3, damageDiceSize: 6, damageBonus: 0,
  damageType: "psychic", successDamage: "none",
  failureSetsZeroHp: true, damageOnlyOnSuccess: true,
};
function resolve(target, effectiveAction = action) {
  return S.resolveAction(1, 1, caster, target, effectiveAction, 5, {
    spendAction: false, checkResource: false, spendResource: false, setup,
  });
}

succeeds = false;
const fail = resolve(ally);
assert.equal(fail.save_succeeded, false);
assert.equal(ally.state.current_hp, 0);
assert.equal(ally.state.temporary_hp, 9, "Failed zero HP does not consume temporary HP");
assert.equal(ally.state.is_dead, true);
assert.equal(fail.damage_roll, null);
assert.equal(damageCalls, 0);
assert.equal(zeroCalls, 1);
assert.match(fail.description, /directly to 0 HP/);

succeeds = true;
const before = foe.state.current_hp;
const passed = resolve(foe);
assert.equal(passed.save_succeeded, true);
assert.equal(foe.state.current_hp, before - 6);
assert.deepEqual(passed.damage_roll.rolls, [1, 2, 3]);
assert.equal(damageCalls, 1);
assert.equal(zeroCalls, 1, "Passed save cannot trigger zero HP");

// Existing save Actions retain normal 'pass = no damage' behavior by default.
const old = member("old-target", "heroes", "character");
const ordinary = { ...action, failureSetsZeroHp: false, damageOnlyOnSuccess: false };
const oldEvent = resolve(old, ordinary);
assert.equal(oldEvent.save_succeeded, true);
assert.equal(old.state.current_hp, 40);
assert.equal(damageCalls, 1);
console.log("Browser asymmetric saved-result zero-HP/typed-damage parity passed.");
