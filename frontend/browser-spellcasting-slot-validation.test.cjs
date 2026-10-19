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

test("healing resource IDs reject malformed slot levels before casting", () => {
  try {
    const context = { window: {}, console };
    vm.runInNewContext(source, context, { filename: "browser-spellcasting.js" });
    vm.runInNewContext(fs.readFileSync(path.join(__dirname, "browser-healing-policy.js"), "utf8"),
      context, { filename: "browser-healing-policy.js" });
    const policy = context.window.IRON_PIT_BROWSER_HEALING_POLICY;
    for (const ruleset of ["2014", "2024"]) {
      const member = { state: {
        template: { ruleset }, feature_last_turn_keys: {},
        resources: { "spell-slot-1": 2, "spell-slot-1junk": 2 },
        spell_slot_expended_turn_key: null,
      } };
      assert.equal(policy.resourceAvailable(member, {
        resourceId: "spell-slot-1", actionCost: "bonus_action", resourceCost: 1,
      }, "1:caster"), true);
      for (const invalid of ["spell-slot-1junk", "spell-slot-01", "spell-slot-0", "spell-slot-10", "spell-slot-1e0"]) {
        assert.throws(() => policy.resourceAvailable(member, {
          resourceId: invalid, actionCost: "bonus_action", resourceCost: 1,
        }, "1:caster"), /Malformed spell-slot/);
        assert.throws(() => policy.resourceAvailable(member, {
          resourceId: invalid, actionCost: "bonus_action", resourceCost: 1,
        }, null), /Malformed spell-slot/);
      }
    }
    for (const invalid of [0, false, "", 1.5, []]) {
      assert.throws(() => policy.resourceAvailable({ state: { resources: {} } },
        { resourceId: invalid }, "1:caster"), /Healing resource ID/);
    }
  } catch (error) {
    console.error("Browser malformed healing spell-slot resource regression failed", error);
    throw error;
  }
});
