"use strict";

// This checks the exact generated browser card. The underlying modifier,
// temporary size, and concentration engines have independent generic tests.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;

try {
  const source = fs.readFileSync(
    path.join(__dirname, "browser-monsters-2014.js"), "utf8",
  );
  vm.runInThisContext(source, { filename: "browser-monsters-2014.js" });
  const card = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-efreeti"];
  assert.ok(card, "Source-admitted 2014 Efreeti must be in the browser roster");
  assert.equal(card.ruleset, "2014");
  assert.equal(card.size, "large");
  const buff = (card.timed_self_buff_actions || [])
    .find((item) => item.id === "enlarge-reduce");
  assert.ok(buff, "Efreeti must actually cast source Enlarge");
  assert.equal(buff.name, "Enlarge/Reduce");
  assert.equal(buff.actionCost, "action");
  assert.equal(buff.resourceId, "enlarge-reduce");
  assert.equal(buff.resourceCost, 1);
  assert.equal(buff.durationRounds, 10);
  assert.equal(buff.expiryTiming, "source_turn_start");
  assert.equal(buff.concentration, true);
  assert.equal(buff.sizeOverride, "huge");
  assert.deepEqual(buff.abilityCheckAdvantageAbilities, ["strength"]);
  assert.deepEqual(
    buff.savingThrowAdvantageGrants[0].abilities, ["strength"],
  );
  assert.deepEqual(
    buff.modifierEffects.map(({ kind, diceCount, diceSize, damageType,
      requiredWeaponAttackKind }) => ({
      kind, diceCount, diceSize, damageType, requiredWeaponAttackKind,
    })),
    [{
      kind: "bonus-damage", diceCount: 1, diceSize: 4,
      damageType: "slashing", requiredWeaponAttackKind: "melee",
    }],
  );
  assert.equal(card.resources["enlarge-reduce"], 3);
  assert.deepEqual(
    card.attacks.map((a) => [a.name, a.kind]),
    [["Scimitar", "melee"], ["Hurl Flame", "ranged"]],
    "Hurl Flame must not turn into an enlarged melee weapon",
  );
  assert.equal(
    (card.timed_self_buff_actions || []).some((a) => a.id === "major-image"),
    false,
    "Major Image stays on the printed card, not as invented arena buff",
  );
  console.log("2014 Efreeti browser card preserves universal Enlarge combat parameters.");
} catch (error) {
  console.error("2014 Efreeti source-to-browser Enlarge parity failed", error);
  throw error;
}
