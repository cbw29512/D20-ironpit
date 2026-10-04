"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: (state) => state.is_unconscious };
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs((a.state.position?.x || 0) - (b.state.position?.x || 0)) * 5,
};
window.IRON_PIT_BROWSER_ATTACK = {
  resolveAttack: (sequence, round, attacker, target, attack) => {
    target.state.current_hp -= 8;
    return {
      sequence, round_number: round, event_type: "attack",
      actor_id: attacker.combatant_id, actor_name: attacker.state.template.name,
      target_id: target.combatant_id, description: `${attacker.state.template.name} hits with ${attack.name}.`,
    };
  },
};
window.IRON_PIT_DICE = {
  rollMany: (count) => Array.from({ length: count }, () => 6),
};
window.IRON_PIT_BROWSER_SAVES = {
  resolveAction: (sequence, round, actor, target, action, _distance, options = {}) => {
    const roll = (options.forcedRoll != null) ? options.forcedRoll : 1;
    const succeeded = roll >= action.dc;
    if (!succeeded) {
      target.state.current_hp -= (action.damageBonus || 0) + 12;
      if (action.failedSaveTimedEffect?.effectId) {
        target.state.active_effect_ids.push(action.failedSaveTimedEffect.effectId);
      }
      if ((action.failedSavePushFt || 0) > 0) {
        target.state.position.x += 2;
      }
    }
    return {
      sequence, round_number: round, event_type: "saving_throw",
      actor_id: actor.combatant_id, actor_name: actor.state.template.name,
      target_id: target.combatant_id, save_succeeded: succeeded,
      description: `${target.state.template.name} ${succeeded ? "SUCCEEDS" : "FAILS"} the save.`,
    };
  },
};

load("browser-legendary-actions.js");

function member(id, side, x, extras = {}) {
  return {
    combatant_id: id, side,
    state: {
      template: {
        name: id, attacks: extras.attacks || [],
        legendary_actions: extras.legendary_actions || [],
      },
      current_hp: extras.hp ?? 40,
      is_alive: true, is_dead: false, is_unconscious: false,
      resources: { "legendary-actions": extras.uses ?? 3 },
      active_effect_ids: extras.active_effect_ids || [],
      position: { x, y: 0 },
    },
  };
}

{
  const legend = member("legend", "monsters", 0, {
    attacks: [{ id: "tail", name: "Tail", diceCount: 2, diceSize: 8, damageBonus: 4, reach: 15 }],
    legendary_actions: [{ id: "tail-attack", name: "Tail Attack", cost: 1, kind: "attack", attack_id: "tail" }],
  });
  const hero = member("hero", "heroes", 2, { hp: 30, legendary_actions: [] });
  const setup = { heroes: [hero], monsters: [legend] };
  const result = window.IRON_PIT_BROWSER_LEGENDARY_ACTIONS.resolveAfterTurn(1, 1, hero, setup);
  assert.equal(result.events.length, 1);
  assert.match(result.events[0].description, /Legendary Action: Tail Attack/);
  assert.equal(legend.state.resources["legendary-actions"], 2);
  assert.equal(hero.state.current_hp, 22);
}

{
  const legend = member("legend", "monsters", 0, {
    attacks: [{ id: "tail", name: "Tail", diceCount: 2, diceSize: 8, damageBonus: 4, reach: 5 }],
    legendary_actions: [{ id: "tail-attack", name: "Tail Attack", cost: 1, kind: "attack", attack_id: "tail" }],
  });
  const hero = member("hero", "heroes", 8, { hp: 30 });
  const setup = { heroes: [hero], monsters: [legend] };
  const result = window.IRON_PIT_BROWSER_LEGENDARY_ACTIONS.resolveAfterTurn(1, 1, hero, setup);
  assert.equal(result.events.length, 0);
  assert.equal(legend.state.resources["legendary-actions"], 3);
}

{
  const legend = member("legend", "monsters", 0, {
    legendary_actions: [{
      id: "wing-attack", name: "Wing Attack", cost: 2, kind: "save",
      save_action: {
        id: "legendary-wing-attack", name: "Wing Attack",
        save_ability: "dexterity", dc: 19, range_ft: 10,
        area: { shape: "emanation", origin: "self", radius_ft: 10 },
        damage_dice_count: 2, damage_dice_size: 6, damage_bonus: 6,
        damage_type: "bludgeoning", success_damage: "none",
        failed_save_timed_effect: { effect_id: "prone" },
      },
    }],
  });
  const hero = member("hero", "heroes", 1, { hp: 30 });
  const startX = legend.state.position.x;
  const setup = { heroes: [hero], monsters: [legend] };
  const result = window.IRON_PIT_BROWSER_LEGENDARY_ACTIONS.resolveAfterTurn(1, 1, hero, setup);
  assert.equal(result.events.length, 1);
  assert.match(result.events[0].description, /Legendary Action: Wing Attack/);
  assert.equal(result.events[0].save_succeeded, false);
  assert.ok(hero.state.active_effect_ids.includes("prone"));
  assert.equal(legend.state.resources["legendary-actions"], 1);
  assert.equal(legend.state.position.x, startX);
}

{
  const legend = member("legend", "monsters", 0, {
    attacks: [{ id: "tail", name: "Tail", diceCount: 2, diceSize: 8, damageBonus: 4, reach: 15 }],
    legendary_actions: [
      { id: "tail-attack", name: "Tail Attack", cost: 1, kind: "attack", attack_id: "tail" },
      {
        id: "wing-attack", name: "Wing Attack", cost: 2, kind: "save",
        save_action: {
          id: "legendary-wing-attack", name: "Wing Attack",
          save_ability: "dexterity", dc: 19, range_ft: 10,
          area: { shape: "emanation", origin: "self", radius_ft: 10 },
          damage_dice_count: 2, damage_dice_size: 6, damage_bonus: 6,
        },
      },
    ],
  });
  const hero = member("hero", "heroes", 1, { hp: 30 });
  const setup = { heroes: [hero], monsters: [legend] };
  const chosen = window.IRON_PIT_BROWSER_LEGENDARY_ACTIONS.choose(legend, setup);
  assert.equal(chosen.kind, "attack");
  assert.equal(chosen.option.id, "tail-attack");
}

console.log("Legendary Action after-turn attack and save paths passed.");
