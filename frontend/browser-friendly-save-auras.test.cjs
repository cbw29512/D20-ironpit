"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = {};
window.IRON_PIT_BROWSER_STATE = { distance: (a, b) => Math.abs(a.position_ft - b.position_ft) };
window.IRON_PIT_BROWSER_MODIFIERS = {
  add: (state, modifier) => {
    state.active_modifiers ||= [];
    if (!state.active_modifiers.some((item) => item.id === modifier.id)) state.active_modifiers.push(modifier);
  },
};
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  has: (state, id) => (state.active_effect_ids || []).includes(id),
  incapacitated: (state) => state.is_unconscious || (state.active_effect_ids || []).includes("incapacitated"),
};

for (const file of ["browser-defensive-modifier-rules.js", "browser-friendly-save-auras.js"]) {
  vm.runInThisContext(fs.readFileSync(`frontend/${file}`, "utf8"));
}

const action = {
  id: "countercharm", name: "Countercharm",
  friendlySaveAdvantageAura: {
    radius_ft: 30,
    required_effect_tags: ["charmed", "frightened"],
    requires_hearing: true,
  },
};
const source = {
  combatant_id: "bard", side: "heroes", position_ft: 0,
  state: {
    current_hp: 20, is_alive: true, is_dead: false, is_unconscious: false,
    active_effect_ids: [], active_modifiers: [],
    timed_effects: [{ effect_id: "countercharm", source_id: "bard", source_effect_id: "countercharm" }],
    template: { name: "Bard", timed_self_buff_actions: [action] },
  },
};
const ally = {
  combatant_id: "ally", side: "heroes", position_ft: 20,
  state: {
    current_hp: 20, is_alive: true, is_dead: false, is_unconscious: false,
    active_effect_ids: [], active_modifiers: [], timed_effects: [],
    template: { name: "Ally", timed_self_buff_actions: [] },
  },
};
const enemy = {
  combatant_id: "enemy", side: "monsters", position_ft: 40,
  state: {
    current_hp: 20, is_alive: true, is_dead: false, is_unconscious: false,
    active_effect_ids: [], active_modifiers: [], timed_effects: [],
    template: { name: "Enemy", timed_self_buff_actions: [] },
  },
};
const setup = { heroes: [source, ally], monsters: [enemy] };
const A = window.IRON_PIT_BROWSER_FRIENDLY_SAVE_AURAS;
const D = window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS;

A.sync(setup);
assert.equal(D.saveAdvantage(ally.state, "wisdom", { effectTags: ["charmed"] }), 1);
assert.equal(D.saveAdvantage(ally.state, "wisdom", { effectTags: ["frightened"] }), 1);
assert.equal(D.saveAdvantage(ally.state, "wisdom", { effectTags: ["poison"] }), 0);

ally.position_ft = 35;
A.sync(setup);
assert.equal(D.saveAdvantage(ally.state, "wisdom", { effectTags: ["charmed"] }), 0);

ally.position_ft = 20;
ally.state.active_effect_ids = ["deafened"];
A.sync(setup);
assert.equal(D.saveAdvantage(ally.state, "wisdom", { effectTags: ["charmed"] }), 0);

ally.state.active_effect_ids = [];
source.state.active_effect_ids = ["incapacitated"];
A.sync(setup);
assert.equal(D.saveAdvantage(ally.state, "wisdom", { effectTags: ["charmed"] }), 0);

console.log("Browser friendly save-aura regressions passed.");
