"use strict";

// Browser source parity: gear-only corrosion does not change an encounter.
// Preserve the normal typed attack and all other printed combat effects.
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const roster = window.IRON_PIT_BROWSER_MONSTERS_2014;
  const gray = roster["2014-gray-ooze"];
  const black = roster["2014-black-pudding"];
  const rust = roster["2014-rust-monster"];
  assert.ok(gray && black && rust, "All corrosion-family sources stay selectable");

  const pseudopod = gray.attacks.find((a) => a.id === "2014-gray-ooze-pseudopod");
  assert.ok(pseudopod);
  assert.deepEqual(
    [pseudopod.kind, pseudopod.bonus, pseudopod.reach,
      pseudopod.diceCount, pseudopod.diceSize, pseudopod.damageBonus, pseudopod.damageType],
    ["melee", 3, 5, 1, 6, 1, "bludgeoning"],
  );
  assert.deepEqual(
    (pseudopod.onHitDamage || []).map((part) =>
      [part.diceCount, part.diceSize, part.damageBonus, part.damageType]),
    [[2, 6, 0, "acid"]],
  );
  assert.equal(pseudopod.onHitModifiers, undefined, "No armor corrosion modifier");
  assert.deepEqual(rust.attacks.map((attack) => attack.name), ["Bite"]);
  assert.ok(black.attacks.some((attack) => attack.id === "2014-black-pudding-pseudopod"));

  for (const monsterId of ["2014-gray-ooze", "2014-black-pudding", "2014-rust-monster"]) {
    let value = 98765;
    window.IRON_PIT_DICE = {
      roll: (sides) => {
        value = (1664525 * value + 1013904223) >>> 0;
        return (value % sides) + 1;
      },
      rollMany: (n, sides) => Array.from({length: n}, () => window.IRON_PIT_DICE.roll(sides)),
    };
    const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
      ruleset: "2014", hero_ids: ["karnok-stoneward-2014-l5"], monster_ids: [monsterId],
    });
    assert.notEqual(battle.outcome, "active");
    assert.ok(battle.events.some((event) => event.event_type === "attack"));
    for (const member of [...battle.setup.heroes, ...battle.setup.monsters]) {
      const state = member.state;
      assert.deepEqual(state.weapon_corrosion_penalties || {}, {});
      assert.deepEqual(state.armor_corrosion_penalties || {}, {});
      assert.deepEqual(state.destroyed_armor_ids || [], []);
    }
  }
  console.log("2014 equipment-destruction exclusion and ordinary browser fights passed");
} catch (error) {
  console.error("2014 equipment-corrosion browser parity failed:", error);
  process.exitCode = 1;
}
