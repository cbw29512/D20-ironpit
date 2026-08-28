"use strict";

const assert = require("node:assert/strict");

global.window = globalThis;
let firstD20 = null;
global.IRON_PIT_DICE = {
  roll(sides) {
    if (sides === 20 && firstD20 !== null) {
      const value = firstD20;
      firstD20 = null;
      return value;
    }
    return sides === 20 ? 15 : sides === 6 ? 4 : Math.max(1, Math.floor(sides / 2));
  },
  rollMany(count, sides) { return Array.from({ length: count }, () => this.roll(sides)); },
};

require("../frontend/preview-data.js");
const { buildRogueAmbush } = require("../frontend/preview-rogue.js");

const successful = buildRogueAmbush();
assert.deepEqual(successful.events.slice(0, 3).map((event) => event.event_type), ["hide", "initiative", "initiative"]);
const successfulRogueInit = successful.events.find((event) => event.event_type === "initiative" && event.actor_id === "mara-vale-l1");
const successfulGoblinInit = successful.events.find((event) => event.event_type === "initiative" && event.actor_id === "srd-goblin-warrior");
const successfulAttack = successful.events.find((event) => event.event_type === "attack" && event.actor_id === "mara-vale-l1");
assert.equal(successfulRogueInit.attack_roll.mode, "advantage");
assert.equal(successfulGoblinInit.attack_roll.mode, "disadvantage");
assert.equal(successfulAttack.attack_roll.mode, "advantage");
assert.equal(successfulAttack.damage_roll.total, 11);
assert.ok(successfulAttack.damage_components.some((component) => component.source === "Sneak Attack"));
assert.equal(successful.winner_name, "Mara Vale");

firstD20 = 3;
const failed = buildRogueAmbush();
const failedGoblinInit = failed.events.find((event) => event.event_type === "initiative" && event.actor_id === "srd-goblin-warrior");
const failedFirstAttack = failed.events.find((event) => event.event_type === "attack" && event.actor_id === "mara-vale-l1");
assert.equal(failed.events[0].event_type, "hide");
assert.match(failed.events[0].description, /fails to hide/);
assert.equal(failedGoblinInit.attack_roll.mode, "normal");
assert.equal(failedFirstAttack.attack_roll.mode, "normal");
assert.ok(!failedFirstAttack.damage_components.some((component) => component.source === "Sneak Attack"));

console.log("Rogue ambush secure-preview behavior is valid.");
