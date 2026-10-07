(() => {
  "use strict";

  const WAKE_SLEEPER_ACTION = {
    id: "wake-sleeper", name: "Wake Sleeper", actionCost: "action", range: 5,
    targetMode: "ally", removableConditions: ["unconscious"], maxConditionsPerUse: 1,
    resourceCosts: {}, resourceCostsPerCondition: {}, expendsSpellSlot: false,
    requiresExplicitEffectPermission: true, animation: "condition-removal",
  };

  function actions(templateActions = []) {
    return [WAKE_SLEEPER_ACTION, ...templateActions];
  }

  function effectAllows(target, conditionId, action) {
    const effects = target.state.timed_effects.filter((effect) => effect.effect_id === conditionId);
    if (action.requiresExplicitEffectPermission) {
      return effects.length > 0 && effects.every((effect) =>
        (effect.allowed_removal_action_ids || []).includes(action.id),
      );
    }
    return effects.every((effect) =>
      !effect.allowed_removal_action_ids?.length || effect.allowed_removal_action_ids.includes(action.id),
    );
  }

  window.IRON_PIT_BROWSER_CONDITION_REMOVAL_POLICY = { actions, effectAllows };
})();
