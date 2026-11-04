"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const stirge2014 = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-stirge"];
assert.ok(stirge2014, "A source-complete attachment card must enter the 2014 roster.");
assert.deepEqual([stirge2014.armor_class, stirge2014.max_hp], [14, 2]);
const bloodDrain2014 = stirge2014.attacks.find(attack => attack.name === "Blood Drain");
assert.ok(bloodDrain2014, "Blood Drain must survive 2014 source compilation.");
assert.deepEqual([bloodDrain2014.kind, bloodDrain2014.bonus, bloodDrain2014.reach,
  bloodDrain2014.diceCount, bloodDrain2014.diceSize, bloodDrain2014.damageBonus,
  bloodDrain2014.damageType], ["melee", 5, 5, 1, 4, 3, "piercing"]);
const attach2014 = bloodDrain2014.onHitAttachment;
assert.deepEqual([attach2014.effect_id, attach2014.source_name, attach2014.periodic_effect_kind,
  attach2014.dice_count, attach2014.dice_size, attach2014.damage_bonus,
  attach2014.tick_timing, attach2014.auto_end_after_hp_loss,
  attach2014.source_detach_movement_ft, attach2014.action_removable,
  attach2014.blocks_source_attacks],
  ["attached-blood-drain", "Blood Drain", "direct_hp_loss", 1, 4, 3,
    "source_turn_start", 10, 5, true, true]);
assert.equal(attach2014.damage_type, null, "2014 blood loss must not become typed damage.");

console.log("Pinned 2014 Stirge browser roster and on-hit capability match immutable source.");
