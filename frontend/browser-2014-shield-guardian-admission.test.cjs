"use strict";

const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();
require("./browser-catalog.js");
require("./battle-lab.js");
require("./browser-turbo.js");

try {
  const guardian = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-shield-guardian"];
  assert.ok(guardian, "A complete source-proven Shield Guardian must enter the 2014 roster.");
  assert.ok(guardian.armor_class > 0 && guardian.max_hp > 0);
  assert.ok(guardian.source_trait_names.includes("Bound"));
  assert.ok(guardian.source_trait_names.includes("Spell Storing"));
  assert.ok(guardian.regeneration, "Printed Regeneration must retain shared combat execution.");
  const fist = guardian.attacks.find(attack => attack.name === "Fist");
  assert.ok(fist, "Printed Fist must remain a usable melee weapon attack.");
  assert.equal(fist.kind, "melee");
  assert.ok(fist.bonus > 0 && fist.diceCount > 0 && fist.diceSize > 1);
  const hero = Object.values(window.IRON_PIT_BROWSER_HEROES).find(
    item => item.ruleset === "2014" && item.class_id === "fighter" && item.level === 5
  );
  assert.ok(hero, "Certified 2014 fighter fixture is required.");
  for (const count of [1, 3]) {
    const selection = {
      ruleset: "2014",
      hero_ids: Array(count).fill(hero.id),
      monster_ids: Array(count).fill("2014-shield-guardian"),
    };
    const seed = 20261106 + count, original = JSON.stringify(guardian);
    const first = window.IRON_PIT_BROWSER_TURBO.runSeeded(selection, seed).battle;
    const repeated = window.IRON_PIT_BROWSER_TURBO.runSeeded(selection, seed).battle;
    assert.deepEqual(repeated.events, first.events, `${count}v${count} must replay identically`);
    assert.equal(repeated.outcome, first.outcome);
    assert.equal(first.setup.monsters.length, count);
    assert.ok(first.events.some(e => e.event_type === "attack"),
      "Universal attacks must actually resolve in the browser fight.");
    assert.equal(JSON.stringify(guardian), original, "Fight state cannot mutate printed source.");
  }
  console.log("2014 Shield Guardian source-admitted browser Fist/regeneration fights passed.");
} catch (error) {
  console.error("2014 Shield Guardian browser combat regression failed", error);
  process.exitCode = 1;
}
