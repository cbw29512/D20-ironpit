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
  assert.equal(result.events[1].damage_bonus, 3, "Two-Weapon Fighting restores the normal ability modifier");
  assert.equal(member.state.bonus_action_available, true, "Two-Weapon Fighting does not change Nick action cost");
}

{
  const member = fighter([], false, ["Two-Weapon Fighting"]); setup.heroes = [member];
  const result = window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION.resolve(
    1, 1, member, target, shortsword, 5, setup, "1:hero-1",
  );
  assert.equal(result.events.length, 2);
  assert.equal(result.events[1].feature_id, "light-extra-attack");
  assert.equal(result.events[1].damage_bonus, 3, "TWF restores damage without requiring Nick");
  assert.equal(member.state.bonus_action_available, false, "ordinary Light extra attack still spends Bonus Action");
}

{
  const member = fighter([]); setup.heroes = [member];
  const result = window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION.resolve(
    1, 1, member, target, shortsword, 5, setup, "1:hero-1",
  );
  assert.equal(result.events.length, 2);
  assert.equal(result.events[1].feature_id, "light-extra-attack");
  assert.equal(result.events[1].damage_bonus, 0);
  assert.equal(member.state.bonus_action_available, false, "ordinary Light extra attack spends Bonus Action");
}

{
  const member = fighter(["scimitar"], true); setup.heroes = [member];
  const first = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, member, setup);
  const attacks = first.events.filter((event) => event.event_type === "attack");
  assert.equal(attacks.length, 3);
  assert.equal(attacks[2].weapon_id, "scimitar");
  assert.equal(attacks[2].feature_id, "weapon-mastery-nick");
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
  member.state.template.attacks = [shortsword];
  assert.equal(window.IRON_PIT_BROWSER_LIGHT_WEAPONS.plan(member.state, shortsword, "1:hero-1"), null,
    "a different Light weapon is required");
}

{
  const member = fighter(["greataxe"]); member.state.template.name = "Cleave Fighter"; member.state.template.attacks = [greataxe];
  const first = monster("cleave-first", 5), second = monster("cleave-second", 5);
  const cleaveSetup = { heroes: [member], monsters: [first, second] };
  const result = window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION.resolve(
    1, 1, member, first, greataxe, 5, cleaveSetup, "1:hero-1",
  );
  assert.equal(result.events.length, 2);
  assert.equal(result.events[1].target_id, "cleave-second");
  assert.equal(result.events[1].feature_id, "weapon-mastery-cleave");
  assert.equal(result.events[1].damage_bonus, 2, "Cleave removes only the positive ability modifier from damage");

  member.state.action_available = true;
  const again = window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION.resolve(
    result.sequence, 1, member, first, greataxe, 5, cleaveSetup, "1:hero-1",
  );
  assert.equal(again.events.length, 1, "Cleave can occur only once per turn");
}

{
  const member = fighter(["greataxe"], true); member.state.template.attacks = [greataxe];
  member.state.template.attack_action = {
    id: "extra-attack", isAttackAction: true,
    slots: [{ attackIds: [greataxe.id] }, { attackIds: [greataxe.id] }],
  };
  const cleaveSetup = { heroes: [member], monsters: [monster("multi-first", 5), monster("multi-second", 5)] };
  const result = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, member, cleaveSetup);
  const attacks = result.events.filter((event) => event.event_type === "attack");
  assert.equal(attacks.length, 3, "two base attacks can produce only one Cleave attack");
  assert.equal(attacks.filter((event) => event.feature_id === "weapon-mastery-cleave").length, 1);
}

{
  const member = fighter(["greataxe"]); member.state.template.attacks = [greataxe];
  const first = monster("far-first", 10), second = monster("far-second", 0);
  const cleaveSetup = { heroes: [member], monsters: [first, second] };
  const extended = { ...greataxe, reach: 10 };
  assert.equal(window.IRON_PIT_BROWSER_WEAPON_MASTERY.cleaveTarget(member, first, extended, cleaveSetup), null,
    "second target must be within 5 feet of the creature hit, not merely within attacker reach");
  assert.equal(window.IRON_PIT_BROWSER_WEAPON_MASTERY.resolveCleave(
    1, 1, member, { hit: false, target_id: first.combatant_id }, greataxe, cleaveSetup, "1:hero-1",
  ).events.length, 0, "a miss cannot trigger Cleave");
}

{
  const negative = { ...greataxe, damageBonus: -1, attackAbilityModifier: -1 };
  assert.equal(window.IRON_PIT_BROWSER_WEAPON_MASTERY.cleaveAttack(negative).damageBonus, -1,
    "negative ability modifiers remain in Cleave damage");
}

console.log("Browser Light/Nick/Two-Weapon Fighting/Cleave regressions passed.");
