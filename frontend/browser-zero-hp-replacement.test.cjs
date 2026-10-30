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

window.IRON_PIT_BROWSER_GRAPPLE = { speedIsZero: () => false };
window.IRON_PIT_BROWSER_MODIFIERS = { effectiveSpeed: (state) => state.template.speed_ft || 30 };
window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: (state) => Boolean(state.is_unconscious) };
window.IRON_PIT_BROWSER_LEGENDARY_ACTIONS = { initialize: () => null, refresh: () => null };
window.IRON_PIT_BROWSER_CONCENTRATION = { resolveDamage: () => null, endIfIncapacitated: () => null };
window.IRON_PIT_BROWSER_UNDEAD_FORTITUDE = { resolve: () => false };
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS = { endDamageSensitive: () => [] };
window.IRON_PIT_BROWSER_REGENERATION = { noteDamageTypes: () => null, defersDeath: () => false };

load("browser-state.js");
load("browser-zero-hp.js");

function template(id, name, kind, maxHp) {
  return {
    id, name, kind, max_hp: maxHp, speed_ft: 30, size: "medium",
    resources: {}, traits: [], damage_immunities: [], damage_resistances: [],
  };
}

const sourceTemplate = template("srd-werewolf", "Werewolf", "monster", 58);
const targetTemplate = template("hero-target", "Target Hero", "character", 22);
const source = {
  combatant_id: "source-werewolf",
  side: "monsters",
  position_ft: 0,
  state: window.IRON_PIT_BROWSER_STATE.buildState(sourceTemplate),
};
const target = {
  combatant_id: "target-hero",
  side: "heroes",
  position_ft: 5,
  state: window.IRON_PIT_BROWSER_STATE.buildState(targetTemplate),
};
target.state.active_effect_ids.push("old-hero-effect");
target.state.resources["old-resource"] = 1;
target.state.initiative_roll = 12;
target.state.initiative_total = 14;
target.state.turn_serial = 3;

const setup = { heroes: [target], monsters: [source] };
const effect = {
  effectId: "cursed",
  replacementMode: "source-template",
  controlMode: "source-side",
  replacementHp: 10,
};

assert.equal(
  window.IRON_PIT_BROWSER_ZERO_HP.applyReplacementEffect(
    target, source, "srd-werewolf-bite", effect, setup,
  ),
  "cursed",
);
assert(target.state.active_effect_ids.includes("cursed"));

const outcome = window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(
  target.state,
  target.state.current_hp,
  false,
  ["piercing"],
  [source.state, target.state],
);

assert.equal(outcome, "zero_hp_replacement");
assert.equal(target.side, "monsters");
assert.equal(target.state.template.id, sourceTemplate.id);
assert.equal(target.state.current_hp, 10);
assert.equal(target.state.initiative_roll, 12);
assert.equal(target.state.initiative_total, 14);
assert.equal(target.state.turn_serial, 3);
assert.equal(target.state.active_effect_ids.includes("old-hero-effect"), false);
assert.equal(target.state.resources["old-resource"], undefined);
assert.equal(setup.heroes.some((member) => member.combatant_id === target.combatant_id), false);
assert.equal(setup.monsters.some((member) => member.combatant_id === target.combatant_id), true);

console.log("Browser zero-HP source-template replacement regression passed.");
