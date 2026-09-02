"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" ? state.action_available : state.bonus_action_available,
  spend: (state, cost) => { if (cost === "action") state.action_available = false; else state.bonus_action_available = false; },
};
window.IRON_PIT_BROWSER_STATE = {
  nearestTarget: (_member, setup) => setup.monsters[0],
  distance: () => 5,
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
      damage_bonus: attack.damageBonus,
    };
  },
};

for (const file of [
  "browser-weapon-mastery.js", "browser-light-weapons.js", "browser-light-attack.js",
  "browser-standard-attack-action.js", "browser-multiattack.js", "browser-action-surge.js",
]) load(file);

const scimitar = {
  id: "scimitar-attack", weaponId: "scimitar", name: "Scimitar", kind: "melee", reach: 5,
  bonus: 5, damageBonus: 3, attackAbilityModifier: 3, light: true, masteryProperty: "Nick",
};
const shortsword = {
  id: "shortsword-attack", weaponId: "shortsword", name: "Shortsword", kind: "melee", reach: 5,
  bonus: 5, damageBonus: 3, attackAbilityModifier: 3, light: true, masteryProperty: "Vex",
};

function fighter(masteries = ["scimitar"], withAction = false, fightingStyles = []) {
  return {
    combatant_id: "hero-1", side: "heroes", position_ft: 0,
    state: {
      template: {
        kind: "character", name: "Nick Fighter", attacks: [scimitar, shortsword], weapon_masteries: masteries,
        fighting_style: fightingStyles[0] || null, fighting_styles: fightingStyles,
        attack_action: withAction ? {
          id: "extra-attack", isAttackAction: true,
          slots: [{ attackIds: [scimitar.id] }, { attackIds: [scimitar.id] }],
        } : null,
      },
      action_available: true, bonus_action_available: true, is_dead: false, is_unconscious: false,
      feature_last_turn_keys: {}, resources: { "action-surge": 1 },
    },
  };
}
const target = {
  combatant_id: "monster-1", side: "monsters", position_ft: 5,
  state: { template: { kind: "monster", name: "Target" }, current_hp: 100, is_alive: true, is_dead: false, grapple_sources: [] },
};
const setup = { heroes: [], monsters: [target] };

{
  const member = fighter(); setup.heroes = [member];
  const result = window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION.resolve(
    1, 1, member, target, scimitar, 5, setup, "1:hero-1",
  );
  assert.equal(result.events.length, 2);
  assert.equal(result.events[1].feature_id, "weapon-mastery-nick");
  assert.equal(result.events[1].weapon_id, "shortsword");
  assert.equal(result.events[1].damage_bonus, 0, "positive ability modifier is removed");
  assert.equal(member.state.bonus_action_available, true, "Nick does not spend Bonus Action");

  const surge = window.IRON_PIT_BROWSER_ACTION_SURGE.resolveAttack(result.sequence, 1, member, setup, "1:hero-1");
  assert.ok(surge);
  assert.equal(surge.events.filter((event) => event.event_type === "attack").length, 1,
    "Action Surge cannot produce a second Nick attack in the same turn");
}

{
  const member = fighter(["scimitar"], false, ["Defense", "Two-Weapon Fighting"]); setup.heroes = [member];
  const result = window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION.resolve(
    1, 1, member, target, scimitar, 5, setup, "1:hero-1",
  );
  assert.equal(result.events.length, 2);
  assert.equal(result.events[1].feature_id, "weapon-mastery-nick");
  assert.equal(result.events[1].damage_bonus, 3, "Two-Weapon Fighting restores the normal ability modifier");
  assert.equal(member.state.bonus_action_available, true, "Two-Weapon Fighting does not change Nick action cost");
}

{
  const member = fighter([]); setup.heroes = [member];
  const result = window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION.resolve(
    1, 1, member, target, scimitar, 5, setup, "1:hero-1",
  );
  assert.equal(result.events.length, 2);
  assert.equal(result.events[1].feature_id, "light-extra-attack");
  assert.equal(member.state.bonus_action_available, false, "ordinary Light extra attack spends Bonus Action");
}

{
  const member = fighter(["scimitar"], true); setup.heroes = [member];
  const first = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, member, setup);
  assert.equal(first.events.filter((event) => event.event_type === "attack").length, 3);
  assert.equal(member.state.bonus_action_available, true);

  member.state.action_available = true;
  const second = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(first.sequence, 1, member, setup);
  assert.equal(second.events.filter((event) => event.event_type === "attack").length, 2,
    "second Attack action in one turn gets no additional Nick attack");
}

{
  const member = fighter(["scimitar"], true); setup.heroes = [member];
  member.state.template.attack_action.isAttackAction = false;
  const result = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, member, setup);
  assert.equal(result.events.filter((event) => event.event_type === "attack").length, 2,
    "monster-style Multiattack does not infer Light/Nick");
}

{
  const member = fighter();
  member.state.template.attacks = [scimitar];
  assert.equal(window.IRON_PIT_BROWSER_LIGHT_WEAPONS.plan(member.state, scimitar, "1:hero-1"), null,
    "a different Light weapon is required");
}

console.log("Browser Light/Nick/Two-Weapon Fighting regressions passed.");
