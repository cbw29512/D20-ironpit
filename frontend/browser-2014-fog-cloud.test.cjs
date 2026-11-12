"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
global.window = globalThis;

window.IRON_PIT_BROWSER_GRID_GEOMETRY = {
  footprintDistanceFt: (a, _sizeA, b) => Math.hypot(a.x - b.x, a.y - b.y) * 5,
};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, kind) => kind === "action" && state.action_available,
  spend: (state) => { state.action_available = false; },
};
window.IRON_PIT_BROWSER_CONCENTRATION = {
  start: (state, sourceId, effectId) => {
    state.concentration = { source_id: sourceId, effect_id: effectId };
  },
};
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.hypot(
    a.state.position.x - b.state.position.x,
    a.state.position.y - b.state.position.y,
  ) * 5,
};
require("./browser-obscuration-visibility.js");
require("./browser-condition-rules.js");
require("./browser-suppression-zones.js");
const zones = window.IRON_PIT_BROWSER_SUPPRESSION_ZONES;
const canSee = window.IRON_PIT_BROWSER_CONDITION_RULES.canSee;

function combatant(id, side, x) {
  return {
    combatant_id: id, side,
    state: {
      template: { name: id, size: "medium", truesight_ft: 0, blindsight_ft: 0 },
      position: { x, y: 7 }, is_alive: true, is_dead: false,
      action_available: true, current_hp: 100,
      resources: { "fog-cloud": 1 }, concentration: null,
      active_effect_ids: [], active_modifiers: [],
      visible_obscuration_zones: [], timed_effects: [], zone_damage_immunities: [],
    },
  };
}
const fog = {
  id: "fog-cloud", name: "Fog Cloud", level: 1, actionCost: "action",
  castRangeFt: 120, radiusFt: 20, durationRounds: 600,
  concentration: true, deafens: false, thunderImmunity: false,
  blocksVerbalSpells: false, obscurationKind: "heavy-physical",
  resourceId: "fog-cloud", resourceCost: 1,
};
test("2014 Fog Cloud skips mutual concealment but casts against sight-required Actions", () => {
  const caster = combatant("fog-caster", "monsters", 1);
  const target = combatant("target", "heroes", 4);
  caster.state.template.suppression_zone_actions = [fog];
  const setup = { monsters: [caster], heroes: [target], map_definition: {}, suppression_zones: [] };
  assert.equal(zones.choose(caster, setup, "1:caster"), null);
  target.state.template.spell_save_actions = [
    { id: "sight-save", requiresTargetSight: true, range: 60 },
  ];
  const selected = zones.choose(caster, setup, "1:caster");
  assert.equal(selected?.action.id, "fog-cloud");
  const event = zones.cast(1, 1, caster, setup, selected.action, selected.center, "1:caster");
  assert.equal(event.feature_id, "fog-cloud");
  assert.match(event.description, /casts Fog Cloud/);
  assert.equal(caster.state.resources["fog-cloud"], 0);
  assert.equal(caster.state.concentration.effect_id, "fog-cloud");
  assert.equal(target.state.active_effect_ids.includes("blinded"), false);
  assert.equal(target.state.active_effect_ids.includes("magical-darkness"), false);
  assert.equal(canSee(caster.state, target.state, 15), false);
  assert.equal(canSee(target.state, caster.state, 15), false);
  const seer = { ...caster.state, template: {
    ...caster.state.template, truesight_ft: 120, magical_darkness_sight_ft: 120,
  } };
  assert.equal(canSee(seer, target.state, 15), false);
  const blindsighted = { ...caster.state, template: {
    ...caster.state.template, blindsight_ft: 120,
  } };
  assert.equal(canSee(blindsighted, target.state, 15), true);
  caster.state.concentration = null;
  zones.expire(setup, 2);
  zones.sync(setup, 2);
  assert.equal(setup.suppression_zones.length, 0);
  assert.equal(canSee(caster.state, target.state, 15), true);
});
test("At-will innate Fog Cloud has no daily resource", () => {
  const caster = combatant("giant", "monsters", 1);
  const enemy = combatant("enemy", "heroes", 4);
  caster.state.template.suppression_zone_actions = [{ ...fog, resourceId: null }];
  enemy.state.template.spell_save_actions = [
    { requiresTargetSight: true, range: 60 },
  ];
  const setup = { monsters: [caster], heroes: [enemy], map_definition: {}, suppression_zones: [] };
  const chosen = zones.choose(caster, setup, "1:caster");
  assert.equal(chosen?.action.resourceId, null);
  zones.cast(1, 1, caster, setup, chosen.action, chosen.center, "1:caster");
  assert.equal(caster.state.resources["fog-cloud"], 1);
});
