"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_DICE = {
  rolls: [],
  roll(sides) {
    if (!this.rolls.length) throw new Error("No queued d" + sides + " roll");
    return this.rolls.shift();
  },
};
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  incapacitated: (state) => Boolean(state.is_unconscious),
  has: (state, id) => (state.active_effect_ids || []).includes(id),
};
window.IRON_PIT_BROWSER_STATE = {
  distance(first, second) {
    return Math.max(
      Math.abs(first.state.position.x - second.state.position.x),
      Math.abs(first.state.position.y - second.state.position.y),
    ) * 5;
  },
  effectiveMaxHp(state) {
    return state.template.max_hp + (state.max_hp_bonus || 0) - (state.hit_point_maximum_reduction || 0);
  },
};
window.IRON_PIT_BROWSER_MODIFIERS = {
  add(state, modifier) {
    state.active_modifiers = [...(state.active_modifiers || []), modifier];
  },
};
window.IRON_PIT_BROWSER_TIMED = {
  apply(state, effectId, sourceId, options = {}) {
    state.timed_effects = [...(state.timed_effects || []), {
      effect_id: effectId,
      source_id: sourceId,
      source_effect_id: options.sourceEffectId || null,
      owned_damage_resistances: [...(options.ownedDamageResistances || [])],
      prevent_hit_point_maximum_reduction: false,
    }];
    state.active_effect_ids = [...(state.active_effect_ids || [])];
    if (!state.active_effect_ids.includes(effectId)) state.active_effect_ids.push(effectId);
    return effectId;
  },
};

load("browser-friendly-weapon-damage-auras.js");
load("browser-friendly-recovery-auras.js");

function combatant(id, side, x, y, extras = {}) {
  return {
    combatant_id: id,
    side,
    state: {
      template: {
        name: id,
        max_hp: extras.maxHp || 20,
        timed_self_buff_actions: extras.actions || [],
      },
      current_hp: extras.hp ?? extras.maxHp ?? 20,
      is_alive: true,
      is_dead: false,
      is_unconscious: Boolean(extras.unconscious),
      timed_effects: extras.effects || [],
      active_effect_ids: extras.effectIds || [],
      active_modifiers: [],
      position: { x, y },
      current_round: 1,
      hit_point_maximum_reduction: 0,
    },
  };
}

const mantle = {
  id: "crusaders-mantle",
  name: "Crusader's Mantle",
  friendlyWeaponDamageAura: { radius_ft: 30, dice_count: 1, dice_size: 4, damage_type: "radiant" },
};
const caster = combatant("aurelia", "heroes", 4, 7, {
  actions: [mantle],
  effects: [{ source_id: "aurelia", source_effect_id: "crusaders-mantle" }],
});
const ally = combatant("ally", "heroes", 5, 7);
const enemy = combatant("enemy", "monsters", 8, 7);
const setup = { heroes: [caster, ally], monsters: [enemy] };
window.IRON_PIT_BROWSER_FRIENDLY_WEAPON_DAMAGE_AURAS.sync(setup);
assert.equal(caster.state.active_modifiers[0].dice_size, 4);
assert.equal(caster.state.active_modifiers[0].damage_type, "radiant");
assert.equal(ally.state.active_modifiers[0].dice_count, 1);
assert.equal(enemy.state.active_modifiers.length, 0);

const vitality = {
  id: "aura-of-vitality",
  name: "Aura of Vitality",
  friendlyRecoveryAura: {
    radius_ft: 30, heal_dice_count: 2, heal_dice_size: 6, heal_flat: 0,
    heal_on_create: true, heal_on_source_turn_start: true,
  },
};
const healer = combatant("healer", "heroes", 4, 7, {
  actions: [vitality],
  effects: [{ source_id: "healer", source_effect_id: "aura-of-vitality" }],
  maxHp: 30,
  hp: 30,
});
const wounded = combatant("wounded", "heroes", 5, 7, { maxHp: 20, hp: 4 });
const vitalitySetup = { heroes: [healer, wounded], monsters: [enemy] };
window.IRON_PIT_DICE.rolls = [6, 5];
window.IRON_PIT_BROWSER_FRIENDLY_RECOVERY_AURAS.activate(healer, vitality, vitalitySetup, 1);
assert.equal(wounded.state.current_hp, 15);
wounded.state.current_hp = 2;
window.IRON_PIT_DICE.rolls = [4, 3];
window.IRON_PIT_BROWSER_FRIENDLY_RECOVERY_AURAS.resolveWindows(healer, vitalitySetup);
assert.equal(wounded.state.current_hp, 9);

const life = {
  id: "aura-of-life",
  name: "Aura of Life",
  damageResistances: ["necrotic"],
  friendlyRecoveryAura: {
    radius_ft: 30, zero_hp_ally_start_heal: 1, necrotic_resistance: true, prevent_hp_maximum_reduction: true,
  },
};
const lifeCaster = combatant("life-caster", "heroes", 4, 7, {
  actions: [life],
  effects: [{
    source_id: "life-caster",
    source_effect_id: "aura-of-life",
    owned_damage_resistances: ["necrotic"],
  }],
});
const downed = combatant("downed", "heroes", 5, 7, { maxHp: 16, hp: 0, unconscious: true });
const lifeSetup = { heroes: [lifeCaster, downed], monsters: [enemy] };
window.IRON_PIT_BROWSER_FRIENDLY_RECOVERY_AURAS.activate(lifeCaster, life, lifeSetup, 1);
assert.equal(window.IRON_PIT_BROWSER_FRIENDLY_RECOVERY_AURAS.applyHitPointMaximumReduction(downed.state, 8), 0);
assert.equal(downed.state.hit_point_maximum_reduction, 0);
assert.ok(downed.state.timed_effects.some((item) =>
  item.effect_id === "recovery-share" && item.owned_damage_resistances.includes("necrotic")));
window.IRON_PIT_BROWSER_FRIENDLY_RECOVERY_AURAS.resolveWindows(downed, lifeSetup);
assert.equal(downed.state.current_hp, 1);
assert.equal(downed.state.is_unconscious, false);
console.log("browser recovery and weapon aura tests passed");
