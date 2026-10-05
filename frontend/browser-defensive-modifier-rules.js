(() => {
  "use strict";

  const baseType = (template) => String(template?.creature_type || "").split(" (")[0].trim().toLowerCase();
  const sourceMatches = (item, template) => {
    const types = item.source_creature_types || [];
    return !types.length || types.map((value) => value.toLowerCase()).includes(baseType(template));
  };
  const asSenseObserver = (attacker) => {
    if (attacker && attacker.template && Array.isArray(attacker.active_effect_ids)) return attacker;
    if (attacker && Array.isArray(attacker.active_effect_ids)) return attacker;
    return {
      template: attacker || {},
      active_effect_ids: [],
      active_modifiers: [],
      timed_effects: [],
    };
  };
  const effectiveSenseRange = (attacker, senseId) => {
    const observer = asSenseObserver(attacker);
    const senses = window.IRON_PIT_BROWSER_EFFECTIVE_SENSES;
    if (senses && senses.effectiveSenseRangeFt) return senses.effectiveSenseRangeFt(observer, senseId);
    const rules = window.IRON_PIT_BROWSER_CONDITION_RULES;
    if (rules && rules.effectiveSenseRangeFt) return rules.effectiveSenseRangeFt(observer, senseId);
    const template = observer.template || attacker || {};
    if (senseId === "blindsight") return Math.max(0, Number(template.blindsight_ft || 0));
    if (senseId === "truesight") return Math.max(0, Number(template.truesight_ft || 0));
    return 0;
  };
  const senseBypasses = (item, attacker, distance) => {
    if (distance == null) return false;
    return (item.bypass_attacker_senses || []).some((sense) => effectiveSenseRange(attacker, sense) >= distance);
  };
  const attacksAgainstDisadvantage = (state, attacker, distance = null) => (state.active_modifiers || [])
    .filter((item) => item.kind === "attacks-against-disadvantage"
      && sourceMatches(item, attacker && attacker.template ? attacker.template : attacker)
      && !senseBypasses(item, attacker, distance)).length;
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
    saveAdvantageModifiers(state, ability, context).length
      + (window.IRON_PIT_BROWSER_MODIFIERS?.d20TestAdvantage(state) || 0);
  function saveAdvantageSourceNames(state, ability, context = {}) {
    try {
      const contextual = saveAdvantageModifiers(state, ability, context);
      const universal = (state.active_modifiers || [])
        .filter((item) => item.kind === "d20-test-advantage");
      return [...new Set([...contextual, ...universal]
        .map((item) => item.source_name || item.source_effect_id))].sort();
    } catch (error) {
      console.error("Failed to identify browser saving-throw Advantage sources", {
        error, combatant: state?.template?.name, ability,
      });
      throw error;
    }
  }
  const saveDisadvantage = (state, ability = null) => (state.active_modifiers || [])
    .filter((item) => item.kind === "saving-throw-disadvantage"
      && (ability == null || item.save_ability == null || item.save_ability === ability)).length;

  function consumeSavingThrowModifiers(state) {
    const removed = (state.active_modifiers || [])
      .filter((item) => item.kind === "saving-throw-disadvantage" && item.consume_on_saving_throw)
      .map((item) => item.source_effect_id);
    state.active_modifiers = (state.active_modifiers || [])
      .filter((item) => !(item.kind === "saving-throw-disadvantage" && item.consume_on_saving_throw));
    return [...new Set(removed)].sort();
  }
  const deathSaveAdvantage = (state) => (state.active_modifiers || [])
    .some((item) => item.kind === "death-save-advantage" || item.kind === "d20-test-advantage");
  const healingMaximized = (state) => (state.active_modifiers || [])
    .some((item) => item.kind === "healing-maximize");
  const conditionImmune = (state, conditionId, sourceTemplate = null) => (state.active_modifiers || [])
    .some((item) => item.kind === "condition-immunity" && item.condition_id === conditionId
      && sourceMatches(item, sourceTemplate)
      && (item.required_active_effect_ids || []).every((effectId) =>
        (state.active_effect_ids || []).includes(effectId)));
  const targetingGate = (state, sourceTemplate = null) => (state.active_modifiers || [])
    .filter((item) => item.kind === "targeting-save-gate" && sourceMatches(item, sourceTemplate))
    .sort((a, b) => (b.save_dc || 0) - (a.save_dc || 0) || a.id.localeCompare(b.id))[0] || null;

  function removeOwnerAttackEnding(state) {
    try {
      const ending = (state.active_modifiers || []).filter((item) => item.ends_on_owner_attack);
      state.active_modifiers = (state.active_modifiers || []).filter((item) => !item.ends_on_owner_attack);
      // Match source and effect together; another source's surviving buff stays active.
      for (const effect of [...(state.timed_effects || [])]) {
        const matches = (item) => item.source_id === effect.source_id && item.source_effect_id === effect.source_effect_id;
        if (ending.some(matches) && !state.active_modifiers.some(matches)) {
          const timed = window.IRON_PIT_BROWSER_TIMED;
          if (!timed) throw new Error("Attack-ending timed modifier cleanup requires the lifecycle runtime.");
          timed.removeGroup(state, effect);
        }
      }
      return [...new Set(ending.map((item) => item.source_effect_id))].sort();
    } catch (error) {
      console.error("Attack-ending modifier cleanup failed.", state.template?.id, error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = {
    attacksAgainstDisadvantage, conditionImmune, consumeSavingThrowModifiers, deathSaveAdvantage, healingMaximized,
    removeOwnerAttackEnding, saveAdvantage, saveAdvantageSourceNames, saveDisadvantage, targetingGate,
  };
})();