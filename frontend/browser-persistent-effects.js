(() => {
  "use strict";

  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const V = () => window.IRON_PIT_BROWSER_SAVES;

  function gatePasses(target, gate = {}) {
    const tags = new Set((target.state.template.creature_tags || []).map((tag) => String(tag).toLowerCase()));
    const creatureType = String(target.state.template.creature_type || "").toLowerCase();
    if ((gate.requiredTargetTags || []).some((tag) => !tags.has(String(tag).toLowerCase()))) return false;
    if ((gate.excludedTargetTags || []).some((tag) => tags.has(String(tag).toLowerCase()))) return false;
    if (creatureType && (gate.excludedCreatureTypes || []).some((item) => String(item).toLowerCase() === creatureType)) return false;
    if (!gate.saveAbility) return true;
    if (!V()?.resolveSavingThrow) throw new Error("Save-gated effect requires the browser saving-throw resolver.");
    return !V().resolveSavingThrow(target.state, gate.saveAbility, gate.saveDc).succeeded;
  }

  function apply(target, effects, sourceId, sourceEffectId, range, round) {
    if (!target?.state?.is_alive || target.state.is_dead) return [];
    const applied = [];
    for (const effect of effects || []) {
      if (effect.maxTargetSize && !S().sizeAtMost(target, effect.maxTargetSize)) continue;
      if (!gatePasses(target, effect.gate)) continue;
      if (effect.grappleEscapeDc) {
        applied.push(...G().apply(target.state, sourceId, effect.grappleEscapeDc, range, Boolean(effect.restrainsWhileGrappled)));
      }
      if (!effect.conditionId || I().immune(target.state, effect.conditionId)) continue;
      if (effect.conditionId === "prone") {
        if (!target.state.active_effect_ids.includes("prone")) target.state.active_effect_ids.push("prone");
        applied.push("prone");
        continue;
      }
      const condition = T().apply(target.state, effect.conditionId, sourceId, {
        sourceEffectId,
        appliedRound: round,
        expiresAtStartOfSourceTurn: Boolean(effect.expiresAtStartOfSourceTurn),
        expiryTiming: effect.expiryTiming || null,
        repeatSaveAbility: effect.repeatSaveAbility || null,
        repeatSaveDc: effect.repeatSaveDc || null,
        repeatSaveTiming: effect.repeatSaveTiming || null,
        allowedRemovalActionIds: effect.allowedRemovalActionIds || [],
      });
      if (condition) applied.push(condition);
    }
    return [...new Set(applied)];
  }

  window.IRON_PIT_BROWSER_PERSISTENT_EFFECTS = { apply, gatePasses };
})();
