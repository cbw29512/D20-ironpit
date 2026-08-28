"use strict";

const { chipText, updateEffectStore } = require("../frontend/effects-view.js");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

try {
  const store = new Map();
  const actor = "fighter";
  const sap = {
    actor_id: actor, effect_id: "sap:enemy:any", operation: "apply",
    kind: "debuff", label: "Sap",
  };
  const vex = {
    actor_id: actor, effect_id: "vex:fighter:goblin", operation: "apply",
    kind: "buff", label: "Vex",
  };

  updateEffectStore(store, [sap, vex]);
  assert(store.get(actor).size === 2, "A combat card must support multiple simultaneous effects.");
  assert(chipText(sap) === "DEBUFF · Sap", "Debuffs must be labeled explicitly.");
  assert(chipText(vex) === "BUFF · Vex", "Buffs must be labeled explicitly.");

  updateEffectStore(store, [{ actor_id: actor, effect_id: sap.effect_id, operation: "remove" }]);
  assert(store.get(actor).size === 1, "Removing one effect must not remove unrelated effects.");
  assert(store.get(actor).has(vex.effect_id), "Unrelated buffs must remain on the card.");

  updateEffectStore(store, [{
    actor_id: "goblin", effect_id: "restrained", operation: "apply",
    kind: "debuff", label: "Restrained",
  }]);
  assert(store.get("goblin").size === 1, "Effects must remain isolated by combatant.");

  console.log("Combat-card buff/debuff checks passed.");
} catch (error) {
  console.error("Combat-card effect checks failed", error);
  process.exitCode = 1;
}
