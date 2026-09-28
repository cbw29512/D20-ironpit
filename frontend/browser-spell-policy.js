(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_SPELL_AREA;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const O = () => window.IRON_PIT_BROWSER_OFFENSE_VALUE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const F = () => window.IRON_PIT_BROWSER_SPELL_FEATURES;

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
    if (F()?.legalSaveSpellLevels) return F().legalSaveSpellLevels(caster.state, turnKey, action);
    return C().legalSlotLevels(caster.state, turnKey, action.level, {
      higherSlotScaling: (action.upcastDicePerLevel || 0) > 0,
    });
  }

  function shouldAutoMaximize(caster, action) {
    return F()?.shouldAutoMaximize ? shouldAutoMaximize(caster, action) : false;
  }

  function slotLevel(caster, action, turnKey) {
    const levels = slotLevels(caster, action, turnKey);
    return levels.length ? levels.at(-1) : null;
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
    const ids = new Set([...explicit, ...visible]);
    const limit = (grant.base_protected_allies || 0)
      + (grant.protected_allies_per_slot_level || 0) * castLevel;
    return { ids, limit };
  }

  function protectedUniversalPlacements(caster, setup, action, castLevel, range, explicitProtectedIds = []) {
    const protection = areaSpellProtection(caster, setup, action, castLevel, explicitProtectedIds);
    return window.IRON_PIT_BROWSER_AREA_TARGETING.legalPlacements(caster, setup, action.area, range)
      .flatMap((placement) => {
        const friendly = [...(placement.friendlyIds || [])];
        if (!friendly.length) return [placement];
        const allEligible = friendly.every((id) => protection.ids.has(id));
        const withinLimit = protection.limit == null || friendly.length <= protection.limit;
        if (!allEligible || !withinLimit) return [];
        return [{ ...placement, friendlyIds: [], protectedFriendlyIds: friendly }];
      });
  }

  function legalSingleTargets(caster, setup, action, range = action.range) {
    const enemies = caster.side === "heroes" ? setup.monsters : setup.heroes;
    return enemies.filter((target) => target.state.is_alive && !target.state.is_dead
      && target.state.current_hp > 0 && S().distance(caster, target) <= range
      && (!action.requiresTargetHearing || !target.state.active_effect_ids.includes("deafened"))
      && (!action.requiresTargetSight || window.IRON_PIT_BROWSER_CONDITION_RULES.canSee(caster.state, target.state)));
  }

  function chooseActionAtSlot(caster, setup, action, castLevel, protectedAllyIds = []) {
    try {
      if (!action || action.actionCost === "reaction" || !E().available(caster.state, action.actionCost)) return null;
      const scaled = scaledSpell(action, castLevel);
      const members = new Map([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
      if (action.area) {
        const baseRange = action.range;
        const castRange = action.area.origin === "point" ? effectiveRange(caster.state, baseRange) : baseRange;
        const normalKeys = new Set(protectedUniversalPlacements(
          caster, setup, action, castLevel, baseRange, protectedAllyIds,
        ).map(placementKey));
        const placements = protectedUniversalPlacements(
          caster, setup, action, castLevel, castRange, protectedAllyIds,
        );
        if (!placements.length) return null;
        placements.sort((a, b) =>
          b.enemyIds.length - a.enemyIds.length || a.friendlyIds.length - b.friendlyIds.length);
        const placement = placements[0];
        const score = placement.enemyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), scaled), 0);
        const rangeModifier = normalKeys.has(placementKey(placement))
          ? null : availableRangeModifier(caster.state, baseRange, castRange);
        return { action, slotLevel: castLevel, targetIds: [...placement.enemyIds], placement,
          expectedDamage: score, rangeModifier,
          maximizeDamage: shouldAutoMaximize(caster, action) };
      }
      if (action.areaRadius) {
        const protection = areaSpellProtection(caster, setup, action, castLevel, protectedAllyIds);
        const placement = A().bestPlacement(
          caster, setup, action.areaRadius, action.range, [...protection.ids], protection.limit,
        );
        if (!placement) return null;
        const score = placement.enemyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), scaled), 0)
          - placement.friendlyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), scaled), 0);
        return { action, slotLevel: castLevel,
          targetIds: [...placement.enemyIds, ...placement.friendlyIds], placement, expectedDamage: score,
          maximizeDamage: shouldAutoMaximize(caster, action) };
      }
      const castRange = effectiveRange(caster.state, action.range);
      const legal = legalSingleTargets(caster, setup, action, castRange);
      if (!legal.length) return null;
      legal.sort((a, b) => O().saveSpell(b, scaled) - O().saveSpell(a, scaled)
        || a.state.current_hp - b.state.current_hp || a.combatant_id.localeCompare(b.combatant_id));
      const target = legal[0];
      return { action, slotLevel: castLevel, targetIds: [target.combatant_id],
        placement: null, expectedDamage: O().saveSpell(target, scaled), hp: target.state.current_hp,
        rangeModifier: availableRangeModifier(caster.state, action.range, S().distance(caster, target)),
        maximizeDamage: shouldAutoMaximize(caster, action) };
    } catch (error) {
      console.error("Browser fixed-slot save-spell selection failed", { caster: caster?.combatant_id, spell: action?.id, error });
      throw error;
    }
  }

  function choose(caster, setup, turnKey, protectedAllyIds = []) {
    try {
      const candidates = [], members = new Map([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
      for (const [index, action] of (caster.state.template.spell_save_actions || []).entries()) {
        if (action.actionCost === "reaction" || action.concentration || !E().available(caster.state, action.actionCost)) continue;
        for (const castLevel of slotLevels(caster, action, turnKey)) {
          const scaled = scaledSpell(action, castLevel);
          if (action.area) {
            const baseRange = action.range;
            const castRange = action.area.origin === "point" ? effectiveRange(caster.state, baseRange) : baseRange;
            const normalKeys = new Set(protectedUniversalPlacements(
              caster, setup, action, castLevel, baseRange, protectedAllyIds,
            ).map(placementKey));
            const placements = protectedUniversalPlacements(
              caster, setup, action, castLevel, castRange, protectedAllyIds,
            );
            if (!placements.length) continue;
            placements.sort((a, b) =>
              b.enemyIds.length - a.enemyIds.length || a.friendlyIds.length - b.friendlyIds.length);
            const placement = placements[0];
            const score = placement.enemyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), scaled), 0);
            const rangeModifier = normalKeys.has(placementKey(placement))
              ? null : availableRangeModifier(caster.state, baseRange, castRange);
            candidates.push({ action, index, score, slotLevel: castLevel,
              targetIds: [...placement.enemyIds], placement, rangeModifier });
            continue;
          }
          if (action.areaRadius) {
            const protection = areaSpellProtection(caster, setup, action, castLevel, protectedAllyIds);
            const placement = A().bestPlacement(
              caster, setup, action.areaRadius, action.range, [...protection.ids], protection.limit,
            );
            if (!placement) continue;
            const score = placement.enemyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), scaled), 0)
              - placement.friendlyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), scaled), 0);
            candidates.push({ action, index, score, slotLevel: castLevel,
              targetIds: [...placement.enemyIds, ...placement.friendlyIds], placement });
            continue;
          }
          const castRange = effectiveRange(caster.state, action.range);
          for (const target of legalSingleTargets(caster, setup, action, castRange)) {
            candidates.push({ action, index, score: O().saveSpell(target, scaled), slotLevel: castLevel,
              targetIds: [target.combatant_id], placement: null, hp: target.state.current_hp,
              rangeModifier: availableRangeModifier(caster.state, action.range, S().distance(caster, target)) });
          }
        }
      }
      candidates.sort((a, b) => b.score - a.score || a.action.level - b.action.level
        || (a.hp ?? Number.MAX_SAFE_INTEGER) - (b.hp ?? Number.MAX_SAFE_INTEGER) || a.index - b.index);
      if (!candidates.length) return null;
      const best = candidates[0];
      return { action: best.action, slotLevel: best.slotLevel, targetIds: best.targetIds,
        placement: best.placement, expectedDamage: best.score, rangeModifier: best.rangeModifier || null,
        maximizeDamage: shouldAutoMaximize(caster, best.action) };
    } catch (error) {
      console.error("Browser save-spell selection failed", { caster: caster?.combatant_id, error });
      throw error;
    }
  }

  function chooseById(caster, setup, turnKey, spellId, protectedAllyIds = []) {
    try {
      const action = (caster.state.template.spell_save_actions || []).find((item) => item.id === spellId);
      if (!action) return null;
      const levels = slotLevels(caster, action, turnKey);
      if (!levels.length) return null;
      return chooseActionAtSlot(caster, setup, action, levels.at(-1), protectedAllyIds);
    } catch (error) {
      console.error("Browser named save-spell selection failed", { caster: caster?.combatant_id, spellId, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SPELL_POLICY = {
    choose, chooseActionAtSlot, chooseById, scaledSpell, slotLevel, slotLevels,
    areaSpellProtection, protectedUniversalPlacements,
    availableRangeModifier, effectiveRange, spendRangeModifier,
  };
})();
