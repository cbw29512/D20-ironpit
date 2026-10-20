"use strict";

// Production ordering contract: source saves happen after start-of-turn
// condition expiry. A prior-turn poison must not erase a new zone application.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

test("browser start-of-turn save zone follows condition lifecycle", () => {
  try {
    const engine = fs.readFileSync(path.join(__dirname, "browser-engine.js"), "utf8");
    const lifecycle = engine.indexOf(
      'const start = lifecycle(sequence, round, member, setup, "target_turn_start", "source_turn_start")',
    );
    const damage = engine.indexOf("const saveDot = window.IRON_PIT_BROWSER_POST_HIT_SAVE_CONDITION");
    const zone = engine.indexOf("const startZones = window.IRON_PIT_BROWSER_SAVE_ZONES?.resolveWindow");
    assert.ok(lifecycle >= 0 && damage >= 0 && zone >= 0, "required start-turn windows are missing");
    assert.ok(lifecycle < zone, "target condition lifecycle must precede new zone saves");
    assert.ok(damage < zone, "start-turn ongoing damage must precede new zone saves");
  } catch (error) {
    console.error("Browser zone turn-start ordering contract failed", { error });
    throw error;
  }
});
