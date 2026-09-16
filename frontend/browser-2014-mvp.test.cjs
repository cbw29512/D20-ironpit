"use strict";

const assert = require("node:assert/strict");

const deterministicDice = (seed = 2014) => {
  let state = seed >>> 0;
  const roll = (sides) => {
    state = (1664525 * state + 1013904223) >>> 0;
    return (state % sides) + 1;
  };
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
};

assert.equal(window.IRON_PIT_2014_MVP_READY, true, "2014 browser test roster must be loaded");
assert.equal(Object.keys(window.IRON_PIT_BROWSER_MONSTERS_2014).length, 32);

window.IRON_PIT_DICE = deterministicDice();
const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
  ruleset: "2014",
  hero_ids: ["2014-brown-bear", "2014-bandit"],
  monster_ids: ["2014-skeleton", "2014-goblin"],
});

assert.equal(battle.ruleset, "2014");
assert.notEqual(battle.outcome, "active");
assert.ok(battle.events.some((event) => event.event_type === "attack"));
for (const member of [...battle.setup.heroes, ...battle.setup.monsters]) {
  assert.equal(member.state.template.ruleset, "2014", `${member.combatant_id} crossed ruleset boundary`);
}
assert.throws(
  () => window.IRON_PIT_BROWSER_ENGINE.runEncounter({
    ruleset: "2014",
    hero_ids: ["2014-bandit"],
    monster_ids: ["srd-wolf"],
  }),
  /Unknown certified Team B combatant for 2014/,
);

console.log("Expanded certified 2014 browser fight lane passed.");
