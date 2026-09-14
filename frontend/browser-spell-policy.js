(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_SPELL_AREA;
  const U = () => window.IRON_PIT_BROWSER_AREA_TARGETING;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const O = () => window.IRON_PIT_BROWSER_OFFENSE_VALUE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const owns = (object, key) => Object.prototype.hasOwnProperty.call(object || {}, key);

  function castAccess(caster, action, turnKey) {
    const resources = caster.state.resources || {}, innateId = `innate-${action.id}`;
    if (owns(resources, innateId)) return resources[innateId] > 0 ? { slotLevel: action.level, resourceId: innateId } : null;
    const slotId = `spell-slot-${action.level}`;
    if (owns(resources, slotId)) {
      return C().slotSpellAvailable(caster.state, turnKey) && resources[slotId] > 0
        ? { slotLevel: action.level, resourceId: slotId } : null;
    }
    return { slotLevel: action.level, resourceId: null };
  }

  function slotLevel(caster, action, turnKey) {
    return castAccess(caster, action, turnKey)?.slotLevel ?? null;
  }

  const creatureType = (target) => (target.state.template.creature_type || "").toLowerCase();
  const rule = (action, field) => action[field] || window.IRON_PIT_BROWSER_SPELL_TARGET_RULES?.[action.id]?.[field] || [];
  const spellAffects = (action, target) => !rule(action, "excludedCreatureTypes").includes(creatureType(target)) && C().affectsTarget(target.state, action.level);
  function legalSingleTargets(caster, setup, action) {
    const enemies = caster.side === "heroes" ? setup.monsters : setup.heroes;
    return enemies.filter((target) => target.state.is_alive && !target.state.is_dead
      && target.state.current_hp > 0 && S().distance(caster, target) <= action.range && spellAffects(action, target));
  }

  function areaScore(placement, members, action) {
    const enemy = placement.enemyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), action), 0);
    return enemy - placement.friendlyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), action), 0);
  }

  function choose(caster, setup, turnKey, protectedAllyIds = []) {
    const candidates = [], members = new Map([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
    const protectedIds = new Set(protectedAllyIds);
    for (const [index, action] of (caster.state.template.spell_save_actions || []).entries()) {
      if (action.actionCost === "reaction" || !E().available(caster.state, action.actionCost)) continue;
      if (action.concentration && caster.state.concentration?.effect_id === action.id) continue;
      const access = castAccess(caster, action, turnKey);
      if (!access) continue;
      if (action.area) {
        for (const placement of U().legalPlacements(caster, setup, action.area, action.range)) {
          if (placement.friendlyIds.some((id) => protectedIds.has(id))) continue;
          const score = areaScore(placement, members, action);
          candidates.push({ action, index, score, ...access,
            targetIds: [...placement.enemyIds, ...placement.friendlyIds], placement });
        }
        continue;
      }
      if (action.areaRadius) {
        const placement = A().bestPlacement(caster, setup, action.areaRadius, action.range, protectedAllyIds);
        if (!placement) continue;
        const score = areaScore(placement, members, action);
        candidates.push({ action, index, score, ...access,
          targetIds: [...placement.enemyIds, ...placement.friendlyIds], placement });
        continue;
      }
      for (const target of legalSingleTargets(caster, setup, action)) {
        candidates.push({ action, index, score: O().saveSpell(target, action), ...access,
          targetIds: [target.combatant_id], placement: null, hp: target.state.current_hp });
      }
    }
    candidates.sort((a, b) => b.score - a.score || a.action.level - b.action.level
      || (a.hp ?? Number.MAX_SAFE_INTEGER) - (b.hp ?? Number.MAX_SAFE_INTEGER) || a.index - b.index);
    if (!candidates.length) return null;
    const best = candidates[0];
    return { action: best.action, slotLevel: best.slotLevel, resourceId: best.resourceId,
      targetIds: best.targetIds, placement: best.placement, expectedDamage: best.score };
  }

  window.IRON_PIT_BROWSER_SPELL_POLICY = { castAccess, choose, slotLevel };
})();