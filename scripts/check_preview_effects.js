"use strict";

const effects = require("../frontend/preview-effects.js");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

try {
  assert(
    effects.resolveRollMode("normal", [{ kind: "disadvantage" }]) === "disadvantage",
    "Sap must impose Disadvantage on a normal attack roll.",
  );
  assert(
    effects.resolveRollMode("advantage", [{ kind: "disadvantage" }]) === "normal",
    "Advantage and Sap Disadvantage must cancel to a normal roll.",
  );

  const fighter = { template: { id: "fighter", weapon_masteries: [] }, attackRollEffects: [] };
  const goblin = { template: { id: "goblin", weapon_masteries: [] }, attackRollEffects: [] };
  effects.applySap(goblin, "fighter");
  assert(goblin.attackRollEffects.length === 1, "Sap should create one temporary effect.");
  effects.consumeAttackEffects(goblin, "fighter");
  assert(goblin.attackRollEffects.length === 0, "Sap should end after the next attack roll.");

  effects.applySap(goblin, "fighter");
  effects.expireAtSourceTurn([fighter, goblin], "fighter");
  assert(goblin.attackRollEffects.length === 0, "Unused Sap should expire at source turn start.");

  const archer = { template: { id: "archer", weapon_masteries: ["shortbow"] }, attackRollEffects: [] };
  effects.applyVex(archer, "archer", "goblin");
  assert(
    effects.resolveRollMode("normal", archer.attackRollEffects, "goblin") === "advantage",
    "Vex should grant Advantage against the creature that was hit.",
  );
  assert(
    effects.resolveRollMode("normal", archer.attackRollEffects, "other") === "normal",
    "Vex should not grant Advantage against a different target.",
  );
  effects.consumeAttackEffects(archer, "other");
  assert(archer.attackRollEffects.length === 1, "Attacking another target should not consume Vex.");
  effects.consumeAttackEffects(archer, "goblin");
  assert(archer.attackRollEffects.length === 0, "Vex should end after the matching attack roll.");

  effects.applyVex(archer, "archer", "goblin");
  effects.endSourceTurn([archer, goblin], "archer");
  assert(archer.attackRollEffects[0].source_turns_remaining === 1, "Vex should survive its source turn.");
  effects.endSourceTurn([archer, goblin], "archer");
  assert(archer.attackRollEffects.length === 0, "Unused Vex should expire at end of next turn.");

  console.log("Preview Sap/Vex effect checks passed.");
} catch (error) {
  console.error("Preview combat effect checks failed", error);
  process.exitCode = 1;
}
