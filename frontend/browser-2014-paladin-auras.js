(() => {
  "use strict";

  const AURA_EFFECTS = new Set([
    "aura-of-protection-2014",
    "aura-of-devotion-2014",
    "aura-of-courage-2014",
  ]);
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || {
    has: (state, id) => state.active_effect_ids?.includes(id) || false,
  };

  const members = (setup) => [...(setup?.heroes || []), ...(setup?.monsters || [])];
  const allies = (target, setup) => target.side === "heroes" ? setup.heroes : setup.monsters;

  function clear(setup) {
    for (const member of members(setup)) {
      member.state.active_modifiers = (member.state.active_modifiers || [])
        .filter((item) => !AURA_EFFECTS.has(item.source_effect_id));
    }
  }

  function auraRadius(source) {
    try {
      const template = source?.state?.template || {};
      const hasAura = (template.aura_of_protection_2014_bonus || 0) > 0
        || template.aura_of_devotion_2014 === true
        || template.aura_of_courage_2014 === true;
      if (!hasAura) return 0;
      const radius = template.aura_radius_2014_ft;
      if (!Number.isInteger(radius) || radius <= 0) {
        throw new Error(`${template.name || source?.combatant_id} has a 2014 Paladin aura without a valid radius.`);
      }
      return radius;
    } catch (error) {
      console.error("Failed to read browser 2014 Paladin aura radius.", { error, combatant: source?.combatant_id });
      throw error;
    }
  }

  function activeAuraSource(source) {
    try {
      const state = source.state;
      return state.is_alive && !state.is_dead && state.current_hp > 0
        && !state.is_unconscious && !Q().has(state, "unconscious");
    } catch (error) {
      console.error("Failed to evaluate browser 2014 Paladin aura source.", { error, combatant: source?.combatant_id });
      throw error;
    }
  }

  function nearbySources(target, setup) {
    return allies(target, setup).filter((source) => {
      const radius = auraRadius(source);
      return radius > 0 && activeAuraSource(source) && S().distance(source, target) <= radius;
    });
  }

  function saveAura(target, sources) {
    const candidates = sources
      .map((source) => [source.state.template.aura_of_protection_2014_bonus || 0, source])
      .filter(([bonus]) => bonus > 0)
      .sort((a, b) => b[0] - a[0] || a[1].combatant_id.localeCompare(b[1].combatant_id));
    if (!candidates.length) return;
    const [bestBonus, source] = candidates[0];
    M().add(target.state, {
      id: `${source.combatant_id}:aura-of-protection-2014:${target.combatant_id}`,
      source_id: source.combatant_id, source_effect_id: "aura-of-protection-2014",
      kind: "saving-throw-flat", flat_bonus: bestBonus,
    });
  }

  function conditionAura(target, sources, featureName, effectId, conditionId) {
    if (target.state.template.condition_immunities?.includes(conditionId)) return;
    const source = sources.find((member) => member.state.template[featureName] === true);
    if (!source) return;
    M().add(target.state, {
      id: `${source.combatant_id}:${effectId}:${target.combatant_id}`,
      source_id: source.combatant_id, source_effect_id: effectId,
      kind: "condition-immunity", condition_id: conditionId,
    });
  }

  function sync(setup) {
    try {
      if (!setup || !M() || !S()) return;
      clear(setup);
      for (const target of members(setup)) {
        const sources = nearbySources(target, setup);
        saveAura(target, sources);
        conditionAura(target, sources, "aura_of_devotion_2014", "aura-of-devotion-2014", "charmed");
        conditionAura(target, sources, "aura_of_courage_2014", "aura-of-courage-2014", "frightened");
      }
    } catch (error) {
      console.error("Failed to synchronize browser 2014 Paladin auras.", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_PALADIN_AURAS_2014 = { sync };
})();
