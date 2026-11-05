"use strict";

const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();
require("./browser-catalog.js");
require("./battle-lab.js");
require("./browser-turbo.js");

const doppelganger = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-doppelganger"];
assert.ok(doppelganger, "A source-complete Doppelganger must enter the 2014 browser roster.");
assert.deepEqual(
  [doppelganger.armor_class, doppelganger.max_hp, doppelganger.initiative_bonus],
  [14, 52, 4],
);
assert.deepEqual(doppelganger.source_trait_names, ["Shapechanger", "Ambusher", "Surprise Attack"]);
assert.deepEqual(doppelganger.condition_immunities, ["charmed"]);
assert.deepEqual(doppelganger.attack_action.slots.map((slot) => slot.attackIds), [
  ["2014-doppelganger-slam"],
  ["2014-doppelganger-slam"],
]);

const slam = doppelganger.attacks.find((attack) => attack.name === "Slam");
assert.ok(slam, "The printed Slam must survive 2014 source compilation.");
assert.deepEqual(
  [slam.kind, slam.bonus, slam.reach, slam.diceCount, slam.diceSize, slam.damageBonus, slam.damageType],
  ["melee", 6, 5, 1, 6, 4, "bludgeoning"],
);
assert.deepEqual(slam.conditionalAttackAdvantage, [{ trigger: "round1_initiative_lead" }]);
assert.deepEqual(slam.conditionalDamage, {
  trigger: "round1_initiative_lead",
  mode: "add",
  diceCount: 3,
  diceSize: 6,
  damageBonus: 0,
  damageType: "bludgeoning",
  sourceName: "Surprise Attack",
});

const hero = Object.values(window.IRON_PIT_BROWSER_HEROES)
  .find((item) => item.ruleset === "2014" && item.class_id === "fighter" && item.level === 5);
assert.ok(hero);
for (const count of [1, 6]) {
  const selection = {
    ruleset: "2014",
    hero_ids: Array(count).fill(hero.id),
    monster_ids: Array(count).fill("2014-doppelganger"),
  };
  const seed = 20261105 + count;
  const before = JSON.stringify(doppelganger);
  const first = window.IRON_PIT_BROWSER_TURBO.runSeeded(selection, seed).battle;
  const replay = window.IRON_PIT_BROWSER_TURBO.runSeeded(selection, seed).battle;
  assert.deepEqual(replay.events, first.events, `${count}v${count} Doppelganger fight must replay deterministically.`);
  assert.equal(replay.outcome, first.outcome);
  assert.equal(first.setup.monsters.length, count);
  assert.equal(JSON.stringify(doppelganger), before, "A fight must not mutate the immutable source card.");
}

console.log("Pinned 2014 Doppelganger browser admission and deterministic 1v1/6v6 fights pass.");
