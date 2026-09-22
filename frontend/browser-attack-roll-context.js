(() => {
  "use strict";

  function create({ baseAdvantageSources = 0, baseDisadvantageSources = 0, rangeDisadvantage = false } = {}) {
    for (const [name, value] of Object.entries({ baseAdvantageSources, baseDisadvantageSources })) {
      if (!Number.isFinite(value) || value < 0) throw new Error(`Attack-roll context requires non-negative ${name}.`);
    }
    return {
      baseAdvantageSources, baseDisadvantageSources, rangeDisadvantage: Boolean(rangeDisadvantage),
      advantageSources: {}, disadvantageSources: {}, descriptionFragments: [], aggregateFeatureId: null,
    };
  }

  function requireContext(ctx) {
    const state = ctx?.attackRollContext;
    if (!state || typeof state !== "object" || Array.isArray(state)) {
      throw new Error("Before-attack-roll hook requires a mutable attackRollContext object.");
    }
    for (const key of ["baseAdvantageSources", "baseDisadvantageSources"]) {
      if (!Number.isFinite(state[key]) || state[key] < 0) throw new Error(`Attack-roll context ${key} is invalid.`);
    }
    if (typeof state.rangeDisadvantage !== "boolean"
        || !state.advantageSources || !state.disadvantageSources
        || Array.isArray(state.advantageSources) || Array.isArray(state.disadvantageSources)
        || !Array.isArray(state.descriptionFragments)) {
      throw new Error("Attack-roll context source state is invalid.");
    }
    return state;
  }

  function setSource(map, sourceId, value, kind) {
    if (typeof sourceId !== "string" || !sourceId.trim()) throw new Error(`Attack-roll ${kind} source requires a stable id.`);
    if (!Number.isFinite(value) || value < 0) throw new Error(`Attack-roll ${kind} source ${sourceId} must be non-negative.`);
    map[sourceId] = value;
  }
  const sum = (map) => Object.values(map).reduce((total, value) => {
    if (!Number.isFinite(value) || value < 0) throw new Error("Attack-roll source map is invalid.");
    return total + value;
  }, 0);
  const advantageSource = (state, id) => Number(state.advantageSources[id] || 0);
  const disadvantageSource = (state, id) => Number(state.disadvantageSources[id] || 0);
  const advantageTotal = (state) => state.baseAdvantageSources + sum(state.advantageSources);
  const disadvantageTotal = (state) => state.baseDisadvantageSources + sum(state.disadvantageSources) + Number(state.rangeDisadvantage);
  const setAdvantageSource = (state, id, value) => setSource(state.advantageSources, id, value, "Advantage");
  const setDisadvantageSource = (state, id, value) => setSource(state.disadvantageSources, id, value, "Disadvantage");
  function noEventResult(sequence) {
    if (!Number.isInteger(sequence) || sequence < 0) throw new Error("Before-attack-roll hook requires a valid sequence.");
    return { events: [], sequence, claimed: false };
  }

  window.IRON_PIT_BROWSER_ATTACK_ROLL_CONTEXT = {
    advantageSource, advantageTotal, create, disadvantageSource, disadvantageTotal, noEventResult,
    requireContext, setAdvantageSource, setDisadvantageSource,
  };
})();