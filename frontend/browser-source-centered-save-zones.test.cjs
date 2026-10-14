"use strict";

// Regression for universal source-centered zones: never infer placement from the printed name.
const assert = require("node:assert/strict");
const test = require("node:test");

let actionsSpent = 0;
global.window = {
  IRON_PIT_ACTION_ECONOMY: {
    available: () => true,
    spend: () => { actionsSpent += 1; },
  },
  IRON_PIT_BROWSER_GRID_GEOMETRY: {
    footprintDistanceFt: (a, _aSize, b) => Math.hypot(a.x - b.x, a.y - b.y) * 5,
  },
  IRON_PIT_BROWSER_STATE: {
    distance: (a, b) => Math.hypot(a.state.position.x - b.state.position.x,
      a.state.position.y - b.state.position.y) * 5,
  },
  IRON_PIT_BROWSER_SPELLCASTING: { slotSpellAvailable: () => true },
  IRON_PIT_BROWSER_SUPPRESSION_ZONES: { verbalBlocked: () => false },
  IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES: { resolveDamage: () => ({}) },
  IRON_PIT_BROWSER_MAIN_ACTION_SELECTION: {
    CATEGORIES: { SAVE_ZONE: "save-zone" },
    registerProvider: () => {},
  },
};
require("./browser-save-zones.js");
require("./browser-save-zone-provider.js");

function scenario(action) {
  const caster = {
    combatant_id: "caster", side: "heroes",
    state: {
      position: { x: 1, y: 7 }, resources: { cloud: 1 },
      template: { name: "Source", persistent_save_zone_actions: [action] },
    },
  };
  const enemy = {
    combatant_id: "target", side: "monsters",
    state: { position: { x: 3, y: 7 }, is_alive: true, is_dead: false, template: { size: "medium" } },
  };
  return { caster, enemy, setup: { heroes: [caster], monsters: [enemy], map_definition: {}, save_zones: [] } };
}

test("nondamaging save-zone placement is source-centered only when explicitly configured", () => {
  const action = { id: "cloud", name: "Any Source Cloud", actionCost: "action",
    castRangeFt: 30, radiusFt: 10, resourceId: "cloud", resourceCost: 1 };
  const { caster, setup, enemy } = scenario({ ...action, centerOnSource: true });
  const sourceChoice = window.IRON_PIT_BROWSER_SAVE_ZONES.choose(caster, setup, "1:caster");
  assert.deepEqual(sourceChoice.center, caster.state.position);
  caster.state.template.persistent_save_zone_actions = [{ ...action }];
  const targetChoice = window.IRON_PIT_BROWSER_SAVE_ZONES.choose(caster, setup, "1:caster");
  assert.deepEqual(targetChoice.center, enemy.state.position);
});

test("damaging save-zone provider respects explicit source-centered geometry", () => {
  const action = { id: "damage-cloud", name: "Any Damage Cloud", actionCost: "action",
    damageDiceCount: 2, damageDiceSize: 6, radiusFt: 10, resourceId: "cloud", resourceCost: 1,
    centerOnSource: true };
  const { caster, setup } = scenario(action);
  // Enemy is 10 feet away: inside a 10-foot source-centered zone.
  const selected = window.IRON_PIT_BROWSER_SAVE_ZONE_PROVIDER.chooseDamaging(caster, setup, "1:caster");
  assert.deepEqual(selected.center, caster.state.position);
  assert.equal(selected.score, 7);
  caster.state.template.persistent_save_zone_actions = [{ ...action, radiusFt: 5 }];
  assert.equal(window.IRON_PIT_BROWSER_SAVE_ZONE_PROVIDER.chooseDamaging(caster, setup, "1:caster"), null);
});

test("illegal off-source placement fails before spending action or limited resource", () => {
  const action = { id: "cloud", name: "Any Source Cloud", actionCost: "action",
    castRangeFt: 0, radiusFt: 10, durationRounds: 10, resourceId: "cloud",
    resourceCost: 1, centerOnSource: true };
  const { caster, enemy, setup } = scenario(action);
  const before = actionsSpent;
  assert.throws(
    () => window.IRON_PIT_BROWSER_SAVE_ZONES.cast(
      1, 1, caster, setup, action, enemy.state.position, "1:caster"),
    /centered on its source/,
  );
  assert.equal(actionsSpent, before);
  assert.equal(caster.state.resources.cloud, 1);
  assert.deepEqual(setup.save_zones, []);
});
