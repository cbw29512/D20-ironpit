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

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "bonus_action" ? state.bonus_action_available : state.action_available,
  spend: (state, cost) => {
    if (cost === "bonus_action") state.bonus_action_available = false;
    else if (cost === "action") state.action_available = false;
  },
};
window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => state.template.max_hp,
};
window.IRON_PIT_BROWSER_SPELLCASTING = {
  slotSpellAvailable: () => true,
  markSlotSpellCast: () => {},
};
window.IRON_PIT_DICE = { roll: () => 5 };

load("browser-heroes.js");
load("browser-healing.js");
load("browser-ability-hooks.js");
load("browser-support.js");

const hero = Object.values(window.IRON_PIT_BROWSER_HEROES)
  .find((item) => item.id === "karnok-stoneward-2014-l11");
assert.ok(hero, "certified 2014 Fighter level 11 must be exported");
assert.deepEqual(hero.healingActions, [{
  id: "second-wind",
  name: "Second Wind",
  actionCost: "bonus_action",
  range: 0,
  targetMode: "self",
  maxTargets: 1,
  diceCount: 1,
  diceSize: 10,
  healingBonus: 11,
  resourceId: "second-wind",
  resourceCost: 1,
  animation: "second-wind",
}]);

const member = {
  combatant_id: "fighter-2014",
  side: "heroes",
  position_ft: 0,
  state: {
    template: hero,
    current_hp: Math.floor(hero.max_hp / 2),
    is_alive: true,
    is_dead: false,
    is_unconscious: false,
    death_save_successes: 0,
    death_save_failures: 0,
    bonus_action_available: true,
    action_available: true,
    resources: { ...hero.resources },
  },
};
const choice = window.IRON_PIT_BROWSER_HEALING.chooseAction(
  member, { heroes: [member], monsters: [] }, "1:fighter-2014",
);
assert.ok(choice);
assert.equal(choice.action.id, "second-wind");
const event = window.IRON_PIT_BROWSER_HEALING.resolve(
  1, 1, member, member, choice.action, "1:fighter-2014",
);
assert.equal(event.feature_id, "second-wind");
assert.equal(event.healing_roll.total, 16);
assert.equal(member.state.resources["second-wind"], 0);
assert.equal(member.state.bonus_action_available, false);

window.IRON_PIT_BROWSER_SUPPORT.installAbilityHooks();
const hook = window.IRON_PIT_BROWSER_ABILITY_HOOKS
  .abilitiesFor(window.IRON_PIT_BROWSER_ABILITY_HOOKS.PHASES.BONUS_ACTION_WINDOW)
  .find((item) => item.id === "second-wind");
assert.deepEqual(hook.rulesets, ["2024"]);

console.log("2014 Fighter Second Wind uses universal browser healing; legacy hook remains 2024-only.");
