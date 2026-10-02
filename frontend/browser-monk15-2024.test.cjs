"use strict";

const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const hero = structuredClone(window.IRON_PIT_BROWSER_HEROES["kael-stillwater-l15"]);
assert.ok(hero, "generated 2024 Monk 15 card must exist");
assert.equal(hero.level, 15);
assert.equal(hero.max_hp, 123);
assert.equal(hero.speed_ft, 55);
assert.equal(hero.resources["focus-points"], 15);

const grants = hero.initiative_resource_refill_grants;
assert.equal(grants.length, 2);
assert.equal(grants[0].source_id, "uncanny-metabolism");
assert.equal(grants[1].source_id, "perfect-focus");
assert.equal(grants[1].source_name, "Perfect Focus");
assert.equal(grants[1].resource_id, "focus-points");
assert.equal(grants[1].when_at_or_below, 3);
assert.equal(grants[1].restore_to_minimum, 4);

function member() {
  const template = structuredClone(hero);
  return {
    combatant_id: "kael-15",
    side: "heroes",
    position_ft: 0,
    state: window.IRON_PIT_BROWSER_STATE.buildState(template),
  };
}

const target = {
  combatant_id: "target",
  side: "monsters",
  position_ft: 5,
  state: {
    template: { name: "Target", resources: {}, initiative_resource_refill_grants: [] },
    resources: {},
  },
};

{
  const actor = member();
  actor.state.resources["focus-points"] = 2;
  actor.state.resources["uncanny-metabolism"] = 0;
  const result = window.IRON_PIT_BROWSER_INITIATIVE_RESOURCE_REFILL.resolve(
    1, { heroes: [actor], monsters: [target] },
  );
  assert.deepEqual(result.events.map((event) => event.feature_id), ["perfect-focus"]);
  assert.equal(actor.state.resources["focus-points"], 4);
}

{
  const actor = member();
  actor.state.resources["focus-points"] = 2;
  actor.state.resources["uncanny-metabolism"] = 1;
  actor.state.current_hp -= 10;
  window.IRON_PIT_DICE = { roll: () => 5 };
  const result = window.IRON_PIT_BROWSER_INITIATIVE_RESOURCE_REFILL.resolve(
    1, { heroes: [actor], monsters: [target] },
  );
  assert.deepEqual(result.events.map((event) => event.feature_id), ["uncanny-metabolism"]);
  assert.equal(actor.state.resources["focus-points"], 15);
  assert.equal(actor.state.resources["uncanny-metabolism"], 0);
}

console.log("2024 Monk 15 Perfect Focus browser parity passed.");
