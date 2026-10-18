"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const source = fs.readFileSync(path.join(__dirname, "browser-spellcasting.js"), "utf8");

for (const ruleset of ["2014", "2024"]) {
  test(`${ruleset} cantrip slot lookup validates ruleset and turn`, () => {
    try {
      const context = { window: {}, console };
      vm.runInNewContext(source, context, { filename: "browser-spellcasting.js" });
      const api = context.window.IRON_PIT_BROWSER_SPELLCASTING;
      const state = { template: { ruleset }, resources: {}, spell_slot_expended_turn_key: null };
      assert.deepEqual(Array.from(api.legalSlotLevels(state, "1:caster", 0)), [0]);
      api.markSlotSpellCast(state, "1:caster");
      assert.deepEqual(Array.from(api.legalSlotLevels(state, "1:caster", 0)), [0]);
      assert.throws(() => api.legalSlotLevels(state, "", 0), /active turn key/);
      assert.throws(() => api.legalSlotLevels(state, "1:caster", true), /integer/);
      assert.throws(() => api.legalSlotLevels(state, "1:caster", -1), /integer/);
      assert.throws(() => api.legalSlotLevels(
        { ...state, template: { ruleset: "unknown" } }, "1:caster", 0,
      ), /Unsupported/);
    } catch (error) {
      console.error("Cantrip slot-query validation regression failed", { ruleset, error });
      throw error;
    }
  });
}

// CI invokes this entry point; include the shared edition-timing parity regressions.
try {
  require("./browser-spellcasting-edition.test.cjs");
} catch (error) {
  console.error("Unable to register spellcasting edition parity regressions", error);
  throw error;
}
