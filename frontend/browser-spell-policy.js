(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_SPELL_AREA;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const O = () => window.IRON_PIT_BROWSER_OFFENSE_VALUE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;

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

  function legalSingleTargets(caster, setup, action) {
    const enemies = caster.side === "heroes" ? setup.monsters : setup.heroes;
    return enemies.filter((target) => target.state.is_alive && !target.state.is_dead
      && target.state.current_hp > 0 && S().distance(caster, target) <= action.range
      && (!action.requiresTargetHearing || !target.state.active_effect_ids.includes("deafened")));
  }

  function choose(caster, setup, turnKey, protectedAllyIds = []) {
    try {
      const candidates = [], members = new Map([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
      for (const [index, action] of (caster.state.template.spell_save_actions || []).entries()) {
        if (action.actionCost === "reaction" || action.concentration || !E().available(caster.state, action.actionCost)) continue;
        for (const castLevel of slotLevels(caster, action, turnKey)) {
          const scaled = scaledSpell(action, castLevel);
          if (action.areaRadius) {
            const placement = A().bestPlacement(caster, setup, action.areaRadius, action.range, protectedAllyIds);
            if (!placement) continue;
            const score = placement.enemyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), scaled), 0)
              - placement.friendlyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), scaled), 0);
            candidates.push({ action, index, score, slotLevel: castLevel,
              targetIds: [...placement.enemyIds, ...placement.friendlyIds], placement });
            continue;
          }
          for (const target of legalSingleTargets(caster, setup, action)) {
            candidates.push({ action, index, score: O().saveSpell(target, scaled), slotLevel: castLevel,
              targetIds: [target.combatant_id], placement: null, hp: target.state.current_hp });
          }
        }
      }
      candidates.sort((a, b) => b.score - a.score || a.action.level - b.action.level
        || (a.hp ?? Number.MAX_SAFE_INTEGER) - (b.hp ?? Number.MAX_SAFE_INTEGER) || a.index - b.index);
      if (!candidates.length) return null;
      const best = candidates[0];
      return { action: best.action, slotLevel: best.slotLevel, targetIds: best.targetIds,
        placement: best.placement, expectedDamage: best.score };
    } catch (error) {
      console.error("Browser save-spell selection failed", { caster: caster?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SPELL_POLICY = { choose, scaledSpell, slotLevel, slotLevels };
})();