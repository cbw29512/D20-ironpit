"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-monsters-generated.js"), "utf8"),
  { filename: "browser-monsters-generated.js" },
);

const giant = window.IRON_PIT_BROWSER_MONSTERS["srd-fire-giant"];
assert.ok(giant, "Fire Giant must be present only after canonical certification earns it");
const hammer = giant.attacks.find((attack) => attack.name === "Hammer Throw");
assert.ok(hammer, "Fire Giant must preserve its printed Hammer Throw attack");
assert.deepEqual(hammer.controlEffect?.forcedMovement, {
  direction: "push",
  maxDistanceFt: 15,
  distanceMode: "up_to",
});
assert.deepEqual(hammer.onHitModifiers, [{
  kind: "next-attack-made-disadvantage",
  consumeOnAttackMade: true,
  expiresAtEndOfTargetTurn: true,
}]);
const slotIds = giant.attack_action.slots.map((slot) => slot.attack_ids || slot.attackIds || []);
assert.equal(slotIds.length, 2, "Fire Giant Multiattack must preserve two attack slots");
for (const ids of slotIds) {
  assert.equal(ids.length, 2, "Each Fire Giant Multiattack slot must allow either printed attack");
  assert.ok(ids.some((id) => giant.attacks.find((attack) => attack.id === id)?.name === "Flame Sword"));
  assert.ok(ids.some((id) => giant.attacks.find((attack) => attack.id === id)?.name === "Hammer Throw"));
}
console.log("Generated Fire Giant preserves universal forced-movement and timed attack-modifier parity.");
