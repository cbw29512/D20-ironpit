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
  rollMany(count, sides) {
    return Array.from({ length: count }, () => this.roll(sides));
  },
};

load("browser-action-economy.js");
load("browser-resources.js");
load("browser-spellcasting.js");
load("browser-modifier-validation.js");
load("browser-modifiers.js");
load("browser-ability-hooks.js");
load("browser-attack-outcome.js");
load("browser-post-hit-damage.js");
load("browser-rolls.js");
load("browser-saving-throws.js");
load("browser-timed-conditions.js");
load("browser-grid-geometry.js");
load("browser-forced-movement.js");
load("browser-spell-modifiers.js");
load("browser-concentration.js");
load("browser-condition-immunity.js");
load("browser-post-hit-spell-riders.js");

function member(option) {
  const attacker = {
    combatant_id: "aurelia",
    state: {
      template: {
        name: "Aurelia Brightshield",
        size: "medium",
        saving_throw_bonuses: { strength: 0, constitution: 0, wisdom: 0 },
        post_hit_spell_options: [option],
      },
      current_hp: 40,
      timed_effects: [],
      active_effect_ids: [],
      active_modifiers: [],
      feature_last_turn_keys: {
        [option.id]: "1:aurelia",
        "paid-post-hit-spell": option.id,
        "paid-post-hit-slot": String(option.level),
      },
      concentration: null,
    },
  };
  const defender = {
    combatant_id: "enemy",
    state: {
      template: {
        name: "Commoner",
        size: "medium",
        saving_throw_bonuses: { strength: 0, constitution: 0, wisdom: 0 },
      },
      current_hp: 40,
      timed_effects: [],
      active_effect_ids: [],
      active_modifiers: [],
      position: { x: 5, y: 7 },
    },
  };
  return { attacker, defender };
}

function ctx(attacker, defender) {
  return {
    sequence: 1,
    round: 1,
    turnKey: "1:aurelia",
    member: attacker,
    target: defender,
    setup: {
      heroes: [attacker],
      monsters: [defender],
      map_definition: { width_squares: 16, height_squares: 16 },
    },
  };
}

const thunderous = {
  id: "thunderous-smite",
  name: "Thunderous Smite",
  level: 1,
  save_ability: "strength",
  save_dc: 13,
  failed_condition_id: "prone",
  failed_push_ft: 10,
};
window.IRON_PIT_DICE.rolls = [1];
const pronePair = member(thunderous);
pronePair.attacker.state.position = { x: 4, y: 7 };
window.IRON_PIT_BROWSER_POST_HIT_SPELL_RIDERS.applyRiders(ctx(pronePair.attacker, pronePair.defender));
assert.ok(pronePair.defender.state.active_effect_ids.includes("prone"));
assert.notEqual(pronePair.defender.state.position.x, 5);

const blinding = {
  id: "blinding-smite",
  name: "Blinding Smite",
  level: 3,
  concentration: true,
  duration_rounds: 10,
  save_ability: "constitution",
  save_dc: 15,
  failed_condition_id: "blinded",
  repeat_save_ability: "constitution",
  repeat_save_dc: 15,
  repeat_save_timing: "target_turn_end",
};
window.IRON_PIT_DICE.rolls = [1];
const blindPair = member(blinding);
window.IRON_PIT_BROWSER_POST_HIT_SPELL_RIDERS.applyRiders(ctx(blindPair.attacker, blindPair.defender));
assert.ok(blindPair.defender.state.active_effect_ids.includes("blinded"));
const timed = blindPair.defender.state.timed_effects.find((item) => item.effect_id === "blinded");
assert.equal(timed.repeat_save_ability, "constitution");
assert.equal(blindPair.attacker.state.concentration.effect_id, "blinding-smite");

const banishing = {
  id: "banishing-smite",
  name: "Banishing Smite",
  level: 5,
  concentration: true,
  duration_rounds: 10,
  exile_if_hp_at_or_below: 50,
};
const exilePair = member(banishing);
exilePair.defender.state.current_hp = 40;
window.IRON_PIT_BROWSER_POST_HIT_SPELL_RIDERS.applyRiders(ctx(exilePair.attacker, exilePair.defender));
assert.ok(exilePair.defender.state.active_effect_ids.includes("banished"));
assert.equal(
  exilePair.defender.state.timed_effects.find((item) => item.effect_id === "banished").removed_from_battlefield,
  true,
);
console.log("browser extra-smite rider tests passed");
