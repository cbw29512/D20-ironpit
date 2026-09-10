(() => {
  "use strict";

  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const MODIFIER_KINDS = new Set(["attacks-against-advantage", "speed"]);

  const sizeAllowed = (target, maximum) => !maximum || S().sizeAtMost(target, maximum);

  function apply(target, sourceId, sourceEffectId, effects, options = {}) {
    if (target.state.is_dead || !target.state.is_alive) return [];
    const applied = [];
    for (const [index, effect] of (effects || []).entries()) {
      if (effect.kind === "prone") {
        if (sizeAllowed(target, effect.maxTargetSize) && !I().immune(target.state, "prone")) {
          if (!target.state.active_effect_ids.includes("prone")) target.state.active_effect_ids.push("prone");
          applied.push("prone");
        }
      } else if (effect.kind === "grapple") {
        if (sizeAllowed(target, effect.maxTargetSize)) {
          applied.push(...G().apply(target.state, sourceId, effect.escapeDc, options.range || 0, Boolean(effect.restrains)));
        }
      } else if (effect.kind === "condition") {
        if (!sizeAllowed(target, effect.maxTargetSize)) continue;
        const condition = T().apply(target.state, effect.condition, sourceId, {
          sourceEffectId, appliedRound: options.round,
          expiresAtStartOfSourceTurn: Boolean(effect.expiresAtStartOfSourceTurn),
          expiryTiming: effect.expiryTiming || null,
          repeatSaveAbility: effect.repeatSaveAbility || null,
          repeatSaveDc: effect.repeatSaveDc || null,
          repeatSaveTiming: effect.repeatSaveTiming || null,
          repeatSaveDelayRounds: effect.repeatSaveDelayRounds || 0,
          allowedRemovalActionIds: effect.allowedRemovalActionIds || [],
        });
        if (condition) applied.push(condition);
      } else if (MODIFIER_KINDS.has(effect.kind)) {
        M().applyEffect(target.state, sourceId, sourceEffectId, effect, index, "failed-save");
      } else {
        throw new Error(`Unsupported failed-save effect kind: ${effect.kind}.`);
      }
    }
    return [...new Set(applied)];
  }

  window.IRON_PIT_BROWSER_SAVE_FAILURE_EFFECTS = { apply };
})();
