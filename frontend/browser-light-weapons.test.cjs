"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" ? state.action_available : state.bonus_action_available,
  resourceAvailable: (state, action) => !action.resourceId || (state.resources?.[action.resourceId] || 0) >= (action.resourceCost || 1),
  spend: (state, cost) => { if (cost === "action") state.action_available = false; else state.bonus_action_available = false; },
};
window.IRON_PIT_BROWSER_STATE = {
  nearestTarget: (_member, setup) => setup.monsters[0],
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
  packTactics: () => false,
  sizeAtMost: () => true,
};
window.IRON_PIT_BROWSER_CHARGE = { openingFeature: () => null };
window.IRON_PIT_BROWSER_SAVES = { legalAction: () => false };
window.IRON_PIT_BROWSER_ATTACK = {
  resolveAttack: (sequence, round, member, target, attack, _distance, options = {}) => {
    if (options.spendAction !== false) window.IRON_PIT_ACTION_ECONOMY.spend(member.state, "action");
    return {
      sequence, round_number: round, event_type: "attack", actor_id: member.combatant_id,
      target_id: target.combatant_id, weapon_id: attack.weaponId, feature_id: options.featureId || null,
      damage_bonus: attack.damageBonus, hit: true,
      description: `${member.state.template.name} hits ${target.state.template.name}.`,
    };
  },
};

for (const file of [
  "browser-weapon-mastery.js", "browser-light-weapons.js", "browser-light-attack.js",
  "browser-standard-attack-action.js", "browser-formation.js", "browser-multiattack.js", "browser-action-surge.js",
]) load(file);

const scimitar = {
  id: "scimitar-attack", weaponId: "scimitar", name: "Scimitar", kind: "melee", reach: 5,
  bonus: 5, damageBonus: 3, attackAbilityModifier: 3, light: true, masteryProperty: "Nick",
};
const shortsword = {
  id: "shortsword-attack", weaponId: "shortsword", name: "Shortsword", kind: "melee", reach: 5,
  bonus: 5, damageBonus: 3, attackAbilityModifier: 3, light: true, masteryProperty: "Vex",
};
const greataxe = {
  id: "greataxe-attack", weaponId: "greataxe", name: "Greataxe", kind: "melee", reach: 5,
  bonus: 5, damageBonus: 5, attackAbilityModifier: 3, light: false, masteryProperty: "Cleave",
};

function fighter(masteries = ["scimitar"], withAction = false, fightingStyles = []) {
  return {
    combatant_id: "hero-1", side: "heroes", position_ft: 0,
    state: {
      template: {
        kind: "character", name: "Nick Fighter", attacks: [shortsword, scimitar], weapon_masteries: masteries,
        fighting_style: fightingStyles[0] || null, fighting_styles: fightingStyles,
        attack_action: withAction ? {
          id: "extra-attack", isAttackAction: true,
          slots: [{ attackIds: [shortsword.id] }, { attackIds: [shortsword.id] }],
        } : null,
      },
      action_available: true, bonus_action_available: true, is_dead: false, is_unconscious: false,
      feature_last_turn_keys: {}, resources: { "action-surge": 1 },
    },
  };
}
function monster(id, position = 5) {
  return {
    combatant_id: id, side: "monsters", position_ft: position,
    state: { template: { kind: "monster", name: id }, current_hp: 100, is_alive: true, is_dead: false, grapple_sources: [] },
  };
}
const target = monster("monster-1");
const setup = { heroes: [], monsters: [target] };

{
  const member = fighter(); setup.heroes = [member];
  const result = window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION.resolve(
    1, 1, member, target, shortsword, 5, setup, "1:hero-1",
  );
  assert.equal(result.events.length, 2);
  assert.equal(result.events[1].feature_id, "weapon-mastery-nick");
  assert.equal(result.events[1].weapon_id, "scimitar");
  assert.equal(result.events[1].damage_bonus, 0, "positive ability modifier is removed");
  assert.equal(member.state.bonus_action_available, true, "Nick does not spend Bonus Action");

  const surge = window.IRON_PIT_BROWSER_ACTION_SURGE.resolveAttack(result.sequence, 1, member, setup, "1:hero-1");
  assert.ok(surge);
  assert.equal(surge.events.filter((event) => event.event_type === "attack").length, 1,
    "Action Surge cannot produce a second Nick attack in the same turn");
}

{
  const member = fighter(); setup.heroes = [member];
  member.state.template.attacks = [scimitar, shortsword];
  const result = window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION.resolve(
    1, 1, member, target, scimitar, 5, setup, "1:hero-1",
  );
  assert.equal(result.events[1].weapon_id, "shortsword");
  assert.equal(result.events[1].feature_id, "light-extra-attack",
    "Nick does not apply when the Nick weapon is only the trigger attack");
  assert.equal(member.state.bonus_action_available, false);
}

{
  const member = fighter(["scimitar"], false, ["Defense", "Two-Weapon Fighting"]); setup.heroes = [member];
  const result = window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION.resolve(
    1, 1, member, target, shortsword, 5, setup, "1:hero-1",
  );
  assert.equal(result.events.length, 2);
  assert.equal(result.events[1].feature_id, "weapon-mastery-nick");
  assert.equal(result.events[1].weapon_id, "scimitar");
  assert.equal(result.events[1].damage_bonus, 3, "Two-Weapon Fighting preserves ability modifier");
}

{
  const member = fighter([], false, ["Defense", "Two-Weapon Fighting"]); setup.heroes = [member];
  const result = window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION.resolve(
    1, 1, member, target, shortsword, 5, setup, "1:hero-1",
  );
  assert.equal(result.events[1].feature_id, "light-extra-attack");
  assert.equal(result.events[1].damage_bonus, 3, "Two-Weapon Fighting preserves ability modifier without Nick");
}

{
  const member = fighter([], false, ["Defense"]); setup.heroes = [member];
  member.state.template.attacks = [greataxe];
  const result = window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION.resolve(
    1, 1, member, target, greataxe, 5, setup, "1:hero-1",
  );
  assert.equal(result.events.length, 1, "non-Light weapon does not generate a Light extra attack");
}

console.log("Browser Light weapon attack regressions passed.");
