"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
load("browser-action-economy.js");
load("browser-state.js");
load("browser-spellcasting.js");
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount) => amount,
  applyDamage: (state, amount) => { state.current_hp -= amount; },
};
window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = {
  resolveDamage: (_state, amount) => ({ applied: amount, healed: 0, sourceName: null }),
};
window.IRON_PIT_BROWSER_OFFENSE_VALUE = {
  autoHitSpell: (_target, action, count) => count * (3.5 + action.damageBonus),
};
load("browser-auto-hit-spell-policy.js");
load("browser-auto-hit-spell.js");

const action = {
  id: "magic-missile", name: "Magic Missile", level: 1, actionCost: "action", range: 120,
  projectileCount: 3, projectilesPerSlotAbove: 1,
  damageDiceCount: 1, damageDiceSize: 4, damageBonus: 1, damageType: "force",
};
function member(id, side, actions = []) {
  const template = {
    id, name: id, kind: side === "monsters" ? "monster" : "character", ruleset: "2014",
    size: "medium", max_hp: 30, speed_ft: 30,
    movement_modes: { walk_ft: 30, fly_ft: 0, climb_ft: 0, swim_ft: 0, burrow_ft: 0, hover: false },
    resources: {}, auto_hit_spell_actions: actions,
    alternate_spell_cast_grants: actions.length ? [{
      source_id: "magic-missile", source_name: "Magic Missile", spell_id: "magic-missile",
      cast_level: 1, resource_id: null, resource_cost: 1, priority: 0,
    }] : [],
    damage_resistances: [], damage_immunities: [], damage_vulnerabilities: [],
  };
  return { combatant_id: id, side, position_ft: side === "monsters" ? 0 : 30,
    state: window.IRON_PIT_BROWSER_STATE.buildState(template) };
}

const caster = member("night-hag", "monsters", [action]);
const target = member("target", "heroes");
const setup = { heroes: [target], monsters: [caster] };
const immutableAction = JSON.stringify(action);
const choice = window.IRON_PIT_BROWSER_AUTO_HIT_SPELL_POLICY.choose(caster, setup, "1:night-hag");
assert.ok(choice);
assert.equal(choice.alternateCast.resource_id, null);
assert.equal(choice.projectileCount, 3);
window.IRON_PIT_DICE = { rollMany: () => [2] };
const event = window.IRON_PIT_BROWSER_AUTO_HIT_SPELL.resolve(
  1, 1, caster, target, setup, choice, "1:night-hag",
);
assert.equal(event.damage_roll.total, 9);
assert.equal(target.state.current_hp, 21);
assert.equal(event.resource_remaining, null);
assert.equal(caster.state.spell_slot_expended_turn_key, null);
assert.equal(caster.state.action_available, false);
assert.deepEqual(caster.state.resources, {});
assert.equal(JSON.stringify(action), immutableAction);

console.log("2014 innate at-will Magic Missile browser parity passed.");
