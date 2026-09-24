const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = {};
function load(file) {
  vm.runInThisContext(fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file });
}

load("browser-action-economy.js");
load("browser-ability-hooks.js");
load("browser-timed-conditions.js");

window.IRON_PIT_BROWSER_STATE = { distance: () => 20 };
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount) => amount,
  applyDamage: (state, amount) => {
    state.current_hp = Math.max(0, state.current_hp - amount);
    if (state.current_hp === 0) {
      state.is_unconscious = true;
      state.is_alive = true;
    }
    return state.current_hp === 0 ? "unconscious" : "damaged";
  },
};

load("browser-timed-auras.js");

const aura = {
  id: "holy-nimbus",
  name: "Holy Nimbus",
  actionCost: "action",
  resourceId: "holy-nimbus",
  resourceCost: 1,
  durationRounds: 10,
  radiusFt: 30,
  startTurnFixedDamage: 10,
  damageType: "radiant",
  savingThrowAdvantageAbilities: [
    "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
  ],
  savingThrowAdvantageSourceCreatureTypes: ["fiend", "undead"],
  savingThrowAdvantageRequiresSpell: true,
  priority: 90,
  animation: "holy-nimbus",
};

function state(name, timedAuraActions = []) {
  return {
    template: { name, ruleset: "2014", timed_aura_actions: timedAuraActions },
    current_hp: 30,
    is_alive: true,
    is_dead: false,
    is_unconscious: false,
    action_available: true,
    bonus_action_available: true,
    reaction_available: true,
    resources: { "holy-nimbus": 1 },
    timed_effects: [],
    active_effect_ids: [],
  };
}

const paladin = { combatant_id: "paladin", side: "heroes", state: state("Aurelia", [aura]) };
const enemy = { combatant_id: "enemy", side: "monsters", state: state("Enemy") };
const setup = { heroes: [paladin], monsters: [enemy] };
const TA = window.IRON_PIT_BROWSER_TIMED_AURAS;

assert.equal(TA.choose(paladin).id, "holy-nimbus");
const activation = TA.activate(1, 1, paladin, aura);
assert.equal(activation.feature_id, "holy-nimbus");
assert.equal(paladin.state.resources["holy-nimbus"], 0);
assert.equal(paladin.state.action_available, false);

const start = TA.resolveStartTurn(2, 1, enemy, setup);
assert.equal(start.events.length, 1);
assert.equal(start.events[0].feature_id, "holy-nimbus");
assert.equal(enemy.state.current_hp, 20);

assert.equal(
  TA.saveAdvantage(paladin.state, "dexterity", { sourceIsSpell: true, sourceCreatureType: "Fiend" }),
  1,
);
assert.equal(
  TA.saveAdvantage(paladin.state, "wisdom", { sourceIsSpell: true, sourceCreatureType: "Undead" }),
  1,
);
assert.equal(
  TA.saveAdvantage(paladin.state, "dexterity", { sourceIsSpell: true, sourceCreatureType: "Humanoid" }),
  0,
);
assert.equal(
  TA.saveAdvantage(paladin.state, "dexterity", { sourceIsSpell: false, sourceCreatureType: "Fiend" }),
  0,
);

const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
assert.ok(
  hooks.abilitiesFor(hooks.PHASES.TURN_START)
    .some((item) => item.id === "timed-aura-start-turn"),
);

console.log("Browser timed aura activation, start-turn damage, and typed spell-save Advantage passed.");
