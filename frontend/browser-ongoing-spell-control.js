(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function forcedRetreatActive(state) {
    return (state.timed_effects || []).some((effect) => effect.turn_behavior === "forced_retreat");
  }

  function apply(targetState, conditionId, sourceId, spellId, saveAbility, saveDc, options = {}) {
    if (!spellId) throw new Error("Ongoing spell control requires a spell id.");
    if (!(saveDc > 0)) throw new Error("Ongoing spell control requires a valid save DC.");
    return T().apply(targetState, conditionId, sourceId, {
      sourceEffectId: spellId,
      appliedRound: options.appliedRound,
      expiryTiming: options.expiryTiming || null,
      repeatSaveAbility: saveAbility,
      repeatSaveDc: saveDc,
      repeatSaveTiming: "target_turn_end",
      allowedRemovalActionIds: options.allowedRemovalActionIds || [],
      turnBehavior: options.turnBehavior || "normal",
    });
  }

  window.IRON_PIT_BROWSER_ONGOING_SPELL_CONTROL = { apply, forcedRetreatActive };
})();
