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
  roll(sides) {
    const result = this.rolls.shift();
    if (!Number.isInteger(result) || result < 1 || result > sides) throw Error("Unexpected die");
    return result;
  },
  rollMany(count, sides) { return Array.from({ length: count }, () => this.roll(sides)); },
};
window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = {
  resolveDamage(state, total, type) {
    return { applied: (state.template.damage_immunities || []).includes(type) ? 0 : total };
  },
};
window.IRON_PIT_BROWSER_ATTACK = {
  applyDamage(state, total) { state.current_hp -= total; return total ? "damaged" : "unchanged"; },
};
load("browser-grapple.js");
load("browser-start-of-turn-timed-burn.js");
const G = window.IRON_PIT_BROWSER_GRAPPLE;
const Burn = window.IRON_PIT_BROWSER_START_OF_TURN_TIMED_BURN;
const periodic = Object.freeze({
  source_name: "Chain grapple", dice_count: 2, dice_size: 6, damage_type: "piercing",
});
const make = (name, side, position) => ({
  combatant_id: name, side, position_ft: position,
  state: {
    template: { name, max_hp: 30, damage_immunities: [] }, current_hp: 30,
    is_alive: true, is_dead: false, is_unconscious: false,
    active_effect_ids: [], grapple_sources: [], timed_effects: [],
  },
});
const setup = () => {
  const dev = make("devil", "monsters", 0);
  const victim = make("victim", "heroes", 5);
  const second = make("second", "heroes", 5);
  return { dev, victim, second, combat: { heroes: [victim, second], monsters: [dev] } };
};

{
  const { dev, victim, second, combat } = setup();
  const status = G.apply(victim.state, "devil", 14, 10, true, false, periodic);
  assert.deepEqual(status, ["grappled", "restrained"]);
  assert.equal(victim.state.grapple_sources[0].escape_dc, 14);
  assert.equal(G.sourceHasActiveGrapple(combat, "devil"), true);
  assert.equal(second.state.grapple_sources.length, 0);
  // A second legal Chain hit may deal damage, but cannot establish another grapple.
  assert.equal(!G.sourceHasActiveGrapple(combat, "devil"), false);
  window.IRON_PIT_DICE.rolls = [3, 4];
  const result = Burn.resolve(1, 2, victim, combat);
  assert.equal(victim.state.current_hp, 23);
  assert.equal(result.events.length, 1);
  assert.match(result.events[0].description, /Chain grapple deals 7 piercing damage/);
  assert.deepEqual(window.IRON_PIT_DICE.rolls, []);
  G.release(victim.state, "devil");
  assert.equal(G.sourceHasActiveGrapple(combat, "devil"), false);
  assert.equal(victim.state.active_effect_ids.includes("restrained"), false);
  assert.equal(Burn.resolve(2, 3, victim, combat).events.length, 0);
}
{
  const { dev, victim, combat } = setup();
  victim.state.template.damage_immunities.push("piercing");
  G.apply(victim.state, "devil", 14, 10, true, false, periodic);
  window.IRON_PIT_DICE.rolls = [4, 5];
  const result = Burn.resolve(1, 2, victim, combat);
  assert.equal(victim.state.current_hp, 30);
  assert.match(result.events[0].description, /deals 0 piercing damage/);
  dev.state.is_dead = true;
  G.cleanup(combat);
  assert.equal(victim.state.grapple_sources.length, 0);
  assert.equal(Burn.resolve(2, 3, victim, combat).events.length, 0);
}
{
  const { dev, victim, combat } = setup();
  G.apply(victim.state, "devil", 14, 10, true, false, periodic);
  dev.position_ft = 20;
  G.cleanup(combat);
  assert.equal(victim.state.grapple_sources.length, 0);
  assert.equal(G.sourceHasActiveGrapple(combat, "devil"), false);
}
console.log("2014 Chain grapple periodic browser regressions passed.");
