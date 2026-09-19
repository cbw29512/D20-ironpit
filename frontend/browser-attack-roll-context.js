(() => {
  "use strict";

  function create({ baseDisadvantageSources = 0, rangedDisadvantage = false } = {}) {
    if (!Number.isFinite(baseDisadvantageSources) || baseDisadvantageSources < 0) {
      throw new Error("Attack-roll context requires non-negative base Disadvantage sources.");
    }
    return {
      baseDisadvantageSources,
      rangedDisadvantage: Boolean(rangedDisadvantage),
      recklessStarted: false,
      recklessAdvantage: 0,
      brutalStrikeSuppression: 0,
      bloodiedFuryAdvantage: 0,
    };
  }

  function requireContext(ctx) {
    const state = ctx?.attackRollContext;
    if (!state || typeof state !== "object" || Array.isArray(state)) {
      throw new Error("Before-attack-roll hook requires a mutable attackRollContext object.");
    }
    for (const field of [
      "baseDisadvantageSources", "recklessAdvantage",
      "brutalStrikeSuppression", "bloodiedFuryAdvantage",
    ]) {
      if (!Number.isFinite(state[field]) || state[field] < 0) {
        throw new Error(`Attack-roll context field ${field} must be a non-negative number.`);
      }
    }
    if (typeof state.rangedDisadvantage !== "boolean" || typeof state.recklessStarted !== "boolean") {
      throw new Error("Attack-roll context boolean fields are invalid.");
    }
    return state;
  }

  function noEventResult(sequence) {
    if (!Number.isInteger(sequence) || sequence < 0) {
      throw new Error("Before-attack-roll hook requires a valid sequence.");
    }
    return { events: [], sequence, claimed: false };
  }

  window.IRON_PIT_BROWSER_ATTACK_ROLL_CONTEXT = { create, noEventResult, requireContext };
})();