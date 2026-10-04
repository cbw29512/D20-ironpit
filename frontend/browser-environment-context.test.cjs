"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;

window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs((a.position_ft || 0) - (b.position_ft || 0)),
};
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  incapacitated: (state) =>
    Boolean(state.is_unconscious)
    || (state.active_effect_ids || []).includes("incapacitated"),
};
window.IRON_PIT_BROWSER_MODIFIERS = { d20TestAdvantage: () => 0 };
window.IRON_PIT_BROWSER_ROLLS = {
  modeFromSources: (advantage, disadvantage) => {
    if (advantage && disadvantage) return "normal";
    if (advantage) return "advantage";
    if (disadvantage) return "disadvantage";
    return "normal";
  },
};

for (const file of ["browser-environment-context.js", "browser-ability-checks.js"]) {
  vm.runInThisContext(fs.readFileSync(`frontend/${file}`, "utf8"), { filename: file });
}

const sunlightAura = {
  id: "generic-sunlight-source",
  inactiveWhileSourceIncapacitated: true,
  environmentContextAura: {
    radius_ft: 30,
    context_tags: ["sunlight"],
  },
};

const source = {
  combatant_id: "source",
  side: "heroes",
  position_ft: 0,
  state: {
    is_unconscious: false,
    active_effect_ids: [],
    timed_effects: [{
      effect_id: "generic-sunlight-source",
      source_id: "source",
      source_effect_id: "generic-sunlight-source",
    }],
    template: {
      name: "Context Source",
      timed_self_buff_actions: [sunlightAura],
      environmentContextReactions: [],
    },
  },
};

const sensitive = {
  combatant_id: "sensitive",
  side: "monsters",
  position_ft: 20,
  state: {
    is_unconscious: false,
    active_effect_ids: [],
    active_modifiers: [],
    template: {
      name: "Sensitive Target",
      timed_self_buff_actions: [],
      environmentContextReactions: [{
        contextTag: "sunlight",
        attackRollDisadvantage: true,
        abilityCheckDisadvantage: true,
      }],
    },
  },
};

const neutral = {
  combatant_id: "neutral",
  side: "monsters",
  position_ft: 20,
  state: {
    is_unconscious: false,
    active_effect_ids: [],
    active_modifiers: [],
    template: {
      name: "Neutral Target",
      timed_self_buff_actions: [],
      environmentContextReactions: [],
    },
  },
};

const setup = { heroes: [source], monsters: [sensitive, neutral] };
const EC = window.IRON_PIT_BROWSER_ENVIRONMENT_CONTEXT;
const checks = window.IRON_PIT_BROWSER_ABILITY_CHECKS;

assert.deepEqual([...EC.activeTags(sensitive, setup)], ["sunlight"]);
assert.equal(EC.disadvantage(sensitive, setup, "attack_roll"), 1);
assert.equal(EC.disadvantage(sensitive, setup, "ability_check"), 1);
assert.equal(checks.mode(sensitive.state, 0, 0, { member: sensitive, setup }), "disadvantage");

assert.equal(EC.disadvantage(neutral, setup, "attack_roll"), 0);
assert.equal(checks.mode(neutral.state, 0, 0, { member: neutral, setup }), "normal");

sensitive.position_ft = 35;
assert.equal(EC.disadvantage(sensitive, setup, "attack_roll"), 0);
assert.equal(checks.mode(sensitive.state, 0, 0, { member: sensitive, setup }), "normal");

sensitive.position_ft = 20;
source.state.active_effect_ids.push("incapacitated");
assert.equal(EC.disadvantage(sensitive, setup, "attack_roll"), 0);
assert.equal(EC.disadvantage(sensitive, setup, "ability_check"), 0);
assert.equal(checks.mode(sensitive.state, 0, 0, { member: sensitive, setup }), "normal");

source.state.active_effect_ids = [];
source.state.timed_effects = [];
assert.equal(EC.disadvantage(sensitive, setup, "attack_roll"), 0);

for (const htmlPath of ["frontend/index.html", "index.html"]) {
  const html = fs.readFileSync(htmlPath, "utf8");
  assert.match(html, /browser-environment-context\.js/);
}

console.log("Browser universal environment-context reactions passed.");
