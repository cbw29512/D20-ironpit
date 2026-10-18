"use strict";
const assert = require("node:assert/strict");
global.window = globalThis;
try {
  require("./browser-monsters-2014.js");
  const monsters = window.IRON_PIT_BROWSER_MONSTERS_2014;
  assert.equal(Object.keys(monsters).length, 228);
  const rust = monsters["2014-rust-monster"];
  const nightmare = monsters["2014-nightmare"];
  assert.ok(rust && nightmare);
  assert.ok(rust.source_trait_names.includes("Iron Scent"));
  assert.ok(rust.source_trait_names.includes("Rust Metal"));
  assert.ok(nightmare.source_trait_names.includes("Confer Fire Resistance"));
  assert.ok(nightmare.damage_immunities.includes("fire"));
  assert.ok(rust.attacks.some((a) => a.name === "Bite"));
  assert.ok(nightmare.attacks.some((a) => a.name === "Hooves"));
  assert.ok(!rust.attacks.some((a) => a.name === "Antennae"));
  assert.ok(!nightmare.attacks.some((a) => a.name === "Ethereal Stride"));
} catch (error) {
  console.error("2014 absent-context browser regression failed", error);
  throw error;
}
