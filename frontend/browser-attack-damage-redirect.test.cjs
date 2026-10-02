"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
};
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  canSee: () => true,
};
let captured = null;
window.IRON_PIT_BROWSER_SAVES = {
  resolveAction: (sequence, round, actor, target, action, distance, options) => {
    captured = { sequence, round, actor, target, action, distance, options };
    actor.state.resources[action.resourceId] -= action.resourceCost || 1;
    return {
      sequence,
      round_number: round,
      event_type: "saving_throw",
      actor_id: actor.combatant_id,
      actor_name: actor.state.template.name,
      target_id: target.combatant_id,
      target_name: target.state.template.name,
      feature_id: action.id,
      save_ability: action.saveAbility,
      save_dc: action.dc,
      damage_roll: { total: 12 },
      damage_components: [{ damage_type: action.damageType, applied_total: 12 }],
      hp_before: 30,
      hp_after: 18,
      temporary_hp_before: 0,
      temporary_hp_after: 0,
    };
  },
};

load("browser-attack-damage-redirect.js");

const monk = {
  combatant_id: "kael",
  side: "heroes",
  position_ft: 0,
  state: {
    resources: { "focus-points": 13 },
    template: {
      name: "Kael Stillwater",
      ability_scores: { dexterity: 20 },
      attackDamageReductionReaction: {
        sourceId: "deflect-attacks",
        zeroDamageRedirect: {
          sourceId: "deflect-attacks-redirect",
          sourceName: "Deflect Attacks",
          resourceId: "focus-points",
          resourceCost: 1,
          meleeRangeFt: 5,
          rangedRangeFt: 60,
          saveAbility: "dexterity",
          saveDc: 14,
          damageDiceCount: 2,
          damageDiceSize: 10,
          damageBonusAbility: "dexterity",
          requiresSight: true,
          requiresClearLine: true,
        },
      },
    },
  },
};

const attacker = {
  combatant_id: "fire-mage",
  side: "monsters",
  position_ft: 30,
  state: {
    is_alive: true,
    is_dead: false,
    current_hp: 30,
    template: {
      name: "Fire Mage",
      attacks: [{ id: "fire-bolt", kind: "ranged", damageType: "fire" }],
    },
  },
};

const setup = { heroes: [monk], monsters: [attacker] };

{
  const event = window.IRON_PIT_BROWSER_ATTACK_DAMAGE_REDIRECT.resolve(
    2,
    1,
    attacker,
    {
      sequence: 1,
      actor_id: attacker.combatant_id,
      target_id: monk.combatant_id,
      attack_id: "fire-bolt",
      damage_reduction_zeroed_attack: true,
    },
    setup,
  );

  assert.ok(event);
  assert.equal(event.feature_id, "deflect-attacks-redirect");
  assert.equal(captured.actor.combatant_id, "kael");
  assert.equal(captured.target.combatant_id, "fire-mage");
  assert.equal(captured.action.damageType, "fire");
  assert.equal(captured.action.damageDiceCount, 2);
  assert.equal(captured.action.damageDiceSize, 10);
  assert.equal(captured.action.damageBonus, 5);
  assert.equal(captured.action.dc, 14);
  assert.equal(captured.distance, 30);
  assert.equal(captured.options.spendAction, false);
  assert.equal(monk.state.resources["focus-points"], 12);
}

{
  captured = null;
  const event = window.IRON_PIT_BROWSER_ATTACK_DAMAGE_REDIRECT.resolve(
    3,
    1,
    attacker,
    {
      sequence: 2,
      actor_id: attacker.combatant_id,
      target_id: monk.combatant_id,
      attack_id: "fire-bolt",
      damage_reduction_zeroed_attack: false,
    },
    setup,
  );
  assert.equal(event, null);
  assert.equal(captured, null);
}

console.log("Browser zero-damage attack redirect regressions passed.");
