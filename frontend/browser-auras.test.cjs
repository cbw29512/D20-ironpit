"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
window.IRON_PIT_DICE = { roll: () => 7 };
window.IRON_PIT_BROWSER_ZERO_HP = {
  applyDamage: (state, amount) => { state.current_hp = Math.max(0, state.current_hp - amount); },
};
window.IRON_PIT_BROWSER_STATE = {
  distance: (left, right) => Math.abs(left.position_ft - right.position_ft),
};
load("browser-ongoing-damage.js");
load("browser-auras.js");

const source = {
  combatant_id: "azer", side: "monsters", position_ft: 5,
  state: { is_alive: true, is_dead: false, is_unconscious: false, active_effect_ids: [], template: {
    name: "Azer Sentinel", damage_resistances: [], damage_vulnerabilities: [], damage_immunities: [],
    end_turn_damage_auras: [{
      id: "fire-aura", name: "Fire Aura", radius_ft: 5,
      damage_dice_count: 1, damage_dice_size: 10, damage_bonus: 0,
      damage_type: "fire", disabled_while_incapacitated: true,
    }],
  } },
};
const target = {
  combatant_id: "hero", side: "heroes", position_ft: 0,
  state: { current_hp: 20, is_alive: true, is_dead: false, template: {
    name: "Hero", damage_resistances: [], damage_vulnerabilities: [], damage_immunities: [],
  } },
};
const setup = { heroes: [target], monsters: [source] };
const result = window.IRON_PIT_BROWSER_AURAS.turnEnd(1, 1, source, setup);
assert.equal(result.sequence, 2);
assert.equal(result.events.length, 1);
assert.equal(result.events[0].feature_id, "fire-aura");
assert.equal(result.events[0].damage_roll.total, 7);
assert.equal(target.state.current_hp, 13);

source.state.active_effect_ids = ["incapacitated"];
const blocked = window.IRON_PIT_BROWSER_AURAS.turnEnd(2, 2, source, setup);
assert.equal(blocked.events.length, 0);
assert.equal(target.state.current_hp, 13);

console.log("Browser end-turn damage aura uses the shared ongoing-damage pipeline and honors Incapacitated suppression.");
