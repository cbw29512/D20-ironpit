"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-engine.js"), "utf8"),
  { filename: "browser-engine.js" },
);

try {
  const reactive = {
    state: {
      reaction_available: false,
      template: { reaction_refresh_each_turn: true },
    },
  };
  const ordinary = {
    state: {
      reaction_available: false,
      template: { reaction_refresh_each_turn: false },
    },
  };

  window.IRON_PIT_BROWSER_ENGINE.refreshPerTurnReactions([reactive, ordinary]);

  assert.equal(reactive.state.reaction_available, true);
  assert.equal(ordinary.state.reaction_available, false);
  console.log("Browser per-turn Reaction refresh regression passed.");
} catch (error) {
  console.error("Browser per-turn Reaction refresh regression failed.", { error });
  throw error;
}
