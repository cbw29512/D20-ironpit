(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_SPELL_AREA;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;

  function availableRangeModifier(state, baseRange, requiredRange) {
    if (requiredRange <= baseRange) return null;
    const options = [...(state.template.spellRangeModifiers || [])]
      .filter((option) =>
        baseRange >= (option.minimumBaseRangeFt ?? 5)
        && requiredRange <= baseRange * (option.rangeMultiplier || 1)
        && (state.resources?.[option.resourceId] || 0) >= (option.resourceCost || 1))
      .sort((a, b) => (b.priority || 0) - (a.priority || 0));
    return options[0] || null;
  }

  function effectiveRange(state, baseRange) {
    let result = baseRange;
    for (const option of (state.template.spellRangeModifiers || [])) {
      if (baseRange < (option.minimumBaseRangeFt ?? 5)) continue;
      if ((state.resources?.[option.resourceId] || 0) < (option.resourceCost || 1)) continue;
      result = Math.max(result, baseRange * (option.rangeMultiplier || 1));
    }
    return result;
  }

  function spendRangeModifier(state, option) {
    if (!option) return null;
    const current = state.resources?.[option.resourceId] || 0;
    const cost = option.resourceCost || 1;
    if (current < cost) throw new Error(`Insufficient ${option.resourceId} for ${option.name}.`);
    state.resources[option.resourceId] = current - cost;
    return state.resources[option.resourceId];
  }

  function placementKey(item) {
    return JSON.stringify({
      targetIds: item.targetIds || item.enemyIds || [],
      friendlyIds: item.friendlyIds || [],
      origin: item.origin || null,
      direction: item.direction || null,
    });
  }

  function scaledSpell(action, slotLevel) {
    if (action.level === 0) {
      if (slotLevel !== 0) throw new Error("Cantrips cannot expend spell slots.");
      return action;
    }
    if (slotLevel < action.level || slotLevel > 9) throw new Error(`Illegal slot level ${slotLevel} for ${action.name}.`);
    const levelsAbove = slotLevel - action.level;
    if (!levelsAbove) return action;
    if (!(action.upcastDicePerLevel > 0)) throw new Error(`${action.name} has no certified higher-slot scaling.`);
    if (action.damageComponents?.length) throw new Error("Multi-component spell upcasting requires component-specific scaling data.");
    return { ...action, damageDiceCount: (action.damageDiceCount || 0) + levelsAbove * action.upcastDicePerLevel };
  }

  function slotLevels(caster, action, turnKey) {
    return C().legalSlotLevels(caster.state, turnKey, action.level, {
      higherSlotScaling: (action.upcastDicePerLevel || 0) > 0,
    });
  }

  function slotLevel(caster, action, turnKey) {
    const levels = slotLevels(caster, action, turnKey);
    return levels.length ? levels.at(-1) : null;
  }

  function alternateCasts(caster, action) {
    return (caster.state.template.alternate_spell_cast_grants || [])
      .filter((grant) => grant.spell_id === action.id)
      .filter((grant) => !grant.resource_id
        || (caster.state.resources?.[grant.resource_id] || 0) >= (grant.resource_cost || 1))
      .sort((a, b) => (b.priority || 0) - (a.priority || 0)
        || a.cast_level - b.cast_level || a.source_id.localeCompare(b.source_id));
  }

  function castOptions(caster, action, turnKey) {
    const normal = slotLevels(caster, action, turnKey)
      .map((castLevel) => ({ castLevel, alternateCast: null }));
    const alternate = alternateCasts(caster, action)
      .map((grant) => ({ castLevel: grant.cast_level, alternateCast: grant }));
    return [...normal, ...alternate];
  }

  function areaSpellProtection(caster, setup, action, castLevel, explicitProtectedIds = []) {
    const grant = caster.state.template.area_spell_ally_protection || null;
    const explicit = new Set(explicitProtectedIds);
    if (!grant || !(grant.eligible_spell_ids || []).includes(action.id)) {
      return { ids: explicit, limit: explicit.size ? null : 0 };
    }
    const allies = caster.side === "heroes" ? setup.heroes : setup.monsters;
    const visible = allies
      .filter((ally) => ally.combatant_id !== caster.combatant_id
        && ally.state.is_alive && !ally.state.is_dead && ally.state.current_hp > 0
        && (!grant.requires_source_sight
          || window.IRON_PIT_BROWSER_CONDITION_RULES.canSee(caster.state, ally.state)))
      .map((ally) => ally.combatant_id);
    return {
      ids: new Set([...explicit, ...visible]),
      limit: (grant.base_protected_allies || 0)
        + (grant.protected_allies_per_slot_level || 0) * castLevel,
    };
  }

  function protectedUniversalPlacements(caster, setup, action, castLevel, range, explicitProtectedIds = []) {
    const protection = areaSpellProtection(caster, setup, action, castLevel, explicitProtectedIds);
    return window.IRON_PIT_BROWSER_AREA_TARGETING.legalPlacements(caster, setup, action.area, range)
      .flatMap((placement) => {
        const friendly = [...(placement.friendlyIds || [])];
        if (!friendly.length) return [placement];
        const allowed = friendly.every((id) => protection.ids.has(id))
          && (protection.limit == null || friendly.length <= protection.limit);
        return allowed ? [{ ...placement, friendlyIds: [], protectedFriendlyIds: friendly }] : [];
      });
  }

  function legalSingleTargets(caster, setup, action, range = action.range) {
    const enemies = caster.side === "heroes" ? setup.monsters : setup.heroes;
    return enemies.filter((target) => target.state.is_alive && !target.state.is_dead
      && target.state.current_hp > 0 && S().distance(caster, target) <= range
      && (!window.IRON_PIT_BROWSER_GRID_BARRIERS || window.IRON_PIT_BROWSER_GRID_BARRIERS.clearBetweenMembers(caster, target, setup))
      && (!action.requiresTargetHearing || !target.state.active_effect_ids.includes("deafened"))
      && (!action.requiresTargetSight || window.IRON_PIT_BROWSER_CONDITION_RULES.canSee(caster.state, target.state))
      && (!(action.requiredTargetCreatureTypes || []).length
        || (action.requiredTargetCreatureTypes || []).some((kind) =>
          String(target.state.template.creature_type || "").split(" (")[0].trim().toLowerCase() === String(kind).toLowerCase())));
  }

  window.IRON_PIT_BROWSER_SPELL_POLICY_SUPPORT = {
    availableRangeModifier, effectiveRange, spendRangeModifier, placementKey, scaledSpell,
    slotLevels, slotLevel, alternateCasts, castOptions, areaSpellProtection,
    protectedUniversalPlacements, legalSingleTargets,
  };
})();
