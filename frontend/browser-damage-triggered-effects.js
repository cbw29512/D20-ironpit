(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function apply(state, amount, damageTypes = []) {
    if (amount <= 0 || !damageTypes.length) return [];
    if (!T()) throw new Error("Browser timed-effect runtime is not loaded.");
    const types = new Set(damageTypes), applied = [];
    for (const profile of state.template.damageTriggeredRollPenalties || []) {
      if (!(profile.damageTypes || []).some((type) => types.has(type))) continue;
      const effect = T().apply(state, profile.id, profile.id, {
        sourceEffectId: profile.id,
        disadvantageAttackRolls: Boolean(profile.attackRollDisadvantage),
        disadvantageAbilityChecks: Boolean(profile.abilityCheckDisadvantage),
        expiresAfterNextTargetTurn: profile.expiresAfterNextTargetTurn !== false,
      });
      if (effect) applied.push(effect);
    }
    return applied;
  }

  window.IRON_PIT_BROWSER_DAMAGE_TRIGGERED_EFFECTS = { apply };
})();
