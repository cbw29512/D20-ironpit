(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_SAVES;
  const ST = () => window.IRON_PIT_BROWSER_STATE;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };

  function resolve(target, attack) {
    const effect = attack.onHitSaveEffect;
    if (!effect || !target.state.is_alive || target.state.is_dead) {
      return { saveRoll: null, saveAbility: null, saveDc: null, saveSucceeded: null, appliedCondition: null };
    }
    if (effect.maxTargetSize && !ST().sizeAtMost(target, effect.maxTargetSize)) {
      return { saveRoll: null, saveAbility: null, saveDc: null, saveSucceeded: null, appliedCondition: null };
    }
    if (!S()) throw new Error("Browser saving-throw runtime is not loaded.");
    const save = S().resolveSavingThrow(target.state, effect.saveAbility, effect.dc);
    let appliedCondition = null;
    if (!save.succeeded && !I().immune(target.state, effect.conditionId)) {
      if (!target.state.active_effect_ids.includes(effect.conditionId)) target.state.active_effect_ids.push(effect.conditionId);
      appliedCondition = effect.conditionId;
    }
    return {
      saveRoll: save.roll,
      saveAbility: effect.saveAbility,
      saveDc: effect.dc,
      saveSucceeded: save.succeeded,
      appliedCondition,
    };
  }

  window.IRON_PIT_BROWSER_ON_HIT_SAVES = { resolve };
})();
