(() => {
  "use strict";

  function emptyTopple() {
    return { saveRoll: null, saveDc: null, saveSucceeded: null, applied: false };
  }

  function create() {
    return {
      damageRoll: null,
      damageComponents: [],
      damageOutcome: null,
      hitSave: null,
      saveDamage: null,
      topple: emptyTopple(),
      sapApplied: "",
      vexApplied: false,
      studiedApplied: false,
      appliedConditions: [],
    };
  }

  function requireOutcome(ctx) {
    const outcome = ctx?.attackOutcome;
    if (!outcome || typeof outcome !== "object" || Array.isArray(outcome)) {
      throw new Error("Attack outcome hook requires a mutable attackOutcome object.");
    }
    if (!Array.isArray(outcome.damageComponents) || !Array.isArray(outcome.appliedConditions)) {
      throw new Error("Attack outcome accumulator has an invalid schema.");
    }
    if (!outcome.topple || typeof outcome.topple !== "object") {
      throw new Error("Attack outcome accumulator requires Topple state.");
    }
    return outcome;
  }

  function noEventResult(sequence) {
    if (!Number.isInteger(sequence) || sequence < 0) throw new Error("Attack outcome hook requires a valid sequence.");
    return { events: [], sequence, claimed: false };
  }

  window.IRON_PIT_BROWSER_ATTACK_OUTCOME = { create, emptyTopple, noEventResult, requireOutcome };
})();
