"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = {};
window.IRON_PIT_BROWSER_STATE = { distance: (a, b) => Math.abs(a.position_ft - b.position_ft) };
window.IRON_PIT_BROWSER_MODIFIERS = {
  d20TestAdvantage: () => 0,
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


source.state.active_effect_ids = [];
source.state.timed_effects = [];
source.state.template.timed_self_buff_actions = [];
source.state.template.friendly_saving_throw_aura = {
  source_id: "aura-of-protection-2024",
  source_name: "Aura of Protection",
  radius_ft: 10,
  flat_bonus: 2,
  inactive_while_incapacitated: true,
  inactive_while_unconscious: false,
};
ally.position_ft = 5;
A.sync(setup);
assert.equal(
  ally.state.active_modifiers.find((item) => item.kind === "saving-throw-flat")?.flat_bonus,
  2,
);

ally.position_ft = 15;
A.sync(setup);
assert.equal(
  ally.state.active_modifiers.some((item) => item.kind === "saving-throw-flat"),
  false,
);

ally.position_ft = 5;
source.state.active_effect_ids = ["incapacitated"];
A.sync(setup);
assert.equal(
  ally.state.active_modifiers.some((item) => item.kind === "saving-throw-flat"),
  false,
);

source.state.active_effect_ids = ["incapacitated"];
source.state.template.friendly_saving_throw_aura = {
  source_id: "aura-of-protection-2014",
  source_name: "Aura of Protection",
  radius_ft: 10,
  flat_bonus: 3,
  inactive_while_incapacitated: false,
  inactive_while_unconscious: true,
};
A.sync(setup);
assert.equal(
  ally.state.active_modifiers.find((item) => item.kind === "saving-throw-flat")?.flat_bonus,
  3,
);
