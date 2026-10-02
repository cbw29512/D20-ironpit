"use strict";

const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const l15 = window.IRON_PIT_BROWSER_HEROES["kael-stillwater-l15"];
const l16 = window.IRON_PIT_BROWSER_HEROES["kael-stillwater-l16"];

assert.ok(l15, "generated 2024 Monk 15 card must exist");
assert.ok(l16, "generated 2024 Monk 16 card must exist");
assert.equal(l15.ability_scores.wisdom, 12);
assert.equal(l16.ability_scores.wisdom, 14);
assert.equal(l16.armor_class, 17);
assert.equal(l16.max_hp, 131);
assert.equal(l16.speed_ft, 55);
assert.equal(l16.initiative_bonus, 10);
assert.equal(l16.resources["focus-points"], 16);

assert.deepEqual(l16.saving_throw_bonuses, {
  strength: 6,
  dexterity: 10,
  constitution: 8,
  intelligence: 5,
  wisdom: 7,
  charisma: 5,
});
assert.equal(l16.skill_bonuses.insight, 7);
assert.equal(l16.skill_bonuses.perception, 7);
assert.equal(l16.resource_backed_on_hit_save_rider.save_dc, 15);
assert.equal(l16.healingActions[0].healingBonus, 2);
assert.equal(l16.attack_damage_reduction_reaction.zeroDamageRedirect.saveDc, 15);

console.log("2024 Monk 16 Wisdom ASI browser parity passed.");
