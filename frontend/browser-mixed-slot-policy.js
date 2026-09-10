(() => {
  "use strict";

  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const MODIFIER_KINDS = new Set(["attacks-against-advantage", "speed"]);
  const sizeAllowed = (target, maximum) => !maximum || S().sizeAtMost(target, maximum);

  function conditionIsNew(member, target, action, effect) {
    if (!sizeAllowed(target, effect.maxTargetSize) || I().immune(target.state, effect.condition)) return false;
    if (!target.state.active_effect_ids.includes(effect.condition)) return true;
    return !(target.state.timed_effects || []).some((timed) =>
      timed.effect_id === effect.condition
      && timed.source_id === member.combatant_id
      && timed.source_effect_id === action.id);
  }

  function effectIsNew(member, target, action, effect) {
    if (effect.kind === "prone") {
      return sizeAllowed(target, effect.maxTargetSize)
        && !target.state.active_effect_ids.includes("prone")
        && !I().immune(target.state, "prone");
    }
    if (effect.kind === "grapple") {
      return sizeAllowed(target, effect.maxTargetSize)
        && !(target.state.grapple_sources || []).some((source) => source.source_id === member.combatant_id);
    }
    if (effect.kind === "condition") return conditionIsNew(member, target, action, effect);
    if (MODIFIER_KINDS.has(effect.kind)) {
      return !(target.state.active_modifiers || []).some((modifier) =>
        modifier.source_id === member.combatant_id && modifier.source_effect_id === action.id);
    }
    throw new Error(`Unsupported mixed-slot failed-save effect: ${effect.kind}.`);
  }

  function preferSaveReplacement(member, target, action) {
    if ((action.failureEffects || []).some((effect) => effectIsNew(member, target, action, effect))) return true;
    if (action.grappleEscapeDc != null) {
      return !(target.state.grapple_sources || []).some((source) => source.source_id === member.combatant_id);
    }
    return false;
  }

  window.IRON_PIT_BROWSER_MIXED_SLOT_POLICY = { preferSaveReplacement };
})();
