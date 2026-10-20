"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION = {
  CATEGORIES: () => ({}), registerProvider: () => {},
};
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-main-action-providers.js"), "utf8"));
const impact = window.IRON_PIT_BROWSER_MAIN_ACTION_PROVIDERS.printedSave;
assert.equal(impact({ id: "any-source", failureSetsZeroHp: true }, { state: { current_hp: 52 } }), 52);
assert.equal(impact({ id: "other-name", failureSetsZeroHp: true }, { state: { current_hp: 3 } }), 3);
assert.equal(impact({ id: "legacy", damageDiceCount: 2, damageDiceSize: 6 }, { state: { current_hp: 52 } }), 7);
assert.throws(() => impact({ id: "bad", failureSetsZeroHp: true }, { state: { current_hp: -1 } }));
console.log("Browser zero-HP save Action scoring remains source-neutral.");
