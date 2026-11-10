(() => {
  "use strict";
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const H = () => window.IRON_PIT_BROWSER_SPELL_POLICY_SUPPORT;
  const A = () => window.IRON_PIT_BROWSER_SPELL_AREA;
  const C = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY;

  function eligible(caster, target, action, setup) {
    try {
      const state = target.state;
      if (!state.is_alive || state.is_dead || state.current_hp <= 0) return false;
      if ((action.excludedCreatureTypes || []).includes(String(state.template.creature_type || "").toLowerCase())) return false;
      if (action.skipUnconscious && (state.is_unconscious || C().has(state, "unconscious", setup))) return false;
      for (const conditionId of [...(action.excludedConditionImmunities || []), action.conditionId]) {
        if (I().immune(state, conditionId, caster.state.template, {
          sourceIsMagical: true, actor: target, setup,
        })) return false;
      }
      return true;
    } catch (error) {
      console.error("HP-pool spell target eligibility failed", {
        caster: caster?.combatant_id, target: target?.combatant_id, error,
      });
      throw error;
    }
  }

  function choose(caster, setup, turnKey) {
    try {
      const enemies = caster.side === "heroes" ? setup.monsters : setup.heroes;
      const choices = [];
      for (const [index, action] of (caster.state.template.hit_point_pool_spell_actions || []).entries()) {
        if (action.actionCost === "reaction" || !E().available(caster.state, action.actionCost)) continue;
        const placement = A().bestPlacement(caster, setup, action.areaRadius, action.range);
        if (!placement) continue;
        const hp = enemies.filter(m => placement.enemyIds.includes(m.combatant_id)
          && eligible(caster, m, action, setup)).map(m => m.state.current_hp).sort((a, b) => a - b);
        if (!hp.length) continue;
        for (const { castLevel: slotLevel, alternateCast } of H().castOptions(caster, {
          ...action, upcastDicePerLevel: action.extraDicePerUpcastLevel,
        }, turnKey)) {
          const count = action.poolDiceCount + (slotLevel - action.level) * action.extraDicePerUpcastLevel;
          if (hp[0] > count * action.poolDiceSize) continue;
          let mean = count * (action.poolDiceSize + 1) / 2, covered = 0;
          for (const value of hp) {
            if (value > mean) break;
            covered += 1; mean -= value;
          }
          const expectedDamage = Math.max(1, covered) * 3; // AI control value; not HP damage.
          choices.push({ action, slotLevel, placement, alternateCast, index, expectedDamage });
        }
      }
      choices.sort((a, b) => b.expectedDamage - a.expectedDamage
        || b.action.level - a.action.level || a.index - b.index);
      return choices[0] || null;
    } catch (error) {
      console.error("Browser HP-pool spell choice failed", {
        caster: caster?.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_HP_POOL_SPELL_POLICY = { choose, eligible };
})();
