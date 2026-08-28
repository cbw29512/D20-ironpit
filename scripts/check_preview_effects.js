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

  const fighter = { attackRollEffects: [] };
  const goblin = { attackRollEffects: [] };
  effects.applySap(goblin, "fighter");
  assert(goblin.attackRollEffects.length === 1, "Sap should create one temporary effect.");
  effects.consumeAttackEffects(goblin);
  assert(goblin.attackRollEffects.length === 0, "Sap should end after the next attack roll.");

  effects.applySap(goblin, "fighter");
  effects.expireAtSourceTurn([fighter, goblin], "fighter");
  assert(goblin.attackRollEffects.length === 0, "Unused Sap should expire at source turn start.");

  console.log("Preview Sap effect checks passed.");
} catch (error) {
  console.error("Preview Sap effect checks failed", error);
  process.exitCode = 1;
}
