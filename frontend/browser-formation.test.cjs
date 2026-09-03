"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-state.js", "browser-formation.js", "browser-standard-attack-action.js", "browser-turn.js",
]) load(file);

const F = window.IRON_PIT_BROWSER_FORMATION;
const S = window.IRON_PIT_BROWSER_STATE;
const E = window.IRON_PIT_ACTION_ECONOMY;
const blade = { id: "blade", kind: "melee", reach: 5 };
const bow = { id: "bow", kind: "ranged", long: 80, normal: 80 };
const melee = { kind: "character", primary_attack_id: "blade", attacks: [blade] };
const meleeWithBackupRange = { kind: "character", primary_attack_id: "blade", attacks: [blade, bow] };
const ranged = { kind: "character", primary_attack_id: "bow", attacks: [bow, blade] };
const rangedCaster = { kind: "character", primary_attack_id: "staff", attacks: [{ id: "staff", kind: "melee" }], spell_save_actions: [{ range: 60 }] };
const buffOnly = { kind: "character", primary_attack_id: "staff", attacks: [{ id: "staff", kind: "melee" }], defensive_spell_actions: [{ range: 30 }] };

assert.equal(F.startingPosition(melee, "heroes"), 5);
assert.equal(F.startingPosition(melee, "monsters"), 10);
assert.equal(F.startingPosition(meleeWithBackupRange, "heroes"), 5, "backup range must not redefine a melee build's formation");
assert.equal(F.hasTrueRangeOffense(meleeWithBackupRange), true, "backup range remains usable while separated");
assert.equal(F.startingPosition(ranged, "heroes"), 0);
assert.equal(F.startingPosition(ranged, "monsters"), 15);
assert.equal(F.startingPosition(rangedCaster, "heroes"), 0, "true ranged spell offense may start backline");
assert.equal(F.startingPosition(buffOnly, "heroes"), 5, "buff capability alone must not create a backliner");

function template(name, primary, attacks) {
  return {
    id: name.toLowerCase(), name, kind: "character", size: "medium", max_hp: 10, speed_ft: 30,
    primary_attack_id: primary, attacks, traits: [], resources: {}, saving_throw_actions: [],
  };
}
const sword = { id: "sword", name: "Sword", kind: "melee", reach: 5 };
const combatBow = { id: "bow", name: "Bow", kind: "ranged", long: 80, normal: 80 };
const frontTemplate = template("Frontline", "sword", [sword]);
const archerTemplate = template("Archer", "bow", [combatBow, sword]);
const enemyTemplate = { ...template("Enemy", "sword", [sword]), kind: "monster" };
const combatant = (id, side, position, tpl) => ({ combatant_id: id, side, position_ft: position, state: S.buildState(tpl) });
const front = combatant("hero-frontline", "heroes", 5, frontTemplate);
const archer = combatant("hero-archer", "heroes", 0, archerTemplate);
const enemy = combatant("monster-enemy", "monsters", 10, enemyTemplate);
const setup = { heroes: [front, archer], monsters: [enemy] };

window.IRON_PIT_BROWSER_ATTACK = {
  resolveAttack(sequence, round, attacker, target, attack) {
    E.spend(attacker.state, "action");
    return { sequence, round_number: round, event_type: "attack", actor_id: attacker.combatant_id,
      target_id: target.combatant_id, weapon_id: attack.id, description: `${attacker.state.template.name} attacks.` };
  },
};

let turn = window.IRON_PIT_BROWSER_TURN.resolveTurn(1, 1, archer, setup);
assert.equal(F.backlineHoldsPosition(archer, setup), true);
assert.equal(archer.position_ft, 0, "true ranged offense stays at range while separated");
assert.deepEqual(turn.events.map((event) => event.event_type), ["attack"]);
assert.equal(turn.events[0].weapon_id, "bow");

front.state.current_hp = 0; front.state.is_alive = false; front.state.is_dead = true;
turn = window.IRON_PIT_BROWSER_TURN.resolveTurn(2, 2, archer, setup);
assert.equal(archer.position_ft, 0, "ranged behavior no longer depends on a frontline role");
assert.deepEqual(turn.events.map((event) => event.event_type), ["attack"]);
assert.equal(turn.events[0].weapon_id, "bow");

enemy.position_ft = 5;
turn = window.IRON_PIT_BROWSER_TURN.resolveTurn(3, 3, archer, setup);
assert.equal(F.backlineHoldsPosition(archer, setup), false, "engaged ranged combatant stops holding");
assert.equal(turn.events.find((event) => event.event_type === "attack").weapon_id, "sword", "engaged ranged combatant switches to melee");

console.log("Simple primary-range formation and close-to-melee browser policy regressions passed.");
