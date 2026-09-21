"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_ACTION_ECONOMY = { available: () => true, spend: () => {} };
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_SAVES = {};
window.IRON_PIT_BROWSER_TIMED = {
  removeGroup(state, effect) {
    state.timed_effects = state.timed_effects.filter((item) => item !== effect);
    state.active_effect_ids = state.active_effect_ids.filter((id) => id !== "frightened");
    return ["frightened"];
  },
};
window.IRON_PIT_BROWSER_STATE = {
  buildState(template) {
    return {
      template,
      current_hp: template.test_zero_hp ? 0 : template.max_hp,
      is_alive: true,
      is_dead: false,
      is_stable: false,
      is_unconscious: Boolean(template.test_zero_hp),
      death_save_successes: 0,
      death_save_failures: 0,
      active_effect_ids: template.test_frightened ? ["frightened"] : [],
      timed_effects: template.test_frightened ? [{
        effect_id: "frightened",
        source_id: "monster-1:source",
        source_effect_id: "intimidating-presence-2014",
      }] : [],
      feature_last_turn_keys: {},
    };
  },
  refreshStartOfTurn() {},
  distance(left, right) { return Math.abs((left.position_ft || 0) - (right.position_ft || 0)); },
};
window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE = {
  resolveTargetTiming: (sequence) => ({ events: [], sequence }),
  resolveSourceTiming: (sequence) => ({ events: [], sequence }),
};
window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS = { prepare: () => ({ events: [], sequence: 1 }) };
window.IRON_PIT_BROWSER_CONCENTRATION = { endIfExpired: () => {} };
window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS = { cleanupDisabledSources: () => {} };
window.IRON_PIT_BROWSER_MODIFIERS = {
  expireSourceTurnStart: () => {},
  expireSourceTurn: () => {},
};
window.IRON_PIT_BROWSER_FORMATION = {
  startingPosition: (template) => template.test_position_ft || 0,
};
window.IRON_PIT_BROWSER_ARENA_MAP = {
  buildStandardMap: () => ({}),
  buildHeroDeploymentZone: () => ({}),
  buildMonsterDeploymentZone: () => ({}),
};
window.IRON_PIT_BROWSER_GRID_PLACEMENT = {
  packZone: (_map, _zone, members) => members.map((member) => member.position_ft),
  apply: () => {},
};
window.IRON_PIT_BROWSER_INITIATIVE = {
  resolve: () => ({ turn_order: ["hero-1:target", "monster-1:source"] }),
  events: () => [],
  turnOrderForRound: (_round, initiative) => [...initiative.turn_order],
};
window.IRON_PIT_BROWSER_TURN = {
  deathSave(sequence, round, member) {
    member.state.is_dead = true;
    member.state.is_alive = false;
    member.state.is_unconscious = false;
    return {
      sequence, round_number: round, event_type: "death_save",
      actor_id: member.combatant_id, actor_name: member.state.template.name,
      is_dead: true, description: "Test death save.",
    };
  },
  resolveTurn() { throw new Error("0-HP target must not enter normal turn resolution."); },
};

window.IRON_PIT_2014_MVP_READY = true;
window.IRON_PIT_BROWSER_HEROES = {
  target: {
    id: "target", name: "Target", ruleset: "2014", kind: "character",
    max_hp: 20, test_zero_hp: true, test_frightened: true, test_position_ft: 0,
  },
};
window.IRON_PIT_BROWSER_MONSTERS_2014 = {
  source: {
    id: "source", name: "Source", ruleset: "2014", kind: "monster",
    max_hp: 20, challenge_rating: "1", test_position_ft: 100,
  },
};

load("browser-ability-hooks.js");
load("browser-intimidating-presence-2014.js");
load("browser-engine.js");

const H = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
assert.deepEqual(
  H.abilitiesFor(H.PHASES.TURN_END_LIFECYCLE).map((item) => item.id),
  ["intimidating-presence-2014"],
);

const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
  ruleset: "2014", hero_ids: ["target"], monster_ids: ["source"],
});
const target = battle.setup.heroes[0];
assert.equal(target.state.timed_effects.length, 0);
assert.equal(target.state.active_effect_ids.includes("frightened"), false);
assert.ok(
  battle.events.some((event) =>
    event.feature_id === "intimidating-presence-2014"
    && event.description === "Intimidating Presence ends on Target."
  ),
  "end-turn lifecycle must clean invalid Intimidating Presence even when the target never gets a normal turn",
);

console.log("Browser turn-end lifecycle hooks preserve 0-HP Intimidating Presence cleanup parity.");
