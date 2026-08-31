"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-state.js", "browser-formation.js", "browser-turn.js",
]) load(file);

const F = window.IRON_PIT_BROWSER_FORMATION;
const S = window.IRON_PIT_BROWSER_STATE;
const E = window.IRON_PIT_ACTION_ECONOMY;
const melee = { kind: "character", primary_attack_id: "blade", attacks: [{ id: "blade", kind: "melee" }] };
const ranged = { kind: "character", primary_attack_id: "bow", attacks: [{ id: "bow", kind: "ranged" }] };
const caster = { kind: "character", primary_attack_id: "staff", attacks: [{ id: "staff", kind: "melee" }], spell_save_actions: [{}] };

assert.equal(F.startingPosition(melee, "heroes"), 5);
assert.equal(F.startingPosition(melee, "monsters"), 10);
assert.equal(F.startingPosition(ranged, "heroes"), 0);
assert.equal(F.startingPosition(ranged, "monsters"), 15);
assert.equal(F.startingPosition(caster, "heroes"), 0);

function targetMember(id, side, position, kind = "monster") {
  return {
    combatant_id: id, side, position_ft: position,
    state: {
      template: { kind, size: "medium" }, current_hp: 10, is_alive: true, is_dead: false,
      is_unconscious: false, active_effect_ids: [], grapple_sources: [],
    },
  };
}

const heroFront = targetMember("hero-front", "heroes", 5, "character");
const heroBack = targetMember("hero-back", "heroes", 0, "character");
const monsterFront = targetMember("monster-front", "monsters", 10);
const monsterBack = targetMember("monster-back", "monsters", 15);
const targetSetup = { heroes: [heroFront, heroBack], monsters: [monsterFront, monsterBack] };
assert.equal(S.nearestTarget(heroBack, targetSetup).combatant_id, "monster-front", "backline attacks the active enemy frontline first");
assert.equal(S.nearestTarget(monsterBack, targetSetup).combatant_id, "hero-front", "enemy backline attacks the active hero frontline first");
assert.equal(S.nearestTarget(monsterFront, targetSetup).combatant_id, "hero-front", "frontlines begin engaged with each other");
heroFront.state.current_hp = 0; heroFront.state.is_alive = false; heroFront.state.is_dead = true;
assert.equal(S.nearestTarget(monsterFront, targetSetup).combatant_id, "hero-back", "backline becomes the target after its frontline falls");

function template(name, primary, attacks) {
  return {
    id: name.toLowerCase(), name, kind: "character", size: "medium", max_hp: 10, speed_ft: 30,
    primary_attack_id: primary, attacks, traits: [], resources: {}, saving_throw_actions: [],
  };
}
const bow = { id: "bow", name: "Bow", kind: "ranged", long: 80, normal: 80 };
const sword = { id: "sword", name: "Sword", kind: "melee", reach: 5 };
const frontTemplate = template("Frontline", "sword", [sword]);
const backTemplate = template("Archer", "bow", [bow, sword]);
const enemyTemplate = { ...template("Enemy", "sword", [sword]), kind: "monster" };
const combatant = (id, side, position, tpl) => ({ combatant_id: id, side, position_ft: position, state: S.buildState(tpl) });
const front = combatant("hero-frontline", "heroes", 5, frontTemplate);
const back = combatant("hero-archer", "heroes", 0, backTemplate);
const enemy = combatant("monster-enemy", "monsters", 10, enemyTemplate);
const setup = { heroes: [front, back], monsters: [enemy] };

window.IRON_PIT_BROWSER_ATTACK = {
  resolveAttack(sequence, round, attacker, target, attack) {
    E.spend(attacker.state, "action");
    return { sequence, round_number: round, event_type: "attack", actor_id: attacker.combatant_id,
      target_id: target.combatant_id, weapon_id: attack.id, description: `${attacker.state.template.name} attacks.` };
  },
};

let turn = window.IRON_PIT_BROWSER_TURN.resolveTurn(1, 1, back, setup);
assert.equal(F.backlineHoldsPosition(back, setup), true);
assert.equal(back.position_ft, 0, "backliner must not advance while an active frontline ally exists");
assert.deepEqual(turn.events.map((event) => event.event_type), ["attack"]);
assert.equal(turn.events[0].weapon_id, "bow");

front.state.current_hp = 0; front.state.is_alive = false; front.state.is_dead = true;
turn = window.IRON_PIT_BROWSER_TURN.resolveTurn(2, 2, back, setup);
assert.equal(F.backlineHoldsPosition(back, setup), false);
assert.equal(back.position_ft, 5, "backliner may close after the frontline is gone");
assert.deepEqual(turn.events.map((event) => event.event_type), ["movement", "attack"]);
assert.equal(turn.events[1].weapon_id, "sword", "adjacent ranged combatant switches to its legal melee option");

console.log("Fixed frontline/backline battlefield policy and browser turn AI regressions passed.");
