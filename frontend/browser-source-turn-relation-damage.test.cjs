"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
window.IRON_PIT_DICE = {
  rolls: [],
  rollMany(count, size) {
    assert.equal(size, 10);
    return Array.from({ length: count }, () => this.rolls.shift());
  },
};
window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = {
  resolveDamage(state, total, type) {
    const immune = (state.template.damage_immunities || []).includes(type);
    const resisted = (state.template.damage_resistances || []).includes(type);
    return { applied: immune ? 0 : resisted ? Math.floor(total / 2) : total };
  },
};
window.IRON_PIT_BROWSER_ATTACK = {
  applyDamage(state, total) {
    state.current_hp = Math.max(0, state.current_hp - total);
    if (state.current_hp === 0) { state.is_alive = false; state.is_dead = true; }
  },
};
load("browser-source-turn-relation-damage.js");
const Source = window.IRON_PIT_BROWSER_SOURCE_TURN_RELATION_DAMAGE;
const rule = Object.freeze({
  source_name: "Barbed Hide", target_relation: "creatures_grappling_source",
  dice_count: 1, dice_size: 10, damage_type: "piercing",
});
const make = (name, side, position) => ({
  combatant_id: name, side, position_ft: position,
  state: {
    template: { name, source_turn_relation_damages: name === "devil" ? [rule] : [] },
    current_hp: 30, is_alive: true, is_dead: false, grapple_sources: [],
  },
});
const devil = make("devil", "monsters", 0);
const first = make("first", "heroes", 5), second = make("second", "heroes", 5);
const combat = { heroes: [first, second], monsters: [devil] };
assert.equal(Source.resolve(1, 1, devil, combat).events.length, 0);
devil.state.grapple_sources.push({ source_id: "first", range_ft: 10 });
devil.state.grapple_sources.push({ source_id: "second", range_ft: 10 });
window.IRON_PIT_DICE.rolls = [7, 6];
const result = Source.resolve(1, 1, devil, combat);
assert.equal(result.sequence, 3);
assert.deepEqual(result.events.map((item) => item.target_id), ["first", "second"]);
assert.equal(first.state.current_hp, 23);
assert.equal(second.state.current_hp, 24);
assert.equal(result.events[0].damage_components[0].applied_total, 7);
assert.equal(Source.resolve(3, 1, first, combat).events.length, 0);
devil.state.grapple_sources = devil.state.grapple_sources.filter((item) => item.source_id !== "first");
second.state.template.damage_resistances = ["piercing"];
window.IRON_PIT_DICE.rolls = [7];
const resisted = Source.resolve(3, 2, devil, combat);
assert.equal(resisted.events.length, 1);
assert.equal(second.state.current_hp, 21);
assert.equal(resisted.events[0].damage_components[0].applied_total, 3);
second.state.template.damage_immunities = ["piercing"];
window.IRON_PIT_DICE.rolls = [8];
assert.equal(Source.resolve(4, 3, devil, combat).events[0].damage_components[0].applied_total, 0);
second.position_ft = 25;
assert.equal(Source.resolve(5, 4, devil, combat).events.length, 0);
second.position_ft = 5;
devil.state.is_dead = true;
assert.equal(Source.resolve(6, 4, devil, combat).events.length, 0);
const newDevil = make("devil", "monsters", 0);
assert.deepEqual(newDevil.state.grapple_sources, []);
console.log("2014 source-turn grapple-target typed damage browser regressions passed.");
