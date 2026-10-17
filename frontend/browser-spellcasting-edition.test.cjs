"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

const source = fs.readFileSync(path.join(__dirname, "browser-spellcasting.js"), "utf8");

function spellcastingApi() {
  try {
    const context = { window: {} };
    vm.runInNewContext(source, context, { filename: "browser-spellcasting.js" });
    return context.window.IRON_PIT_BROWSER_SPELLCASTING;
  } catch (error) {
    console.error("Unable to load shared browser spellcasting runtime", error);
    throw error;
  }
}

for (const [ruleset, secondCastLegal] of [["2014", true], ["2024", false]]) {
  test(`${ruleset} slot restriction respects edition and fight reset`, () => {
    try {
      const api = spellcastingApi();
      const template = { ruleset };
      const state = { template, spell_slot_expended_turn_key: null };
      assert.equal(api.slotSpellAvailable(state, "1:caster"), true);
      api.markSlotSpellCast(state, "1:caster");
      assert.equal(api.slotSpellAvailable(state, "1:caster"), secondCastLegal);
      if (secondCastLegal) api.markSlotSpellCast(state, "1:caster");
      else assert.throws(() => api.markSlotSpellCast(state, "1:caster"), /already been expended/);
      assert.equal(api.slotSpellAvailable(state, "2:caster"), true);
      assert.equal(api.slotSpellAvailable({ template, spell_slot_expended_turn_key: null }, "1:caster"), true);
    } catch (error) {
      console.error("Browser spellcasting edition regression failed", { ruleset, error });
      throw error;
    }
  });
}

test("unsupported ruleset and missing turn key fail closed", () => {
  try {
    const api = spellcastingApi();
    assert.throws(() => api.slotSpellAvailable({ template: { ruleset: "legacy" } }, "1:caster"), /Unsupported/);
    assert.throws(() => api.slotSpellAvailable({ template: { ruleset: "2014" } }, ""), /active turn key/);
  } catch (error) {
    console.error("Browser spellcasting invalid-state regression failed", error);
    throw error;
  }
});

for (const ruleset of ["2014", "2024"]) {
  test(`${ruleset} first spell records before its own slot expenditure`, () => {
    try {
      const api = spellcastingApi();
      const template = { ruleset };
      const state = { template, feature_last_turn_keys: {}, spell_slot_expended_turn_key: null };
      assert.equal(api.spellTurnLegal(state, "1:caster", "action", 1), true);
      api.recordSpellTurn(state, "1:caster", "action", 1);
      api.markSlotSpellCast(state, "1:caster");
      assert.equal(api.slotSpellAvailable(state, "1:caster"), ruleset === "2014");
      if (ruleset === "2024") assert.equal(api.spellTurnLegal(state, "1:caster", "action", 1), false);
      assert.equal(api.slotSpellAvailable({ template, spell_slot_expended_turn_key: null }, "1:caster"), true);
    } catch (error) {
      console.error("First-spell ordering regression failed", { ruleset, error });
      throw error;
    }
  });
}

test("2014 healing candidate selection honors bonus-action spell timing", () => {
  try {
    const context = { window: {}, console };
    vm.runInNewContext(source, context);
    vm.runInNewContext(fs.readFileSync(path.join(__dirname, "browser-healing-policy.js"), "utf8"), context);
    const policy = context.window.IRON_PIT_BROWSER_HEALING_POLICY;
    const member = { state: {
      template: { ruleset: "2014" },
      feature_last_turn_keys: {}, resources: { "spell-slot-1": 2 },
      spell_slot_expended_turn_key: null,
    } };
    const bonus = { resourceId: "spell-slot-1", resourceCost: 1, actionCost: "bonus_action" };
    const action = { ...bonus, actionCost: "action" };
    assert.equal(policy.resourceAvailable(member, action, "1:caster"), true);
    member.state.feature_last_turn_keys["spell:bonus-action"] = "1:caster";
    assert.equal(policy.resourceAvailable(member, action, "1:caster"), false);
    assert.equal(policy.resourceAvailable(member, action, "2:caster"), true);
    member.state.feature_last_turn_keys = { "spell:action-noncantrip": "1:caster" };
    assert.equal(policy.resourceAvailable(member, bonus, "1:caster"), false);
  } catch (error) {
    console.error("2014 healing spell selection regression failed", error);
    throw error;
  }
});

test("explicit save-spell choice rejects a 2014 cast after bonus-action spell", () => {
  try {
    const context = { window: {}, console };
    vm.runInNewContext(source, context);
    context.window.IRON_PIT_ACTION_ECONOMY = { available: () => true };
    context.window.IRON_PIT_BROWSER_SPELL_POLICY_SUPPORT = {
      scaledSpell: (action) => action, slotLevel: () => 1, slotLevels: () => [1],
      alternateCasts: () => [], castOptions: () => [{ castLevel: 1, alternateCast: null }],
      protectedUniversalPlacements: () => [{ enemyIds: [], friendlyIds: [], protectedFriendlyIds: [] }],
      placementKey: () => "one", effectiveRange: () => 30,
      availableRangeModifier: () => null,
    };
    vm.runInNewContext(fs.readFileSync(path.join(__dirname, "browser-spell-policy.js"), "utf8"), context);
    const caster = { combatant_id: "caster", side: "heroes", state: {
      template: { ruleset: "2014", spell_save_actions: [{
        id: "synthetic-save", level: 1, actionCost: "action", range: 30, area: { origin: "point" },
      }] }, feature_last_turn_keys: { "spell:bonus-action": "1:caster" },
    } };
    const setup = { heroes: [caster], monsters: [] };
    assert.equal(context.window.IRON_PIT_BROWSER_SPELL_POLICY.chooseById(
      caster, setup, "1:caster", "synthetic-save"), null);
  } catch (error) {
    console.error("Explicit 2014 spell selection regression failed", error);
    throw error;
  }
});

for (const [firstCost, firstLevel, secondCost, secondLevel, allowed] of [
  ["bonus_action", 1, "action", 0, true],
  ["bonus_action", 1, "action", 1, false],
  ["bonus_action", 1, "reaction", 0, false],
  ["action", 1, "bonus_action", 1, false],
  ["action", 0, "bonus_action", 1, true],
  ["action", 1, "action", 1, true],
]) {
  test(`2014 cast order ${firstCost}/${firstLevel} -> ${secondCost}/${secondLevel}`, () => {
    try {
      const api = spellcastingApi();
      const state = { template: { ruleset: "2014" }, feature_last_turn_keys: {} };
      api.recordSpellTurn(state, "1:caster", firstCost, firstLevel);
      assert.equal(api.spellTurnLegal(state, "1:caster", secondCost, secondLevel), allowed);
      assert.equal(api.spellTurnLegal(state, "2:caster", secondCost, secondLevel), true);
    } catch (error) {
      console.error("Browser 2014 spell ordering regression failed", error);
      throw error;
    }
  });
}
