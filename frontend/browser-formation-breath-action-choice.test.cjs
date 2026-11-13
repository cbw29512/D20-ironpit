"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const monsters = window.IRON_PIT_BROWSER_MONSTERS;
  const state = window.IRON_PIT_BROWSER_STATE;
  const saves = window.IRON_PIT_BROWSER_AREA_SAVES;
  const action = window.IRON_PIT_BROWSER_MULTIATTACK;
  const make = (id, side, row, template) => {
    const current = state.buildState(structuredClone(template));
    current.formation_row = row;
    current.initial_formation_row = row;
    return {combatant_id: id, side, position_ft: 400,
      state: current};
  };
  const foe = monsters["srd-owlbear"];
  assert.ok(foe, "Need a certified 2024 unarmored target.");
  for (const [id, shape, name] of [
    ["srd-hell-hound", "cone", "Fire Breath"],
    ["srd-blue-dragon-wyrmling", "line", "Lightning Breath"],
  ]) {
    const template = monsters[id];
    assert.ok(template, `Missing certified 2024 ${id}`);
    const actor = make("source", "monsters", "front", template);
    const heroes = [0, 1, 2].map(i => make(`hero-${i}`, "heroes", "front", foe));
    const setup = {arena_mode: "formation", heroes, monsters: [actor]};
    const source = template.saving_throw_actions.find(s => s.area?.shape === shape);
    assert.ok(source, `${name} missing from source card`);
    assert.ok(actor.state.resources[source.resourceId] > 0);
    const selected = saves.choose(actor, setup, "action");
    const weaponDamage = action.expectedDamage(actor, setup);
    assert.ok(selected, `${name} never entered the universal Action chooser`);
    const count = selected.placement.targetIds.length;
    assert.equal(count, shape === "cone" ? 3 : 1);
    const breathDamage = saves.expectedSaveDamage(selected.action) * count;
    // Log the factual tactical comparison, never create a fake Breath event.
    console.log(`${name} eligible: targets=${count}, printed=${breathDamage}, multiattack=${weaponDamage}`);
    assert.equal(selected.action.id, source.id);
  }
  console.log("2024 source Breath action eligibility passed.");
} catch (error) {
  console.error("2024 source Breath choice regression failed.", error);
  throw error;
}
