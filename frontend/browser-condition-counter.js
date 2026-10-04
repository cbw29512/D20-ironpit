(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_DEBUFF_ANSWERS;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const P = () => window.IRON_PIT_BROWSER_SPELL_POLICY;
  const R = () => window.IRON_PIT_BROWSER_SPELL_RESOLUTION;

  function allies(member, setup) {
    const roster = member.side === "heroes" ? setup.heroes : setup.monsters;
    return roster.filter((ally) => ally.state.is_alive && !ally.state.is_dead && ally.state.current_hp > 0);
  }

  function typeOk(action, target) {
    const creatureType = String(target.state.template.creature_type || "").split(" (")[0].trim().toLowerCase();
    const required = (action.requiredTargetCreatureTypes || action.required_target_creature_types || [])
      .map((item) => String(item).toLowerCase());
    const excluded = (action.excludedTargetCreatureTypes || action.excluded_target_creature_types || [])
      .map((item) => String(item).toLowerCase());
    if (required.length && !required.includes(creatureType)) return false;
    return !excluded.includes(creatureType);
  }

  function radiusOf(action) {
    return Number(action.area?.radius_ft || action.area?.radiusFt || action.areaRadius || action.area_radius_ft || 0);
  }

  function reachable(caster, target, action) {
    return S().distance(caster, target) <= Number(action.range || action.range_ft || 0) + radiusOf(action);
  }

  function covered(center, target, action) {
    const radius = radiusOf(action);
    if (radius <= 0) return center.combatant_id === target.combatant_id;
    return S().distance(center, target) <= radius;
  }

  function choose(caster, setup, turnKey) {
    try {
      if (!E().available(caster.state, "action")) return null;
      const needy = allies(caster, setup).filter((ally) => A().activeConditionIds(ally.state).length);
      if (!needy.length) return null;
      for (const action of caster.state.template.spell_save_actions || []) {
        const answered = A().counteredConditionIds(action);
        if (!answered.size || !A().failedSaveIsBeneficial(action)) continue;
        if ((action.actionCost || action.action_cost || "action") !== "action") continue;
        if ((action.castRounds || action.cast_rounds || 1) > 1 || action.repeatOnly || action.repeat_only) continue;
        if ((action.concentration) && caster.state.concentration) continue;
        const patients = needy.filter((ally) => {
          const active = new Set(A().activeConditionIds(ally.state));
          return [...answered].some((item) => active.has(item)) && typeOk(action, ally) && reachable(caster, ally, action);
        });
        if (!patients.length) continue;
        const center = patients[0];
        const targetIds = allies(caster, setup)
          .filter((ally) => typeOk(action, ally) && covered(center, ally, action))
          .map((ally) => ally.combatant_id);
        if (!targetIds.includes(center.combatant_id)) continue;
        const options = P()?.castOptions?.(caster, action, turnKey) || [];
        if (!options.length) continue;
        const option = options[0];
        return {
          action, slotLevel: option.castLevel, targetIds, expectedDamage: 0, alternateCast: option.alternateCast || null,
        };
      }
      return null;
    } catch (error) {
      console.error("Failed browser condition-counter choice", { caster: caster?.combatant_id, error });
      throw error;
    }
  }

  function resolve(sequence, round, caster, setup, choice, turnKey) {
    return R().resolve(sequence, round, caster, setup, choice, turnKey);
  }

  window.IRON_PIT_BROWSER_CONDITION_COUNTER = { choose, resolve };
})();
