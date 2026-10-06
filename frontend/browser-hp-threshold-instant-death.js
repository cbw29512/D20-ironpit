(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;
  const D = () => window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES;
  const DD = () => D()?.resolveDamage ? D() : (() => { throw new Error("HP-threshold fallback damage requires the shared damage resolver."); })();

  function legal(member, target, action) {
    try {
      // Visibility is source data, not a spell-name branch.
      const distance = F().saveDistance(member, target, action.range || 0);
      if (action.requiresTargetSight && !window.IRON_PIT_BROWSER_CONDITION_RULES.canSee(member.state, target.state, distance)) return false;
      if (!E().available(member.state, action.actionCost || "action")) return false;
      if (!target.state.is_alive || target.state.is_dead || target.state.current_hp <= 0) return false;
      if (target.state.current_hp > action.maxCurrentHp && !(action.fallbackDamageDiceCount || 0)) return false;
      if (distance > (action.range || 0)) return false;
      if (action.resourceId && (member.state.resources?.[action.resourceId] || 0) < (action.resourceCost || 1)) return false;
      return true;
    } catch (error) {
      console.error("HP-threshold target legality failed.", member.combatant_id, action.id, error);
      throw error;
    }
  }

  function choose(member, setup) {
    for (const action of member.state.template.hp_threshold_instant_death_actions || []) {
      const legalTargets = F().targetOrder(member, setup).filter((target) => legal(member, target, action));
      if (!legalTargets.length) continue;
      const primary = legalTargets[0];
      const targets = [primary];
      if ((action.maxTargets || 1) > 1) {
        for (const target of legalTargets.slice(1)) {
          if (action.secondaryTargetWithinFt != null
            && F().saveDistance(primary, target, action.secondaryTargetWithinFt) > action.secondaryTargetWithinFt) {
            continue;
          }
          targets.push(target);
          if (targets.length >= action.maxTargets) break;
        }
      }
      return { target: primary, targets, action };
    }
    return null;
  }

  function spendOnce(member, action) {
    if (action.resourceId) member.state.resources[action.resourceId] -= (action.resourceCost || 1);
    E().spend(member.state, action.actionCost || "action");
    return action.resourceId ? member.state.resources[action.resourceId] : null;
  }

  function resolveTarget(sequence, round, member, target, action, setup, remaining) {
    const hpBefore = target.state.current_hp;
    const states = [...setup.heroes, ...setup.monsters].map((item) => item.state);
    const fallback = target.state.current_hp > action.maxCurrentHp;
    let prevented = false, damageRoll = null, damageComponents = [];
    if (fallback) {
      const rolls = window.IRON_PIT_DICE.rollMany(action.fallbackDamageDiceCount, action.fallbackDamageDiceSize);
      const raw = rolls.reduce((sum, value) => sum + value, 0) + (action.fallbackDamageBonus || 0);
      const resolved = DD().resolveDamage(target.state, raw, action.fallbackDamageType);
      const applied = resolved.applied;
      damageRoll = {
        notation: `${action.fallbackDamageDiceCount}d${action.fallbackDamageDiceSize}`,
        rolls, modifier: action.fallbackDamageBonus || 0, total: applied,
      };
      damageComponents = [{
        source: action.name, notation: damageRoll.notation, rolls,
        modifier: action.fallbackDamageBonus || 0, damage_type: action.fallbackDamageType,
        total: raw, applied_total: applied,
        absorbed_healing: resolved.healed || 0,
        absorption_source_name: resolved.sourceName || null,
      }];
      if (applied) Z().applyDamage(target.state, applied, false, [action.fallbackDamageType], states);
    } else {
      prevented = Z().applyInstantDeath(target.state, states) === "zero_hp_replacement";
    }
    const wardLog = window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT?.consumeLog(target.state) || "";
    return {
      sequence, round_number: round, event_type: "feature",
      actor_id: member.combatant_id, actor_name: member.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name,
      hp_before: hpBefore, hp_after: target.state.current_hp, is_dead: target.state.is_dead,
      damage_roll: damageRoll, damage_components: damageComponents,
      feature_id: action.id, resource_remaining: remaining,
      animation: action.animation || "instant-death",
      description: member.state.template.name + " uses " + action.name + " on " + target.state.template.name + "; "
        + (fallback
          ? target.state.template.name + " takes " + damageRoll.total + " " + action.fallbackDamageType + " damage."
          : (prevented ? target.state.template.name + "'s ward negates the instant-death effect." : target.state.template.name + " dies."))
        + wardLog,
    };
  }

  function resolve(sequence, round, member, target, action, setup) {
    if (!legal(member, target, action)) throw new Error(action.name + " is no longer legal.");
    const remaining = spendOnce(member, action);
    return resolveTarget(sequence, round, member, target, action, setup, remaining);
  }

  function resolveGroup(sequence, round, member, targets, action, setup) {
    if (!targets.length || targets.length > (action.maxTargets || 1)) throw new Error("Illegal threshold target count.");
    if (targets.some((target) => !legal(member, target, action))) throw new Error("Illegal threshold target.");
    if (action.secondaryTargetWithinFt != null && targets.length > 1) {
      const primary = targets[0];
      if (targets.slice(1).some((target) =>
        F().saveDistance(primary, target, action.secondaryTargetWithinFt) > action.secondaryTargetWithinFt)) {
        throw new Error("Threshold secondary target violates linked-target distance.");
      }
    }
    const remaining = spendOnce(member, action);
    return targets.map((target, index) =>
      resolveTarget(sequence + index, round, member, target, action, setup, remaining));
  }

  function installProvider() {
    const selection = window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
    if (!selection) throw new Error("HP-threshold instant-death provider requires main-action selection.");
    selection.registerProvider({
      id: "hp-threshold-instant-death",
      category: selection.CATEGORIES.HP_THRESHOLD_INSTANT_DEATH,
      rulesets: ["2014", "2024"],
      discover: ({ member, setup }) => {
        const selected = choose(member, setup);
        return selected ? {
          payload: {
            targetIds: selected.targets.map((target) => target.combatant_id),
            actionId: selected.action.id,
          },
        } : null;
      },
      resolve: ({ sequence, round, member, setup }, candidate) => {
        const ids = candidate.payload.targetIds || [candidate.payload.targetId];
        const targets = ids.map((id) =>
          [...setup.heroes, ...setup.monsters].find((item) => item.combatant_id === id) || null);
        const action = (member.state.template.hp_threshold_instant_death_actions || [])
          .find((item) => item.id === candidate.payload.actionId) || null;
        if (targets.some((target) => !target) || !action) throw new Error("HP-threshold instant-death candidate became unavailable.");
        const events = resolveGroup(sequence, round, member, targets, action, setup);
        return { events, sequence: sequence + events.length };
      },
    });
  }

  window.IRON_PIT_BROWSER_HP_THRESHOLD_INSTANT_DEATH = {
    choose, installProvider, legal, resolve, resolveGroup,
  };
})();
