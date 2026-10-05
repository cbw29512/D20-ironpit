(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_SPELL_AREA;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const O = () => window.IRON_PIT_BROWSER_OFFENSE_VALUE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;

  const H = () => window.IRON_PIT_BROWSER_SPELL_POLICY_SUPPORT;

  function chooseActionAtSlot(caster, setup, action, castLevel, protectedAllyIds = [], alternateCast = null) {
    try {
      if (!action || action.actionCost === "reaction" || (action.castRounds || 1) > 1
        || !E().available(caster.state, action.actionCost)
        || window.IRON_PIT_BROWSER_TEMPORARY_TERRAIN?.spellTerrainSupported?.(action) === false) return null;
      const scaled = H().scaledSpell(action, castLevel);
      const members = new Map([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
      if (action.area) {
        const baseRange = action.range;
        const castRange = action.area.origin === "point" ? H().effectiveRange(caster.state, baseRange) : baseRange;
        const normalKeys = new Set(H().protectedUniversalPlacements(
          caster, setup, action, castLevel, baseRange, protectedAllyIds,
        ).map(H().placementKey));
        const placements = H().protectedUniversalPlacements(
          caster, setup, action, castLevel, castRange, protectedAllyIds,
        );
        if (!placements.length) return null;
        placements.sort((a, b) =>
          b.enemyIds.length - a.enemyIds.length || a.friendlyIds.length - b.friendlyIds.length);
        const placement = placements[0];
        const score = placement.enemyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), scaled), 0);
        const rangeModifier = normalKeys.has(H().placementKey(placement))
          ? null : H().availableRangeModifier(caster.state, baseRange, castRange);
        return { action, slotLevel: castLevel, targetIds: [...placement.enemyIds], placement,
          expectedDamage: score, rangeModifier, alternateCast };
      }
      if (action.areaRadius) {
        const protection = H().areaSpellProtection(caster, setup, action, castLevel, protectedAllyIds);
        const placement = A().bestPlacement(
          caster, setup, action.areaRadius, action.range, [...protection.ids], protection.limit,
        );
        if (!placement) return null;
        const score = placement.enemyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), scaled), 0)
          - placement.friendlyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), scaled), 0);
        return { action, slotLevel: castLevel,
          targetIds: [...placement.enemyIds, ...placement.friendlyIds], placement, expectedDamage: score,
          alternateCast };
      }
      const castRange = H().effectiveRange(caster.state, action.range);
      const chosen = H().rankedSaveTargets(H().legalSingleTargets(caster, setup, action, castRange), scaled, castLevel);
      if (!chosen.length) return null;
      let score = 0, farthest = 0;
      for (const target of chosen) {
        score += O().saveSpell(target, scaled);
        if (action.failedSaveTimedEffect) score += Math.max(8, target.state.current_hp * 0.35);
        farthest = Math.max(farthest, S().distance(caster, target));
      }
      return { action, slotLevel: castLevel, targetIds: chosen.map((target) => target.combatant_id),
        placement: null, expectedDamage: score, hp: chosen[0].state.current_hp,
        rangeModifier: H().availableRangeModifier(caster.state, action.range, farthest),
        alternateCast };
    } catch (error) {
      console.error("Browser fixed-slot save-spell selection failed", { caster: caster?.combatant_id, spell: action?.id, error });
      throw error;
    }
  }

  function choose(caster, setup, turnKey, protectedAllyIds = []) {
    try {
      const candidates = [], members = new Map([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
      for (const [index, action] of (caster.state.template.spell_save_actions || []).entries()) {
        if (action.actionCost === "reaction" || (action.castRounds || 1) > 1
          || action.repeatOnly
          || (action.concentration && caster.state.concentration)
          || !E().available(caster.state, action.actionCost)
          || window.IRON_PIT_BROWSER_TEMPORARY_TERRAIN?.spellTerrainSupported?.(action) === false
          || window.IRON_PIT_BROWSER_DEBUFF_ANSWERS?.failedSaveIsBeneficial?.(action)) continue;
        for (const { castLevel, alternateCast } of H().castOptions(caster, action, turnKey)) {
          const scaled = H().scaledSpell(action, castLevel);
          if (action.area) {
            const baseRange = action.range;
            const castRange = action.area.origin === "point" ? H().effectiveRange(caster.state, baseRange) : baseRange;
            const normalKeys = new Set(H().protectedUniversalPlacements(
              caster, setup, action, castLevel, baseRange, protectedAllyIds,
            ).map(H().placementKey));
            const placements = H().protectedUniversalPlacements(
              caster, setup, action, castLevel, castRange, protectedAllyIds,
            );
            if (!placements.length) continue;
            placements.sort((a, b) =>
              b.enemyIds.length - a.enemyIds.length || a.friendlyIds.length - b.friendlyIds.length);
            const placement = placements[0];
            const score = placement.enemyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), scaled), 0);
            const rangeModifier = normalKeys.has(H().placementKey(placement))
              ? null : H().availableRangeModifier(caster.state, baseRange, castRange);
            candidates.push({ action, index, score, slotLevel: castLevel,
              targetIds: [...placement.enemyIds], placement, rangeModifier, alternateCast });
            continue;
          }
          if (action.areaRadius) {
            const protection = H().areaSpellProtection(caster, setup, action, castLevel, protectedAllyIds);
            const placement = A().bestPlacement(
              caster, setup, action.areaRadius, action.range, [...protection.ids], protection.limit,
            );
            if (!placement) continue;
            const score = placement.enemyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), scaled), 0)
              - placement.friendlyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), scaled), 0);
            candidates.push({ action, index, score, slotLevel: castLevel,
              targetIds: [...placement.enemyIds, ...placement.friendlyIds], placement, alternateCast });
            continue;
          }
          const castRange = H().effectiveRange(caster.state, action.range);
          const chosen = H().rankedSaveTargets(H().legalSingleTargets(caster, setup, action, castRange), scaled, castLevel);
          if (!chosen.length) continue;
          let score = 0, farthest = 0;
          for (const target of chosen) {
            score += O().saveSpell(target, scaled);
            farthest = Math.max(farthest, S().distance(caster, target));
          }
          candidates.push({ action, index, score, slotLevel: castLevel,
            targetIds: chosen.map((target) => target.combatant_id), placement: null, hp: chosen[0].state.current_hp,
            rangeModifier: H().availableRangeModifier(caster.state, action.range, farthest),
            alternateCast });
        }
      }
      candidates.sort((a, b) => Number(b.score > 0) - Number(a.score > 0)
        || b.action.level - a.action.level
        || b.score - a.score
        || Number(Boolean(b.alternateCast)) - Number(Boolean(a.alternateCast))
        || (a.hp ?? Number.MAX_SAFE_INTEGER) - (b.hp ?? Number.MAX_SAFE_INTEGER) || a.index - b.index);
      if (!candidates.length) return null;
      const best = candidates[0];
      return { action: best.action, slotLevel: best.slotLevel, targetIds: best.targetIds,
        placement: best.placement, expectedDamage: best.score, rangeModifier: best.rangeModifier || null,
        alternateCast: best.alternateCast || null,
        damageMaximizer: C().safeDamageMaximizer(caster.state, best.action.id, best.slotLevel) };
    } catch (error) {
      console.error("Browser save-spell selection failed", { caster: caster?.combatant_id, error });
      throw error;
    }
  }

  function chooseById(caster, setup, turnKey, spellId, protectedAllyIds = []) {
    try {
      const action = (caster.state.template.spell_save_actions || []).find((item) => item.id === spellId);
      if (!action) return null;
      const options = H().castOptions(caster, action, turnKey);
      if (!options.length) return null;
      const selected = options.sort((a, b) =>
        Number(Boolean(b.alternateCast)) - Number(Boolean(a.alternateCast))
        || b.castLevel - a.castLevel)[0];
      return chooseActionAtSlot(
        caster, setup, action, selected.castLevel, protectedAllyIds, selected.alternateCast,
      );
    } catch (error) {
      console.error("Browser named save-spell selection failed", { caster: caster?.combatant_id, spellId, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SPELL_POLICY = {
    choose, chooseActionAtSlot, chooseById,
    scaledSpell: H().scaledSpell,
    slotLevel: H().slotLevel,
    slotLevels: H().slotLevels,
    alternateCasts: H().alternateCasts,
    castOptions: H().castOptions,
    areaSpellProtection: H().areaSpellProtection,
    protectedUniversalPlacements: H().protectedUniversalPlacements,
    availableRangeModifier: H().availableRangeModifier,
    effectiveRange: H().effectiveRange,
    spendRangeModifier: H().spendRangeModifier,
  };
})();
