"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
require("./browser-test-runtime.cjs").loadWebsite();

function fixture(immune = false) {
  const hero = structuredClone(window.IRON_PIT_BROWSER_HEROES["kael-stillwater-l5"]);
  const foe = structuredClone(window.IRON_PIT_BROWSER_MONSTERS["srd-goblin-warrior"]);
  foe.max_hp = 1000;
  if (immune) foe.damage_immunities = ["bludgeoning"];
  const member = (id, side, template, position) => ({
    combatant_id: id, side, position_ft: position,
    state: window.IRON_PIT_BROWSER_STATE.buildState(template),
  });
  const heroMember = member("hero", "heroes", hero, 0);
  const target = member("foe", "monsters", foe, 5);
  // Fixed dice keep hits and successful saves reproducible without mocking rules.
  window.IRON_PIT_DICE = {
    roll: (sides) => sides === 20 ? 19 : 1,
    rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? 19 : 1),
  };
  return { hero: heroMember, target, setup: { heroes: [heroMember], monsters: [target] } };
}

test("Extra Attack emits its triggering hit before the once-per-turn rider", () => {
  const { hero, setup } = fixture();
  const result = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, hero, setup);
  assert.deepEqual(result.events.map((event) => event.sequence), [1, 2, 3]);
  assert.deepEqual(result.events.map((event) => event.event_type), ["attack", "feature", "attack"]);
  assert.equal(result.events[1].feature_id, "stunning-strike");
  assert.equal(hero.state.resources["focus-points"], 4);
});

test("Opportunity Attack can use the rider on a different creature's turn", () => {
  const { hero, target, setup } = fixture();
  const first = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, hero, setup);
  const event = window.IRON_PIT_BROWSER_REACTIONS.resolveOpportunityAttack(
    first.sequence, 1, hero, target, setup, 5, 10, "speed", { turnKey: "1:foe" },
  );
  assert.ok(event?.hit);
  const result = window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH.chain(
    event.sequence + 1, 1, hero, event, setup, "1:foe",
  );
  assert.deepEqual(result.events.map((item) => item.event_type), ["attack", "feature"]);
  assert.equal(result.events[1].feature_id, "stunning-strike");
  assert.equal(hero.state.resources["focus-points"], 3);
});

test("A zero-damage Opportunity Attack hit still qualifies for its hit rider", () => {
  const { hero, target, setup } = fixture(true);
  const event = window.IRON_PIT_BROWSER_REACTIONS.resolveOpportunityAttack(
    1, 1, hero, target, setup, 5, 10, "speed", { turnKey: "1:foe" },
  );
  assert.ok(event?.hit);
  assert.equal(event.hp_before, event.hp_after);
  const result = window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH.chain(2, 1, hero, event, setup, "1:foe");
  assert.equal(result.events[1]?.feature_id, "stunning-strike");
  assert.equal(hero.state.resources["focus-points"], 4);
});

test("Failed-save incapacitation immediately ends concentration and its allied effects", () => {
  const { hero, target, setup } = fixture();
  const C = window.IRON_PIT_BROWSER_CONCENTRATION;
  C.start(target.state, target.combatant_id, "test-concentration", 1, [hero.state, target.state]);
  window.IRON_PIT_BROWSER_MODIFIERS.add(hero.state, {
    id: "test-effect", source_id: target.combatant_id, source_effect_id: "test-concentration",
    source_name: "Test", kind: "armor-class", flat_bonus: 1, concentration_required: true,
  });
  window.IRON_PIT_DICE.roll = () => 1;
  const result = window.IRON_PIT_BROWSER_RESOURCE_HIT_SAVE.resolve(
    1, 1, hero, target, { id: "kael-2024-unarmed" }, "1:hero", setup,
  );
  assert.equal(result.save_succeeded, false);
  assert.equal(target.state.concentration, null);
  assert.equal(hero.state.active_modifiers.some((item) => item.id === "test-effect"), false);
});

for (const dashes of [0, 1, 2]) {
  test(`Off-turn slow preserves movement spent and adjusts ${dashes} Dash allowances`, () => {
    const { hero, target, setup } = fixture();
    window.IRON_PIT_BROWSER_STATE.beginTurn(target.state);
    // Dash grants are independently covered by tactical-action regressions.
    target.state.dash_uses_this_turn = dashes;
    target.state.movement_remaining_ft = 30 * (1 + dashes) - 10;
    const event = window.IRON_PIT_BROWSER_REACTIONS.resolveOpportunityAttack(
      1, 1, hero, target, setup, 5, 10, "speed", { turnKey: "1:foe" },
    );
    window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH.chain(2, 1, hero, event, setup, "1:foe");
    assert.equal(target.state.movement_remaining_ft, 15 * (1 + dashes) - 10);
    window.IRON_PIT_BROWSER_STATE.beginTurn(target.state);
    assert.equal(target.state.dash_uses_this_turn, 0);
    assert.equal(target.state.movement_remaining_ft, 15);
  });
}

test("Grid movement rechecks the interrupted step after the hit reduces Speed", () => {
  const { hero, target: mover, setup } = fixture();
  const destination = structuredClone(hero);
  destination.combatant_id = "destination";
  destination.state.position = { x: 7, y: 1 };
  destination.state.reaction_available = false;
  hero.state.position = { x: 0, y: 1 };
  mover.state.position = { x: 1, y: 1 };
  mover.state.movement_remaining_ft = 10;
  setup.heroes.push(destination);
  setup.map_definition = { id: "slow-grid", width_squares: 10, height_squares: 3, cell_size_ft: 5 };
  const result = window.IRON_PIT_BROWSER_REACTION_MOVEMENT.moveToward(
    1, 1, mover, destination, setup, 5, "speed", { turnKey: "1:foe" },
  );
  assert.ok(result.events.some((event) => event.feature_id === "stunning-strike"));
  assert.equal(result.movement, null);
  assert.deepEqual(mover.state.position, { x: 1, y: 1 });
  assert.equal(mover.state.movement_remaining_ft, 0);
});
