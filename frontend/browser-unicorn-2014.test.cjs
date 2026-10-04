"use strict";

const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const unicorn = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-unicorn"];
assert.ok(unicorn, "2014 Unicorn must be on the certified website roster");
assert.equal(unicorn.challenge_rating, "5");
assert.equal(unicorn.max_hp, 67);
assert.equal(unicorn.armor_class, 12);
assert.deepEqual(
  (unicorn.legendary_actions || []).map((item) => item.name).sort(),
  ["Heal Self", "Hooves", "Shimmering Shield"],
);
assert.ok(unicorn.attacks.some((item) => item.id === "2014-unicorn-hooves"));
assert.ok(unicorn.attacks.some((item) => item.id === "2014-unicorn-horn" && item.charge));
assert.ok((unicorn.healingActions || []).some((item) => item.id === "healing-touch"));
assert.deepEqual(
  (unicorn.spell_save_actions || []).map((item) => item.id).sort(),
  ["calm-emotions", "entangle"],
);
assert.ok((unicorn.timed_self_buff_actions || []).some((item) => item.id === "dispel-evil-and-good"));
assert.ok((unicorn.condition_removal_actions || []).some((item) => item.id === "break-enchantment"));
assert.equal(unicorn.resources["legendary-actions"], 3);
assert.ok(unicorn.start_turn_resource_refill_ids.includes("legendary-actions"));
assert.ok(!(unicorn.teleport_actions || []).length);
assert.ok(!(unicorn.legendary_actions || []).some((item) => /teleport/i.test(item.name)));
console.log("Certified 2014 Unicorn binds the printed legendary block except pit-banned Teleport.");
