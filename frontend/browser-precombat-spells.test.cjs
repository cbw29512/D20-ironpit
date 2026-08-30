"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of ["browser-heroes.js", "browser-condition-rules.js", "browser-state.js", "browser-precombat-spells.js"]) load(file);
const S = window.IRON_PIT_BROWSER_STATE;
const P = window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
const defense = (id, level, priority = 0, concentration = false) => ({
  id, name: id, level, actionCost: "action", durationMinutes: 60,
  temporaryHp: 5, temporaryHpPerSlotAbove: 5, damageResistances: [],
  concentration, priority, animation: "precombat-defense",
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
  const c = caster([defense("upcast-defense", 1)], { 3: 1 });
  P.prepare({ heroes: [c], monsters: [enemy()] });
  assert.equal(c.state.temporary_hp, 15);
  assert.equal(c.state.resources["spell-slot-3"], 0);
}

{
  const c = caster([defense("concentration-defense", 1, 20, true), defense("safe-defense", 1)], { 1: 1 });
  assert.equal(P.choose(c).spell.id, "safe-defense");
}

{
  const spell = { ...defense("resist-fire", 1), temporaryHp: 0, temporaryHpPerSlotAbove: 0, damageResistances: ["fire"] };
  const c = caster([spell], { 1: 1 });
  P.prepare({ heroes: [c], monsters: [enemy()] });
  assert.deepEqual(c.state.temporary_damage_resistances, ["fire"]);
}

console.log("Browser precombat defensive spell regressions passed.");
