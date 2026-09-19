"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-heroes.js"), "utf8"),
  { filename: "browser-heroes.js" },
);

const heroes = Object.values(window.IRON_PIT_BROWSER_HEROES || {});
let offensiveCount = 0;
for (const hero of heroes) {
  for (const action of hero.spell_attack_actions || []) {
    offensiveCount += 1;
    assert.equal(
      action.actionCost, "action",
      `${hero.id} offensive spell attack ${action.id} must stay in the Main Action timing window`,
    );
  }
  for (const action of hero.spell_save_actions || []) {
    offensiveCount += 1;
    assert.equal(
      action.actionCost, "action",
      `${hero.id} offensive save spell ${action.id} must stay in the Main Action timing window`,
    );
  }
}
assert.ok(offensiveCount > 0, "certified hero artifact should expose offensive spell actions");
console.log("Certified offensive hero spells remain Action-timed for Main Action selection.");
