"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
require("./browser-test-runtime.cjs").loadWebsite();

function execute(kind, label) {
  const source = kind === "monster"
    ? window.IRON_PIT_BROWSER_MONSTERS["srd-goblin-warrior"]
    : window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
  const template = structuredClone(source);
  template.id = "synthetic-attacker";
  template.kind = kind;
  template.name = "Synthetic";
  template.attacks = [{
    id: "synthetic-claw", name: label, kind: "melee",
    bonus: 5, diceCount: 2, diceSize: 6, damageBonus: 2,
    damageType: "bludgeoning", reach: 5, animation: "slash",
  }];
  template.primary_attack_id = "synthetic-claw";
  template.weapon_masteries = [];
  template.traits = [];
  const targetTemplate = structuredClone(window.IRON_PIT_BROWSER_MONSTERS["srd-goblin-warrior"]);
  targetTemplate.id = "synthetic-target";
  targetTemplate.armor_class = 10;
  targetTemplate.max_hp = 100;
  const attacker = {combatant_id: "attacker", side: kind === "monster" ? "monsters" : "heroes",
    position_ft: 0, state: window.IRON_PIT_BROWSER_STATE.buildState(template)};
  const target = {combatant_id: "target", side: "monsters", position_ft: 5,
    state: window.IRON_PIT_BROWSER_STATE.buildState(targetTemplate)};
  const rolls = [15, 4, 5];
  window.IRON_PIT_DICE = {
    roll(sides) { const v = rolls.shift(); assert.ok(v >= 1 && v <= sides); return v; },
    rollMany(count, sides) { return Array.from({length: count}, () => this.roll(sides)); },
  };
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(
    1, 1, attacker, target, template.attacks[0], 5, {spendAction: false},
  );
  return {hit: event.hit, damage: event.damage_roll.total, hp: target.state.current_hp};
}

test("renamed monster and character attacks use identical browser combat rules", () => {
  assert.deepEqual(execute("monster", "Tail"), execute("character", "Imaginary Coil"));
});
