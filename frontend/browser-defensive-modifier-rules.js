(() => {
  "use strict";

  const baseType = (template) => String(template?.creature_type || "").split(" (")[0].trim().toLowerCase();
  const sourceMatches = (item, template) => {
    const types = item.source_creature_types || [];
    return !types.length || types.map((value) => value.toLowerCase()).includes(baseType(template));
  };
  const attacksAgainstDisadvantage = (state, attackerTemplate) => (state.active_modifiers || [])
    .filter((item) => item.kind === "attacks-against-disadvantage" && sourceMatches(item, attackerTemplate)).length;
  const saveAdvantage = (state, ability) => (state.active_modifiers || [])
    .filter((item) => item.kind === "saving-throw-advantage" && item.save_ability === ability).length;
  const saveDisadvantage = (state) => (state.active_modifiers || [])
    .filter((item) => item.kind === "saving-throw-disadvantage").length;

  function consumeSavingThrowModifiers(state) {
    const removed = (state.active_modifiers || [])
      .filter((item) => item.kind === "saving-throw-disadvantage" && item.consume_on_saving_throw)
      .map((item) => item.source_effect_id);
    state.active_modifiers = (state.active_modifiers || [])
      .filter((item) => !(item.kind === "saving-throw-disadvantage" && item.consume_on_saving_throw));
    return [...new Set(removed)].sort();
  }
  const deathSaveAdvantage = (state) => (state.active_modifiers || [])
    .some((item) => item.kind === "death-save-advantage");
  const deathSaveNat20Threshold = (state) => {
    const thresholds = (state.active_modifiers || [])
      .filter((item) => item.kind === "death-save-nat20-threshold")
      .map((item) => item.flat_bonus);
    return thresholds.length ? Math.min(...thresholds) : 20;
  };
  const healingMaximized = (state) => (state.active_modifiers || [])
    .some((item) => item.kind === "healing-maximize");
  const conditionImmune = (state, conditionId, sourceTemplate = null) => (state.active_modifiers || [])
    .some((item) => item.kind === "condition-immunity" && item.condition_id === conditionId
      && sourceMatches(item, sourceTemplate));
  const targetingGate = (state) => (state.active_modifiers || [])
    .filter((item) => item.kind === "targeting-save-gate")
    .sort((a, b) => (b.save_dc || 0) - (a.save_dc || 0) || a.id.localeCompare(b.id))[0] || null;

  function removeOwnerAttackEnding(state) {
    const removed = (state.active_modifiers || []).filter((item) => item.ends_on_owner_attack)
      .map((item) => item.source_effect_id);
    state.active_modifiers = (state.active_modifiers || []).filter((item) => !item.ends_on_owner_attack);
    return [...new Set(removed)].sort();
  }

  window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = {
    attacksAgainstDisadvantage, conditionImmune, consumeSavingThrowModifiers, deathSaveAdvantage,
    deathSaveNat20Threshold, healingMaximized, removeOwnerAttackEnding, saveAdvantage, saveDisadvantage, targetingGate,
  };
})();