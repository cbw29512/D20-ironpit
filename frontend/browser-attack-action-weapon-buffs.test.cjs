"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;

const added = [];
window.IRON_PIT_BROWSER_MODIFIERS = {
  add: (state, modifier) => { state.active_modifiers.push(modifier); added.push(modifier); },
  damageSourceQualifiers: () => new Set(["attack", "weapon", "melee"]),
};
window.IRON_PIT_BROWSER_RESOURCES = {
  available: (state, id, cost) => (state.resources[id] || 0) >= cost,
  spend: (state, id, cost) => {
    state.resources[id] -= cost;
    return state.resources[id];
  },
};
window.IRON_PIT_BROWSER_TIMED = {
  apply: (state, effectId, sourceId, options) => {
    state.timed_effects.push({
      effect_id: effectId,
      source_id: sourceId,
      source_effect_id: options.sourceEffectId,
    });
    return effectId;
  },
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (target, amount, damageType) => {
    if ((target.template.damage_resistances || []).includes(damageType)) return Math.floor(amount / 2);
    return amount;
  },
};

for (const file of ["browser-attack-action-weapon-buffs.js", "browser-rolls.js"]) {
  vm.runInThisContext(fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file });
}

const member = {
  combatant_id: "aurelia",
  state: {
    resources: { "channel-divinity": 2 },
    timed_effects: [],
    active_modifiers: [],
    template: {
      name: "Aurelia Brightshield",
      attacks: [{ id: "aurelia-longsword", weaponId: "longsword", name: "Longsword" }],
      attack_action_weapon_buffs: [{
        id: "sacred-weapon",
        name: "Sacred Weapon",
        resourceId: "channel-divinity",
        resourceCost: 1,
        weaponId: "longsword",
        durationRounds: 100,
        attackRollBonus: 2,
        damageTypeChoice: "radiant",
        sourceIsMagical: true,
      }],
      damage_resistance_bypass_grants: [],
    },
  },
};

const event = window.IRON_PIT_BROWSER_ATTACK_ACTION_WEAPON_BUFFS.resolve(1, 1, member);
assert.ok(event);
assert.equal(event.feature_id, "sacred-weapon");
assert.equal(member.state.resources["channel-divinity"], 1);
assert.equal(added.find((item) => item.kind === "attack-roll-flat").flat_bonus, 2);
assert.equal(added.find((item) => item.kind === "weapon-damage-type-choice").damage_type, "radiant");

const attack = {
  id: "aurelia-longsword",
  weaponId: "longsword",
  name: "Longsword",
  kind: "melee",
  damageType: "slashing",
  damageTypeChoices: [],
};
assert.equal(
  window.IRON_PIT_BROWSER_ROLLS.chooseDamageType(
    member.state,
    attack,
    { template: { damage_resistances: ["slashing"], damage_immunities: [], damage_vulnerabilities: [] } },
    ["attack", "weapon", "melee"],
  ),
  "radiant",
);
assert.equal(window.IRON_PIT_BROWSER_ATTACK_ACTION_WEAPON_BUFFS.resolve(2, 2, member), null);
assert.equal(member.state.resources["channel-divinity"], 1);

// Prove the standard single-attack wrapper activates the generic buff before resolving the attack.
const order = [];
const actualResolve = window.IRON_PIT_BROWSER_ATTACK_ACTION_WEAPON_BUFFS.resolve;
window.IRON_PIT_BROWSER_ATTACK_ACTION_WEAPON_BUFFS.resolve = (...args) => {
  order.push("buff");
  return actualResolve(...args);
};
window.IRON_PIT_BROWSER_ATTACK.resolveAttack = () => {
  order.push("attack");
  return { event_type: "attack", attack_roll: { total: 20 }, hit: true };
};
window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH = null;
window.IRON_PIT_BROWSER_LIGHT_ATTACK = { resolve: (sequence) => ({ events: [], sequence }) };
window.IRON_PIT_BROWSER_WEAPON_MASTERY = {
  resolveCleave: (sequence) => ({ events: [], sequence }),
};
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-standard-attack-action.js"), "utf8"),
  { filename: "browser-standard-attack-action.js" },
);
member.state.turn_terminated = false;
window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION.resolve(
  3, 3, member,
  { combatant_id: "target", state: { template: { name: "Target" } } },
  { ...attack, light: false },
  5,
  { heroes: [member], monsters: [] },
  "3:aurelia",
);
assert.deepEqual(order, ["buff", "attack"]);

console.log("browser Attack-action weapon buff regressions passed");
