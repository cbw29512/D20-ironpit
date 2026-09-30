"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

let dice = [];
window.IRON_PIT_BROWSER_ROLLS = {
  modeFromSources: (advantage, disadvantage) => {
    if (Boolean(advantage) === Boolean(disadvantage)) return "normal";
    return advantage ? "advantage" : "disadvantage";
  },
  d20: (modifier, mode) => {
    const count = mode === "normal" ? 1 : 2;
    const rolls = dice.splice(0, count);
    const selected = mode === "advantage" ? Math.max(...rolls)
      : mode === "disadvantage" ? Math.min(...rolls) : rolls[0];
    return {
      notation: count === 2 ? "2d20" : "1d20",
      rolls, modifier, total: selected + modifier, selected_roll: selected, mode,
    };
  },
};
window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false };
window.IRON_PIT_BROWSER_EXHAUSTION = {
  abilityCheckDisadvantage: () => 0,
  d20Modifier: () => 0,
};
window.IRON_PIT_DICE = { roll: () => dice.shift() };

load("browser-modifiers.js");
load("browser-ability-checks.js");
load("browser-defensive-modifier-rules.js");
load("browser-initiative.js");
load("browser-turn.js");

const foresight = {
  id: "hero:foresight:d20",
  source_id: "hero",
  source_effect_id: "foresight",
  source_name: "Foresight",
  kind: "d20-test-advantage",
};
const template = (id, kind = "character") => ({
  id, name: id, kind, initiative_bonus: 0, initiative_advantage: false,
  first_round_extra_turn_grants: [], first_round_extra_turn_initiative_offset: null,
  death_save_advantage: false, death_save_recovery_minimum: 20,
});
const state = (id, kind = "character") => ({
  template: template(id, kind),
  active_modifiers: [], active_effect_ids: [], exhaustion_level: 0,
  current_hp: 10, is_alive: true, is_dead: false, is_unconscious: false, is_stable: false,
  death_save_successes: 0, death_save_failures: 0,
});

{
  const hero = { combatant_id: "hero", side: "heroes", state: state("hero") };
  const monster = { combatant_id: "monster", side: "monsters", state: state("monster", "monster") };
  hero.state.active_modifiers.push({ ...foresight });
  dice = [3, 18, 10];
  const result = window.IRON_PIT_BROWSER_INITIATIVE.resolve({ heroes: [hero], monsters: [monster] });
  const heroGroup = result.groups.find((group) => group.side === "heroes");
  assert.equal(heroGroup.initiative_roll.mode, "advantage");
  assert.deepEqual(heroGroup.initiative_roll.rolls, [3, 18]);
  assert.equal(heroGroup.initiative_roll.selected_roll, 18);
}

{
  const hero = { combatant_id: "hero", side: "heroes", state: state("hero") };
  hero.state.current_hp = 0;
  hero.state.is_unconscious = true;
  hero.state.active_modifiers.push({ ...foresight });
  dice = [4, 14];
  const event = window.IRON_PIT_BROWSER_TURN.deathSave(1, 1, hero);
  assert.equal(event.death_save_roll.mode, "advantage");
  assert.deepEqual(event.death_save_roll.rolls, [4, 14]);
  assert.equal(event.death_save_roll.selected_roll, 14);
}

assert.equal(
  window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS.saveAdvantageSourceNames(
    { active_modifiers: [{ ...foresight }] }, "wisdom", {},
  )[0],
  "Foresight",
);

console.log("Browser universal D20-test Advantage regressions passed.");
