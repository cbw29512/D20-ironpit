"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

load("browser-action-economy.js");
load("browser-resources.js");
window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: (state) => state.active_effect_ids.includes("stunned") };
load("browser-rage.js");
load("browser-initiative-resource-refill.js");

function member(ruleset = "2024", persistent = true) {
  const template = {
    name: ruleset === "2024" ? "Rokhan L15" : "Rokhan 2014 L15",
    ruleset,
    rage_damage_bonus: 3,
    wearing_heavy_armor: false,
    mindless_rage: false,
    frenzy_bonus_attack_2014: false,
    persistent_rage_2014: ruleset === "2014" && persistent,
    rage_persists_without_maintenance: ruleset === "2024" && persistent,
    unlimited_resources: [],
    resources: { rage: 5 },
    initiative_resource_refill_grants: ruleset === "2024" && persistent ? [{
      source_id: "persistent-rage",
      source_name: "Persistent Rage",
      resource_id: "rage",
      when_at_or_below: 4,
      restore_amount: 5,
    }] : [],
  };
  return {
    combatant_id: ruleset === "2024" ? "hero:rokhan-l15" : "hero:rokhan-2014-l15",
    side: "heroes",
    state: {
      template,
      resources: { rage: 2 },
      active_effect_ids: [],
      timed_effects: [],
      temporary_damage_resistances: [],
      bonus_action_available: true,
      action_available: true,
      reaction_available: true,
      rage_expires_round: null,
      rage_max_round: null,
      is_dead: false,
      is_unconscious: false,
    },
  };
}

{
  const hero = member();
  const target = {
    combatant_id: "monster:target",
    side: "monsters",
    state: {
      template: { name: "Target", resources: {}, initiative_resource_refill_grants: [] },
      resources: {},
    },
  };
  const refill = window.IRON_PIT_BROWSER_INITIATIVE_RESOURCE_REFILL.resolve(
    1, { heroes: [hero], monsters: [target] },
  );
  assert.equal(refill.sequence, 2);
  assert.equal(hero.state.resources.rage, 5);
  assert.equal(refill.events[0].feature_id, "persistent-rage");

  const event = window.IRON_PIT_BROWSER_RAGE.enter(2, 1, hero);
  assert.ok(event);
  assert.equal(hero.state.resources.rage, 4);
  assert.equal(hero.state.rage_max_round, 101);
  assert.equal(hero.state.rage_expires_round, 101);

  hero.state.bonus_action_available = true;
  assert.equal(window.IRON_PIT_BROWSER_RAGE.maintain(3, 2, hero), null);
  assert.equal(hero.state.bonus_action_available, true);

  hero.state.active_effect_ids.push("stunned");
  window.IRON_PIT_BROWSER_RAGE.endIfIncapacitated(hero.state);
  assert.equal(window.IRON_PIT_BROWSER_RAGE.active(hero.state), true);

  hero.state.is_unconscious = true;
  window.IRON_PIT_BROWSER_RAGE.endIfIncapacitated(hero.state);
  assert.equal(window.IRON_PIT_BROWSER_RAGE.active(hero.state), false);
}

{
  const hero = member("2014", true);
  hero.state.resources.rage = 5;
  const event = window.IRON_PIT_BROWSER_RAGE.enter(1, 1, hero);
  assert.ok(event);
  assert.equal(hero.state.rage_max_round, 11);
  assert.equal(hero.state.rage_expires_round, 11);
}

console.log("Browser 2024 Persistent Rage parity passed.");
