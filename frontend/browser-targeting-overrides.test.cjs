const assert = require("assert");
const fs = require("fs");
const vm = require("vm");
global.window = global;
function load(file) {
  vm.runInThisContext(fs.readFileSync(__dirname + "/" + file, "utf8"), { filename: file });
}

window.IRON_PIT_DICE = { values: [6], roll() { return this.values.shift(); } };
window.IRON_PIT_BROWSER_STATE = {
  effectiveMaxHp: (state) => state.template.max_hp,
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
};
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  canSee: (_observer, target) => !(target.active_effect_ids || []).includes("invisible"),
};
window.IRON_PIT_BROWSER_CHARMED_TARGETING = { blocks: () => false };
window.IRON_PIT_BROWSER_HEALING_POLICY = { swarm: () => false };

load("browser-targeting-overrides.js");
load("browser-formation.js");
load("browser-healing.js");

const rule = {
  sourceId: "flesh-golem-berserk", sourceName: "Berserk",
  maxCurrentHp: 40, dieSize: 6, minimumRoll: 6,
  targetMode: "nearest_visible_creature", endsOnFullHp: true,
};
function member(id, side, position, hp = 100) {
  return {
    combatant_id: id, side, position_ft: position,
    state: {
      template: { name: id, kind: "monster", max_hp: 100, turn_start_targeting_overrides: [rule], attacks: [] },
      current_hp: hp, is_alive: true, is_dead: false, active_effect_ids: [],
      timed_effects: [], grapple_sources: [], active_targeting_override_ids: [],
    },
  };
}

const golem = member("golem", "monsters", 0, 40);
const result = window.IRON_PIT_BROWSER_TARGETING_OVERRIDES.resolveStartOfTurn(1, 1, golem);
assert.equal(result.events.length, 1);
assert.equal(result.events[0].feature_roll.total, 6);
assert.deepEqual(golem.state.active_targeting_override_ids, ["flesh-golem-berserk"]);

const ally = member("ally", "monsters", 5);
const enemy = member("enemy", "heroes", 20);
const setup = { heroes: [enemy], monsters: [golem, ally] };
assert.equal(window.IRON_PIT_BROWSER_FORMATION.targetOrder(golem, setup)[0], ally);

ally.state.active_effect_ids.push("invisible");
assert.equal(window.IRON_PIT_BROWSER_FORMATION.targetOrder(golem, setup)[0], enemy);

golem.state.current_hp = 99;
assert.equal(window.IRON_PIT_BROWSER_HEALING.restore(golem.state, 1), 1);
assert.deepEqual(golem.state.active_targeting_override_ids, []);

console.log("Browser turn-start targeting override parity passed.");
