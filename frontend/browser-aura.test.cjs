"use strict";
const assert = require("node:assert/strict"), fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of ["browser-condition-rules.js", "browser-state.js", "browser-zero-hp.js", "browser-attack.js", "browser-aura.js"]) load(file);
const template = (id, resistance = false) => ({ id, name: id, kind: id === "azer" ? "monster" : "character", armor_class: 10, max_hp: 20, speed_ft: 30,
  movement_modes: { walk_ft: 30 }, traits: [], damage_immunities: [], damage_resistances: resistance ? ["fire"] : [], damage_vulnerabilities: [], condition_immunities: [],
  endTurnDamageAura: id === "azer" ? { name: "Fire Aura", radius: 5, diceCount: 1, diceSize: 10, damageBonus: 0, damageType: "fire", targetMode: "enemies", disabledWhileIncapacitated: true } : null });
const state = (t) => ({ template: t, current_hp: t.max_hp, temporary_hp: 0, temporary_damage_resistances: [], active_effect_ids: [], is_alive: true, is_dead: false, is_unconscious: false, is_stable: false, death_save_successes: 0, death_save_failures: 0, concentration: null });
const member = (id, side, t, position) => ({ combatant_id: id, side, position_ft: position, state: state(t) });
const source = member("m1", "monsters", template("azer"), 5), normal = member("h1", "heroes", template("normal"), 0), half = member("h2", "heroes", template("half", true), 10), ally = member("m2", "monsters", template("ally"), 5);
window.IRON_PIT_DICE = { roll: () => 7 };
let result = window.IRON_PIT_BROWSER_AURA.resolve(1, 1, source, { heroes: [normal, half], monsters: [source, ally] });
assert.equal(result.sequence, 3); assert.deepEqual(result.events.map((e) => e.damage_roll.total), [7, 3]);
assert.equal(normal.state.current_hp, 13); assert.equal(half.state.current_hp, 17); assert.equal(ally.state.current_hp, 20);
source.state.is_unconscious = true; normal.state.current_hp = 20;
result = window.IRON_PIT_BROWSER_AURA.resolve(3, 2, source, { heroes: [normal], monsters: [source] });
assert.deepEqual(result.events, []); assert.equal(normal.state.current_hp, 20);
console.log("Browser end-turn Fire Aura shared-roll, defenses, targeting, and Incapacitated regressions passed.");
