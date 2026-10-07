(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const P = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const WAKE_SLEEPER_ACTION = {
    id: "wake-sleeper", name: "Wake Sleeper", actionCost: "action", range: 5,
    targetMode: "ally", removableConditions: ["unconscious"], maxConditionsPerUse: 1,
    resourceCosts: {}, resourceCostsPerCondition: {}, expendsSpellSlot: false,
    requiresExplicitEffectPermission: true, animation: "condition-removal",
  };

  const PRIORITY = {
    paralyzed: 0, stunned: 0, incapacitated: 0, petrified: 0,
    blinded: 1, restrained: 1, poisoned: 2, frightened: 2, charmed: 2,
    deafened: 3, grappled: 3, prone: 4, exhaustion: 4, curse: 4,
    "ability-score-reduction": 5, "hit-point-maximum-reduction": 5,
  };

  const distance = (a, b) => window.IRON_PIT_BROWSER_STATE.distance(a, b);
  const allies = (member, setup) => member.side === "heroes" ? setup.heroes : setup.monsters;

  function targetAllowed(remover, target, action) {
    try {
      if (!target.state.is_alive || target.state.is_dead || target.side !== remover.side) return false;
      const type = String(target.state.template.creature_type || "").split(" (")[0].trim().toLowerCase();
      if ((action.excludedCreatureTypes || []).some(kind => kind.toLowerCase() === type)) return false;
      if (distance(remover, target) > action.range) return false;
      if (action.targetMode === "self") return target.combatant_id === remover.combatant_id;
      if (action.targetMode === "ally") return target.combatant_id !== remover.combatant_id;
      if (action.requiresActiveEffectId) {
        const required = action.requiresActiveEffectId;
        const active = (remover.state.active_effect_ids || []).includes(required);
        const concentrating = remover.state.concentration?.effect_id === required;
        if (!active && !concentrating) return false;
      }
      return true;
    } catch (error) {
      console.error("Failed removal target legality", { remover: remover.combatant_id, target: target.combatant_id, action: action.id, error });
      throw error;
    }
  }

  function costs(action, count) {
    const result = { ...(action.resourceCosts || {}) };
    Object.entries(action.resourceCostsPerCondition || {}).forEach(([id, cost]) => {
      result[id] = (result[id] || 0) + cost * count;
    });
    return result;
  }

  function resourcesAvailable(member, action, count) {
    return Object.entries(costs(action, count)).every(([id, cost]) => (member.state.resources[id] || 0) >= cost);
  }

  function effectAllows(target, conditionId, action) {
    const effects = target.state.timed_effects.filter((effect) => effect.effect_id === conditionId);
    if (action.requiresExplicitEffectPermission) {
      return effects.length > 0 && effects.every((effect) =>
        (effect.allowed_removal_action_ids || []).includes(action.id),
      );
    }
    return effects.every((effect) =>
      !effect.allowed_removal_action_ids?.length || effect.allowed_removal_action_ids.includes(action.id),
    );
  }

  function removable(target, action) {
    const allowed = new Set(action.removableConditions || []);
    const effects = [...new Set(target.state.active_effect_ids)]
      .filter((id) => allowed.has(id) && effectAllows(target, id, action));
    if (action.reducesExhaustionLevels && target.state.exhaustion_level) effects.push("exhaustion");
    if ((action.removesCurses || action.removesAllCurses) && target.state.active_curses?.length) effects.push("curse");
    if (action.removesAbilityScoreReductions && Object.keys(target.state.ability_score_reductions || {}).length) {
      effects.push("ability-score-reduction");
    }
    if (action.removesHitPointMaximumReductions && target.state.hit_point_maximum_reduction) {
      effects.push("hit-point-maximum-reduction");
    }
    return effects.sort((a, b) => (PRIORITY[a] ?? 9) - (PRIORITY[b] ?? 9) || a.localeCompare(b));
  }

  function affordable(member, target, action) {
    const result = removable(target, action).slice(0, action.maxConditionsPerUse || 1);
    while (result.length && !resourcesAvailable(member, action, result.length)) result.pop();
    return result;
  }

  function slotAvailable(remover, action, turnKey) {
    return !action.expendsSpellSlot || P().slotSpellAvailable(remover.state, turnKey);
  }

  function chooseAction(remover, setup, turnKey) {
    const choices = [];
    for (const action of [WAKE_SLEEPER_ACTION, ...(remover.state.template.condition_removal_actions || [])]) {
      if (action.actionCost === "reaction" || !E().available(remover.state, action.actionCost)) continue;
      if (!slotAvailable(remover, action, turnKey)) continue;
      for (const target of allies(remover, setup)) {
        if (!targetAllowed(remover, target, action)) continue;
        const conditions = affordable(remover, target, action);
        if (conditions.length) choices.push({ action, target, conditions });
      }
    }
    choices.sort((a, b) => {
      const urgency = (PRIORITY[a.conditions[0]] ?? 9) - (PRIORITY[b.conditions[0]] ?? 9);
      if (urgency) return urgency;
      const economy = (a.action.actionCost === "bonus_action" ? 0 : 1) - (b.action.actionCost === "bonus_action" ? 0 : 1);
      if (economy) return economy;
      if (a.conditions.length !== b.conditions.length) return b.conditions.length - a.conditions.length;
      return distance(remover, a.target) - distance(remover, b.target);
    });
    return choices[0] || null;
  }

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
      if (id === "grappled") target.state.grapple_sources = [];
    } catch (error) {
      console.error("Failed to end condition", { target: target.combatant_id, id, error });
      throw error;
    }
  }

  function resolve(sequence, round, remover, target, action, conditionIds, turnKey) {
    try {
      if (action.actionCost === "reaction") throw new Error("Reaction cleansing requires a matching trigger.");
      if (!targetAllowed(remover, target, action) || !conditionIds?.length) throw new Error("Illegal condition-removal target.");
      if (!slotAvailable(remover, action, turnKey)) throw new Error("A spell slot was already expended to cast a spell this turn.");
      if (new Set(conditionIds).size !== conditionIds.length || conditionIds.length > (action.maxConditionsPerUse || 1)) {
        throw new Error("Condition-removal request exceeds its distinct-condition limit.");
      }
      const legal = new Set(removable(target, action));
      if (conditionIds.some((id) => !legal.has(id))) throw new Error("Condition-removal action cannot remove this effect.");
      if (!E().available(remover.state, action.actionCost) || !resourcesAvailable(remover, action, conditionIds.length)) {
        throw new Error("Condition-removal economy or resources are unavailable.");
      }
      E().spend(remover.state, action.actionCost);
      if (action.expendsSpellSlot) P().markSlotSpellCast(remover.state, turnKey);
      const payments = Object.entries(costs(action, conditionIds.length));
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
          target.state.active_curses = action.removesAllCurses ? [] : target.state.active_curses.slice(1);
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

  function chooseReaction(remover, setup, trigger, affectedTarget, turnKey) {
    if (!E().available(remover.state, "reaction")) return null;
    const actions = (remover.state.template.condition_removal_actions || []).filter((action) =>
      action.actionCost === "reaction" && action.reactionTrigger === trigger && slotAvailable(remover, action, turnKey),
    );
    for (const action of actions) {
      if (!targetAllowed(remover, affectedTarget, action)) continue;
      const conditions = affordable(remover, affectedTarget, action);
      if (conditions.length) return { action, target: affectedTarget, conditions };
    }
    return null;
  }

  window.IRON_PIT_BROWSER_CONDITION_REMOVAL = { chooseAction, chooseReaction, removeCondition, resolve };
})();
