(() => {
  "use strict";
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const P = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const R = () => window.IRON_PIT_BROWSER_CONDITION_REMOVAL_POLICY
    || (() => { throw new Error("browser-condition-removal-policy.js is required."); })();

  function removeCondition(target, id) {
    try {
      const T = window.IRON_PIT_BROWSER_TIMED;
      for (const effect of [...target.state.timed_effects]) {
        if (effect.effect_id !== id) continue;
        const siblings = target.state.timed_effects.some((item) => item.source_id === effect.source_id
          && item.source_effect_id === effect.source_effect_id && item.effect_id !== id);
        if (effect.source_effect_id && !siblings) T.removeGroup(target.state, effect);
        else T.removeEffect(target.state, effect);
      }
      target.state.active_effect_ids = target.state.active_effect_ids.filter((item) => item !== id);
      if ((target.state.template.innate_condition_ids || []).includes(id)) target.state.active_effect_ids.push(id);
      if (id === "grappled") target.state.grapple_sources = [];
    } catch (error) {
      console.error("Failed to end condition", { target: target.combatant_id, id, error });
      throw error;
    }
  }
  function resolve(sequence, round, remover, target, action, conditionIds, turnKey) {
    try {
      if (action.actionCost === "reaction") throw new Error("Reaction cleansing requires a matching trigger.");
      if (!R().targetAllowed(remover, target, action) || !conditionIds?.length) throw new Error("Illegal condition-removal target.");
      if (!R().slotAvailable(remover, action, turnKey)) throw new Error("A spell slot was already expended to cast a spell this turn.");
      if (new Set(conditionIds).size !== conditionIds.length || conditionIds.length > (action.maxConditionsPerUse || 1)) {
        throw new Error("Condition-removal request exceeds its distinct-condition limit.");
      }
      const legal = new Set(R().removable(target, action));
      if (conditionIds.some((id) => !legal.has(id))) throw new Error("Condition-removal action cannot remove this effect.");
      if (!E().available(remover.state, action.actionCost) || !R().resourcesAvailable(remover, action, conditionIds.length)) {
        throw new Error("Condition-removal economy or resources are unavailable.");
      }
      E().spend(remover.state, action.actionCost);
      if (action.expendsSpellSlot) P().markSlotSpellCast(remover.state, turnKey);
      const payments = Object.entries(R().costs(action, conditionIds.length));
      payments.forEach(([id, cost]) => {
        if ((remover.state.resources[id] || 0) < cost) throw new Error(`Required resource ${id} is unavailable.`);
        remover.state.resources[id] -= cost;
      });
      const riders = new Set(["exhaustion", "curse", "ability-score-reduction", "hit-point-maximum-reduction"]);
      conditionIds.filter((id) => !riders.has(id)).forEach((id) => removeCondition(target, id));
      if (conditionIds.some((id) => riders.has(id))) {
        const wanted = new Set(conditionIds);
        if (wanted.has("exhaustion") && action.reducesExhaustionLevels && target.state.exhaustion_level) {
          window.IRON_PIT_BROWSER_EXHAUSTION.reduce(target.state, action.reducesExhaustionLevels);
        }
        if (wanted.has("curse") && target.state.active_curses?.length && (action.removesCurses || action.removesAllCurses)) {
          const removedCurses = action.removesAllCurses
            ? [...target.state.active_curses]
            : [target.state.active_curses[0]];
          for (const effect of [...(target.state.timed_effects || [])]) {
            if ((effect.owned_curse_ids || []).some((curseId) => removedCurses.includes(curseId))) {
              window.IRON_PIT_BROWSER_TIMED.removeGroup(target.state, effect);
            }
          }
          target.state.active_curses = target.state.active_curses.filter((curseId) => !removedCurses.includes(curseId));
        }
        if (wanted.has("ability-score-reduction") && action.removesAbilityScoreReductions
          && Object.keys(target.state.ability_score_reductions || {}).length) {
          const ability = Object.keys(target.state.ability_score_reductions).sort()[0];
          delete target.state.ability_score_reductions[ability];
        }
        if (wanted.has("hit-point-maximum-reduction") && action.removesHitPointMaximumReductions) {
          target.state.hit_point_maximum_reduction = 0;
          const maximum = window.IRON_PIT_BROWSER_STATE.effectiveMaxHp(target.state);
          if (target.state.current_hp > maximum) target.state.current_hp = maximum;
        }
      }
      if (action.endsRequiredEffect && action.requiresActiveEffectId) {
        const concentration = window.IRON_PIT_BROWSER_CONCENTRATION;
        if (!concentration) throw new Error("Break Enchantment requires browser-concentration.js.");
        concentration.end(remover.state);
      }
      const names = conditionIds.map((id) => id.replaceAll("_", " ").toUpperCase()).join(", ");
      return {
        sequence, round_number: round, event_type: "feature",
        actor_id: remover.combatant_id, actor_name: remover.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        removed_condition_ids: [...conditionIds], feature_id: action.id,
        resource_remaining: payments.length === 1 ? remover.state.resources[payments[0][0]] : null,
        animation: action.animation || "condition-removal",
        description: `${remover.state.template.name} uses ${action.name} on ${target.state.template.name}; ${names} ends.`,
      };
    } catch (error) {
      console.error("Condition removal rejected or failed", { remover: remover.combatant_id, target: target.combatant_id, action: action.id, error });
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_CONDITION_REMOVAL = {
    chooseAction: (...args) => R().chooseAction(...args),
    chooseReaction: (...args) => R().chooseReaction(...args),
    removeCondition,
    resolve,
  };
})();
