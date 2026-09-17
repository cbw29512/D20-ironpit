(() => {
  "use strict";

  const AURA_EFFECTS = new Set([
    "aura-of-protection-2014",
    "aura-of-devotion-2014",
    "aura-of-courage-2014",
  ]);
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;

  const members = (setup) => [...(setup?.heroes || []), ...(setup?.monsters || [])];
  const allies = (target, setup) => target.side === "heroes" ? setup.heroes : setup.monsters;

  function clear(setup) {
    for (const member of members(setup)) {
      member.state.active_modifiers = (member.state.active_modifiers || [])
        .filter((item) => !AURA_EFFECTS.has(item.source_effect_id));
    }
  }

  function nearbySources(target, setup) {
    return allies(target, setup).filter((source) => source.combatant_id !== target.combatant_id
      && S().active(source) && S().distance(source, target) <= 10);
  }

  function saveAura(target, sources) {
    const own = target.state.template.aura_of_protection_2014_bonus || 0;
    const candidates = sources
      .map((source) => [source.state.template.aura_of_protection_2014_bonus || 0, source])
      .filter(([bonus]) => bonus > 0)
      .sort((a, b) => b[0] - a[0] || a[1].combatant_id.localeCompare(b[1].combatant_id));
    if (!candidates.length) return;
    const [bestBonus, source] = candidates[0], extra = Math.max(0, bestBonus - own);
    if (!extra) return;
    M().add(target.state, {
      id: `${source.combatant_id}:aura-of-protection-2014:${target.combatant_id}`,
      source_id: source.combatant_id, source_effect_id: "aura-of-protection-2014",
      kind: "saving-throw-flat", flat_bonus: extra,
    });
  }

  function conditionAura(target, sources, featureName, conditionId) {
    if (target.state.template.condition_immunities?.includes(conditionId)) return;
    const source = sources.find((member) => member.state.template[featureName] === true);
    if (!source) return;
    M().add(target.state, {
      id: `${source.combatant_id}:${featureName}:${target.combatant_id}`,
      source_id: source.combatant_id, source_effect_id: featureName,
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
        conditionAura(target, sources, "aura_of_devotion_2014", "charmed");
        conditionAura(target, sources, "aura_of_courage_2014", "frightened");
      }
    } catch (error) {
      console.error("Failed to synchronize browser 2014 Paladin auras.", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_PALADIN_AURAS_2014 = { sync };
})();
