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


// Source-parameterized saving-throw reaction: success zeroes hit,
// failure spends Reaction but leaves the original components intact.
{
  const rule = { sourceId: "catch-projectile", sourceName: "Catch Projectile",
    attackKinds: ["ranged"], requiredDamageTypes: [],
    negateOnSaveAbility: "dexterity", negateOnSaveDc: 10 };
  window.IRON_PIT_BROWSER_SAVING_THROWS = {
    resolveSavingThrow: (_state, ability, dc) => {
      assert.equal(ability, "dexterity");
      assert.equal(dc, 10);
      return { succeeded: true };
    },
  };
  const defender = state(rule);
  const result = window.IRON_PIT_BROWSER_ATTACK_DAMAGE_REDUCTION.apply(
    defender, { kind: "ranged" }, [{ source: "rock", damage_type: "bludgeoning", total: 23 }],
  );
  assert.equal(result.used, true);
  assert.equal(result.zeroedAttack, true);
  assert.equal(result.components[0].total, 0);
  assert.equal(defender.reaction_available, false);
}
{
  const rule = { sourceId: "catch-projectile", sourceName: "Catch Projectile",
    attackKinds: ["ranged"], requiredDamageTypes: [],
    negateOnSaveAbility: "dexterity", negateOnSaveDc: 10 };
  window.IRON_PIT_BROWSER_SAVING_THROWS = {
    resolveSavingThrow: () => ({ succeeded: false }),
  };
  const defender = state(rule);
  const parts = [{ source: "rock", damage_type: "bludgeoning", total: 23 }];
  const result = window.IRON_PIT_BROWSER_ATTACK_DAMAGE_REDUCTION.apply(
    defender, { kind: "ranged" }, parts,
  );
  assert.equal(result.used, true);
  assert.equal(result.zeroedAttack, false);
  assert.deepEqual(result.components, parts);
  assert.equal(defender.reaction_available, false);
}


{
  const rule = { sourceId: "rock-catching", sourceName: "Rock Catching",
    attackKinds: ["ranged"], requiredDamageTypes: ["bludgeoning"],
    requiredAttackQualifiers: ["hurled-object"], negateOnSaveDamageTypes: ["bludgeoning"],
    negateOnSaveAbility: "dexterity", negateOnSaveDc: 10 };
  window.IRON_PIT_BROWSER_SAVING_THROWS = {
    resolveSavingThrow: () => ({ succeeded: true }),
  };
  const arrowDefender = state(rule);
  const arrow = window.IRON_PIT_BROWSER_ATTACK_DAMAGE_REDUCTION.apply(
    arrowDefender, { kind: "ranged", name: "Longbow", damageSourceQualifiers: [] },
    [{ source: "arrow", damage_type: "piercing", total: 12 }],
  );
  assert.equal(arrow.used, false);
  assert.equal(arrowDefender.reaction_available, true);
  const rockDefender = state(rule);
  const rock = window.IRON_PIT_BROWSER_ATTACK_DAMAGE_REDUCTION.apply(
    rockDefender, { kind: "ranged", name: "Rock", damageSourceQualifiers: ["hurled-object"] },
    [{ source: "rock", damage_type: "bludgeoning", total: 22 }, { source: "fire", damage_type: "fire", total: 5 }],
  );
  assert.equal(rock.used, true);
  assert.equal(rock.zeroedAttack, false);
  assert.deepEqual(rock.components.map((part) => part.total), [0, 5]);
  assert.equal(rockDefender.reaction_available, false);
}

console.log("Universal browser attack damage reduction regressions passed.");
