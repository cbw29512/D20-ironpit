"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const script = fs.readFileSync(require("node:path").join(__dirname, "browser-friendly-roll-bonus-auras.js"), "utf8");

test("dynamic Leadership-style bonus reaches eligible allies and stops at source death", () => {
  const window = {
    IRON_PIT_BROWSER_STATE: { distance: (a, b) => Math.abs(a.x - b.x) },
    IRON_PIT_BROWSER_CONDITION_RULES: { has: (state, id) => state.active_effect_ids.includes(id) },
    IRON_PIT_BROWSER_MODIFIERS: { add: (state, modifier) => state.active_modifiers.push(modifier) },
  };
  vm.runInNewContext(script, { window, console });
  const state = (id, x) => ({
    combatant_id: id, side: "monsters", x,
    state: { is_alive: true, is_dead: false, current_hp: 20, active_modifiers: [],
      active_effect_ids: [], timed_effects: [], template: { timed_self_buff_actions: [] } },
  });
  const knight = state("knight", 0), ally = state("ally", 20), far = state("far", 40);
  knight.state.template.timed_self_buff_actions = [{
    id: "leadership", name: "Leadership",
    friendlyRollBonusAura: {
      radius_ft: 30, includes_source: true, requires_hearing: true,
      attack_dice_count: 1, attack_dice_size: 4, save_dice_count: 1, save_dice_size: 4,
    },
  }];
  knight.state.timed_effects.push({ source_id: "knight", source_effect_id: "leadership" });
  const setup = { heroes: [], monsters: [knight, ally, far] };
  const sync = window.IRON_PIT_BROWSER_FRIENDLY_ROLL_BONUS_AURAS.sync;
  sync(setup);
  assert.equal(knight.state.active_modifiers.length, 2);
  assert.equal(ally.state.active_modifiers.length, 2);
  assert.equal(far.state.active_modifiers.length, 0);
  assert.equal(ally.state.active_modifiers[0].source_name, "Leadership");
  sync(setup);
  assert.equal(ally.state.active_modifiers.length, 2, "resync must not stack duplicates");
  ally.state.active_effect_ids.push("deafened");
  sync(setup);
  assert.equal(ally.state.active_modifiers.length, 0);
  knight.state.current_hp = 0;
  sync(setup);
  assert.equal(knight.state.active_modifiers.length, 0);
});
