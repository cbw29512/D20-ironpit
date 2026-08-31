"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of ["browser-condition-immunity.js", "browser-condition-rules.js", "browser-grapple.js", "browser-state.js", "browser-formation.js"]) load(file);

const F = window.IRON_PIT_BROWSER_FORMATION;
const S = window.IRON_PIT_BROWSER_STATE;
const melee = { kind: "character", primary_attack_id: "blade", attacks: [{ id: "blade", kind: "melee" }] };
const ranged = { kind: "character", primary_attack_id: "bow", attacks: [{ id: "bow", kind: "ranged" }] };
const caster = { kind: "character", primary_attack_id: "staff", attacks: [{ id: "staff", kind: "melee" }], spell_save_actions: [{}] };

assert.equal(F.startingPosition(melee, "heroes"), 5);
assert.equal(F.startingPosition(melee, "monsters"), 10);
assert.equal(F.startingPosition(ranged, "heroes"), 0);
assert.equal(F.startingPosition(ranged, "monsters"), 15);
assert.equal(F.startingPosition(caster, "heroes"), 0);

function member(id, side, position, kind = "monster") {
  return {
    combatant_id: id,
    side,
    position_ft: position,
    state: {
      template: { kind, size: "medium" }, current_hp: 10, is_alive: true, is_dead: false,
      is_unconscious: false, active_effect_ids: [], grapple_sources: [],
    },
  };
}

const heroFront = member("hero-front", "heroes", 5, "character");
const heroBack = member("hero-back", "heroes", 0, "character");
const monsterFront = member("monster-front", "monsters", 10);
const monsterBack = member("monster-back", "monsters", 15);
const setup = { heroes: [heroFront, heroBack], monsters: [monsterFront, monsterBack] };

assert.equal(S.nearestTarget(heroBack, setup).combatant_id, "monster-front", "backline attacks the active enemy frontline first");
assert.equal(S.nearestTarget(monsterBack, setup).combatant_id, "hero-front", "enemy backline attacks the active hero frontline first");
assert.equal(S.nearestTarget(monsterFront, setup).combatant_id, "hero-front", "frontlines begin engaged with each other");

heroFront.state.current_hp = 0;
heroFront.state.is_alive = false;
heroFront.state.is_dead = true;
assert.equal(S.nearestTarget(monsterFront, setup).combatant_id, "hero-back", "backline becomes the target after its frontline falls");

console.log("Fixed frontline/backline battlefield policy regressions passed.");
