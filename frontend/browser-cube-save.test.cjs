const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = global;
window.IRON_PIT_BROWSER_FORMATION = {
  targetOrder: (actor, setup) => actor.side === "heroes" ? setup.monsters : setup.heroes,
  saveDistance: (actor, target, range) => Math.min(Math.abs(actor.position_ft - target.position_ft), range),
};
window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-saves.js"), "utf8"), { filename: "browser-saves.js" });

const state = (name) => ({ template: { name }, is_alive: true, is_dead: false, current_hp: 10 });
const actor = { combatant_id: "caster", side: "heroes", position_ft: 0, state: state("Caster") };
const enemy = (id, slot) => ({ combatant_id: id, side: "monsters", position_ft: 5, state: state(id), slot });
const setup = { heroes: [actor], monsters: [enemy("a", 0), enemy("b", 1), enemy("c", 2)] };
const action = { name: "Thunderwave", range: 15, area: { shape: "cube", sizeFt: 15 } };

const targets = window.IRON_PIT_BROWSER_SAVES.targetsFor(actor, setup, action);
assert.deepEqual(targets.map((target) => target.combatant_id), ["a", "b", "c"]);
