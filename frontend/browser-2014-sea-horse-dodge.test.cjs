"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();
require("./browser-catalog.js");
require("./battle-lab.js");
require("./browser-turbo.js");

(async () => {
  const card = IRON_PIT_BROWSER_MONSTERS_2014["2014-sea-horse"];
  assert.ok(card, "2014 Sea Horse must be source-admitted");
  assert.deepEqual(card.attacks, []);
  assert.equal(card.primary_attack_id, null);
  const before = JSON.stringify(card);
  const catalog = await IRON_PIT_BROWSER_CATALOG.buildCatalog("2014");
  const hero = catalog.heroes.find(item => item.coverage_status === "raw_ready" && item.runnable_template_id);
  assert.ok(hero);
  let observedDodge = false;
  for (let seed = 1; seed <= 20 && !observedDodge; seed += 1) {
    const battle = IRON_PIT_BROWSER_TURBO.runSeeded({
      ruleset: "2014",
      hero_ids: [hero.runnable_template_id],
      monster_ids: ["2014-sea-horse"],
    }, seed).battle;
    observedDodge = battle.events.some(event =>
      event.actor_name === "Sea Horse" && event.feature_id === "dodge");
    assert.equal(battle.events.some(event =>
      event.actor_name === "Sea Horse" && event.event_type === "attack"), false);
  }
  assert.equal(observedDodge, true, "Sea Horse should reach the shared Dodge fallback");
  assert.equal(JSON.stringify(card), before, "browser fight state must not mutate the card");
  console.log("2014 Sea Horse browser Dodge integration passed.");
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
