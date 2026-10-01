"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false };
window.IRON_PIT_BROWSER_TIMED = {
  suppressesAction: () => false,
  suppressesBonusAction: () => false,
  suppressesReactions: () => false,
};
load("browser-action-economy.js");
load("browser-attack-damage-reduction.js");

const state = (rule) => ({
  template: {
    name: "Defender",
    level: 3,
    ability_scores: { strength: 10, dexterity: 17, constitution: 10, intelligence: 10, wisdom: 10, charisma: 10 },
    attackDamageReductionReaction: rule,
  },
  current_hp: 24,
  is_dead: false,
  is_unconscious: false,
  reaction_available: true,
  turn_terminated: false,
});

const rule2024 = {
  sourceId: "deflect-attacks",
  sourceName: "Deflect Attacks",
  attackKinds: ["melee", "ranged"],
  requiredDamageTypes: ["bludgeoning", "piercing", "slashing"],
  reductionDiceCount: 1,
  reductionDiceSize: 10,
  reductionAbility: "dexterity",
  addLevel: true,
};

{
  window.IRON_PIT_DICE = { roll: () => 4 };
  const defender = state(rule2024);
  const result = window.IRON_PIT_BROWSER_ATTACK_DAMAGE_REDUCTION.apply(
    defender,
    { kind: "melee" },
    [{ source: "club", damage_type: "bludgeoning", total: 12 }],
  );
  assert.equal(result.used, true);
  assert.equal(result.reduction, 10);
  assert.equal(result.sourceId, "deflect-attacks");
  assert.equal(result.sourceName, "Deflect Attacks");
  assert.equal(result.components[0].total, 2);
  assert.equal(defender.reaction_available, false);
}

{
  window.IRON_PIT_DICE = { roll: () => { throw new Error("Fire-only damage must not roll reduction."); } };
  const defender = state(rule2024);
  const result = window.IRON_PIT_BROWSER_ATTACK_DAMAGE_REDUCTION.apply(
    defender,
    { kind: "ranged" },
    [{ source: "fire bolt", damage_type: "fire", total: 12 }],
  );
  assert.equal(result.used, false);
  assert.equal(result.components[0].total, 12);
  assert.equal(defender.reaction_available, true);
}

{
  window.IRON_PIT_DICE = { roll: () => 4 };
  const defender = state(rule2024);
  const result = window.IRON_PIT_BROWSER_ATTACK_DAMAGE_REDUCTION.apply(
    defender,
    { kind: "ranged" },
    [
      { source: "arrow", damage_type: "piercing", total: 4 },
      { source: "flame", damage_type: "fire", total: 8 },
    ],
  );
  assert.equal(result.used, true);
  assert.deepEqual(result.components.map((part) => part.total), [0, 2]);
}

{
  const legacy = state({
    sourceId: "deflect-missiles",
    sourceName: "Deflect Missiles",
    attackKinds: ["ranged"],
    requiredDamageTypes: [],
    reductionDiceCount: 1,
    reductionDiceSize: 10,
    reductionAbility: "dexterity",
    addLevel: true,
  });
  window.IRON_PIT_DICE = { roll: () => 4 };
  const melee = window.IRON_PIT_BROWSER_ATTACK_DAMAGE_REDUCTION.apply(
    legacy, { kind: "melee" }, [{ source: "sword", damage_type: "slashing", total: 8 }],
  );
  assert.equal(melee.used, false);
  const ranged = window.IRON_PIT_BROWSER_ATTACK_DAMAGE_REDUCTION.apply(
    legacy, { kind: "ranged" }, [{ source: "arrow", damage_type: "piercing", total: 8 }],
  );
  assert.equal(ranged.used, true);
  assert.equal(ranged.sourceId, "deflect-missiles");
}

{
  const defender = state(rule2024);
  defender.reaction_available = false;
  window.IRON_PIT_DICE = { roll: () => { throw new Error("Unavailable Reaction must not roll."); } };
  const result = window.IRON_PIT_BROWSER_ATTACK_DAMAGE_REDUCTION.apply(
    defender, { kind: "melee" }, [{ source: "club", damage_type: "bludgeoning", total: 8 }],
  );
  assert.equal(result.used, false);
}

console.log("Universal browser attack damage reduction regressions passed.");
