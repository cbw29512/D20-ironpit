"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
global.window = globalThis;

window.IRON_PIT_BROWSER_GRID_GEOMETRY = {
  footprintDistanceFt: (a, _sa, b) => Math.hypot(a.x - b.x, a.y - b.y) * 5,
};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
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
const vision = window.IRON_PIT_BROWSER_CONDITION_RULES;
const obscuration = window.IRON_PIT_BROWSER_OBSCURATION_VISIBILITY;

function member(id, side, x) {
  return {
    combatant_id: id, side,
    state: {
      template: { name: id, size: "medium", truesight_ft: 0, blindsight_ft: 0 },
      position: { x, y: 7 }, is_alive: true, is_dead: false,
      action_available: true, current_hp: 100,
      resources: { darkness: 1 }, concentration: null,
      active_effect_ids: [], active_modifiers: [],
      visible_obscuration_zones: [], timed_effects: [],
      zone_damage_immunities: [],
    },
  };
}

test("2014 source-neutral Darkness casts once, obscures sight, and ends with Concentration", () => {
  const caster = member("caster", "monsters", 1);
  const target = member("target", "heroes", 4);
  caster.state.template.suppression_zone_actions = [{
    id: "darkness", name: "Darkness", level: 2,
    actionCost: "action", castRangeFt: 60, radiusFt: 15,
    durationRounds: 100, resourceId: "darkness", resourceCost: 1,
    concentration: true, obscurationKind: "magical-darkness",
    deafens: false, blocksVerbalSpells: false, thunderImmunity: false,
  }];
  const setup = {
    monsters: [caster], heroes: [target], map_definition: {},
    suppression_zones: [],
  };
  const chosen = zones.choose(caster, setup, "1:caster");
  assert.equal(chosen?.action.id, "darkness");
  const event = zones.cast(1, 1, caster, setup, chosen.action, chosen.center, "1:caster");
  assert.equal(event.feature_id, "darkness");
  assert.match(event.description, /casts Darkness/);
  assert.equal(caster.state.resources.darkness, 0);
  assert.equal(caster.state.concentration.effect_id, "darkness");
  assert.deepEqual(target.state.active_effect_ids, ["magical-darkness"]);
  assert.equal(vision.canSee(caster.state, target.state, 15), false);
  assert.equal(vision.canSee(target.state, caster.state, 15), false);
  const trueSeer = {
    ...caster.state,
    template: { ...caster.state.template, truesight_ft: 60 },
  };
  assert.equal(vision.canSee(trueSeer, target.state, 15), true);
  const blindSeer = {
    ...caster.state,
    template: { ...caster.state.template, blindsight_ft: 60 },
    active_effect_ids: ["blinded"],
  };
  assert.equal(vision.canSee(blindSeer, target.state, 15), true);
  target.state.position = { x: 10, y: 7 };
  zones.sync(setup, 1);
  assert.equal(target.state.active_effect_ids.includes("magical-darkness"), false);
  assert.equal(vision.canSee(caster.state, target.state, 45), false);
  caster.state.concentration = null;
  zones.expire(setup, 2);
  zones.sync(setup, 2);
  assert.equal(setup.suppression_zones.length, 0);
  assert.equal(vision.canSee(caster.state, target.state, 45), true);
  assert.equal(caster.state.visible_obscuration_zones.length, 0);
});

test("physical fog cannot be bypassed by Truesight; a missing position fails closed", () => {
  const observer = member("seer", "heroes", 0).state;
  const target = member("target", "monsters", 8).state;
  observer.template.truesight_ft = 100;
  const fog = {
    zone_id: "fog", position: { x: 4, y: 7 }, radius_ft: 15,
    obscuration_kind: "heavy-physical",
  };
  observer.visible_obscuration_zones = [fog];
  assert.equal(obscuration.blocked(observer, target, { truesightReaches: true }), true);
  assert.equal(vision.canSee(observer, target, 40), false);
  target.position = null;
  assert.equal(obscuration.blocked(observer, target, { truesightReaches: true }), true);
});
