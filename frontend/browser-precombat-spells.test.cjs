"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-rules.js", "browser-modifiers.js", "browser-state.js",
  "browser-concentration.js", "browser-spell-modifiers.js", "browser-precombat-spells.js",
]) load(file);
const S = window.IRON_PIT_BROWSER_STATE;
const P = window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS;
const C = window.IRON_PIT_BROWSER_CONCENTRATION;
const H = window.IRON_PIT_BROWSER_HEROES;
const base = H["karnok-stoneward-l1"];
const defense = (id, level, priority = 0) => ({
  id, name: id, level, actionCost: "action", range: 0, durationMinutes: 60,
  targetPolicy: "self", targetCount: 1,
  temporaryHp: 5, temporaryHpPerSlotAbove: 5, damageResistances: [], modifierEffects: [],
  concentration: false, priority, animation: "precombat-defense",
});
function caster(spells, slots) {
  const template = structuredClone(base);
  template.defensive_spell_actions = spells;
  template.resources = Object.fromEntries(Object.entries(slots).map(([level, uses]) => [`spell-slot-${level}`, uses]));
  return { combatant_id: "caster", side: "heroes", position_ft: 0, state: S.buildState(template) };
}
const enemy = () => ({ combatant_id: "enemy", side: "monsters", position_ft: 30, state: S.buildState(structuredClone(base)) });

{
  const c = caster([defense("preferred", 1, 10), defense("backup", 2)], { 1: 1, 3: 1 });
  const result = P.prepare({ heroes: [c], monsters: [enemy()] });
  assert.equal(result.events.length, 1);
  assert.equal(result.events[0].feature_id, "preferred");
  assert.equal(c.state.temporary_hp, 5);
  assert.equal(c.state.resources["spell-slot-1"], 0);
  assert.equal(c.state.resources["spell-slot-3"], 1);
  assert.equal(c.state.action_available, true);
  assert.equal(c.state.bonus_action_available, true);
}

{
  const c = caster([defense("stronger", 2, 1), defense("weaker", 1, 99)], { 1: 1, 2: 1 });
  const result = P.prepare({ heroes: [c], monsters: [enemy()] });
  assert.equal(result.events[0].feature_id, "stronger");
  assert.equal(c.state.opening_buff_spell_id, "stronger");
  assert.equal(c.state.resources["spell-slot-2"], 0);
  assert.equal(c.state.resources["spell-slot-1"], 1);
}

{
  const c = caster([defense("no-upcast", 1)], { 3: 1 });
  const result = P.prepare({ heroes: [c], monsters: [enemy()] });
  assert.equal(result.events.length, 0);
  assert.equal(c.state.temporary_hp, 0);
  assert.equal(c.state.resources["spell-slot-3"], 1);
  assert.equal(P.choose(c), null);
}

{
  const unsafe = { ...defense("unsafe", 1, 20), concentration: true };
  const c = caster([unsafe], { 1: 1 });
  assert.throws(() => P.prepare({ heroes: [c], monsters: [enemy()] }), /source-owned modifier effects/);
}

{
  const spell = { ...defense("resist-fire", 1), temporaryHp: 0, temporaryHpPerSlotAbove: 0, damageResistances: ["fire"] };
  const c = caster([spell], { 1: 1 });
  P.prepare({ heroes: [c], monsters: [enemy()] });
  assert.deepEqual(c.state.temporary_damage_resistances, ["fire"]);
}

{
  const template = structuredClone(H["seraphine-dawnshield-l1"]);
  const c = { combatant_id: "cleric", side: "heroes", position_ft: 0, state: S.buildState(template) };
  const ally = { combatant_id: "ally", side: "heroes", position_ft: 5, state: S.buildState(structuredClone(base)) };
  const setup = { heroes: [c, ally], monsters: [enemy()] }, states = [c.state, ally.state, setup.monsters[0].state];
  const first = P.prepare(setup);
  assert.equal(first.events[0].feature_id, "bless");
  assert.equal(first.events[0].concentration_started_effect_id, "bless");
  assert.equal(c.state.opening_buff_spell_id, "bless");
  C.end(c.state, states);
  c.state.resources["spell-slot-1"] = 1;
  const second = P.prepare(setup, 99);
  assert.equal(second.events.length, 0);
  assert.equal(c.state.resources["spell-slot-1"], 1);
}

console.log("Browser precombat defensive spell regressions passed.");
