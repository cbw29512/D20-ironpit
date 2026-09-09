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
  expiresAtEndOfTargetTurn: true,
}]);
assert.deepEqual(
  giant.attack_action.slots.map((slot) => slot.attack_ids || slot.attackIds),
  [
    giant.attack_action.slots[0].attack_ids || giant.attack_action.slots[0].attackIds,
    giant.attack_action.slots[1].attack_ids || giant.attack_action.slots[1].attackIds,
  ],
  "Fire Giant Multiattack must remain a two-slot universal combination action",
);
console.log("Generated Fire Giant preserves universal forced-movement and timed attack-modifier parity.");
