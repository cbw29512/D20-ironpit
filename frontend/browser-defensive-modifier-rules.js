(() => {
  "use strict";

  const baseType = (template) => String(template?.creature_type || "").split(" (")[0].trim().toLowerCase();
  const sourceMatches = (item, template) => {
    const types = item.source_creature_types || [];
    return !types.length || types.map((value) => value.toLowerCase()).includes(baseType(template));
  };
  const attacksAgainstDisadvantage = (state, attackerTemplate) => (state.active_modifiers || [])
    .filter((item) => item.kind === "attacks-against-disadvantage" && sourceMatches(item, attackerTemplate)).length;
  function saveAdvantageModifiers(state, ability, context = {}) {
    try {
      const contextTags = new Set(
        (context.effectTags || []).map((tag) => String(tag).trim().toLowerCase()).filter(Boolean),
      );
      return (state.active_modifiers || []).filter((item) =>
        item.kind === "saving-throw-advantage"
        && item.save_ability === ability
        && (!item.requires_magical_effect || Boolean(context.magicalEffect))
        && (!item.requires_spell_effect || Boolean(context.spellEffect))
        && (item.required_effect_tags || []).every((tag) =>
          contextTags.has(String(tag).trim().toLowerCase()))
        && (
          !(item.source_creature_types || []).length
          || (item.source_creature_types || []).map((value) => value.toLowerCase())
            .includes(String(context.sourceCreatureType || "").split(" (")[0].trim().toLowerCase())
        ));
    } catch (error) {
      console.error("Failed to resolve browser saving-throw Advantage sources", {
        error, combatant: state?.template?.name, ability,
      });
      throw error;
    }
  }
  const saveAdvantage = (state, ability, context = {}) =>
    saveAdvantageModifiers(state, ability, context).length;
  function saveAdvantageSourceNames(state, ability, context = {}) {
    try {
      return [...new Set(saveAdvantageModifiers(state, ability, context)
        .map((item) => item.source_name || item.source_effect_id))].sort();
    } catch (error) {
      console.error("Failed to identify browser saving-throw Advantage sources", {
        error, combatant: state?.template?.name, ability,
      });
      throw error;
    }
  }
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
    attacksAgainstDisadvantage, conditionImmune, consumeSavingThrowModifiers, deathSaveAdvantage, healingMaximized,
    removeOwnerAttackEnding, saveAdvantage, saveAdvantageSourceNames, saveDisadvantage, targetingGate,
  };
})();