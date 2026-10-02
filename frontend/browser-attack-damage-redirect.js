(() => {
  "use strict";

  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const V = () => window.IRON_PIT_BROWSER_SAVES;

  function attackById(source, attackId) {
    try {
      if (!attackId) return null;
      return (source?.state?.template?.attacks || []).find((attack) => attack.id === attackId) || null;
    } catch (error) {
      console.error("Browser zero-damage redirect attack lookup failed", { attackId, error });
      throw error;
    }
  }

  function legalTargets(reactor, setup, rangeFt, rule) {
    try {
      const opponents = reactor.side === "heroes" ? setup.monsters : setup.heroes;
      return opponents
        .filter((target) => target.state.is_alive && !target.state.is_dead && target.state.current_hp > 0)
        .filter((target) => S().distance(reactor, target) <= rangeFt)
        .filter((target) => !rule.requiresSight || Q().canSee(reactor.state, target.state))
        .filter((target) => !rule.requiresClearLine
          || !window.IRON_PIT_BROWSER_GRID_BARRIERS
          || window.IRON_PIT_BROWSER_GRID_BARRIERS.clearBetweenMembers(reactor, target, setup))
        .sort((a, b) => S().distance(reactor, a) - S().distance(reactor, b)
          || String(a.combatant_id).localeCompare(String(b.combatant_id)));
    } catch (error) {
      console.error("Browser zero-damage redirect target selection failed", {
        reactor: reactor?.combatant_id, error,
      });
      throw error;
    }
  }

  function resolve(sequence, round, source, triggeringEvent, setup) {
    try {
      if (!triggeringEvent?.damage_reduction_zeroed_attack) return null;
      const members = [...(setup?.heroes || []), ...(setup?.monsters || [])];
      const reactor = members.find((member) => member.combatant_id === triggeringEvent.target_id) || null;
      if (!reactor) return null;

      const reduction = reactor.state.template.attackDamageReductionReaction;
      const rule = reduction?.zeroDamageRedirect || null;
      if (!rule) return null;

      const current = reactor.state.resources?.[rule.resourceId] || 0;
      if (current < (rule.resourceCost || 1)) return null;

      const attack = attackById(source, triggeringEvent.attack_id);
      if (!attack) return null;
      const rangeFt = attack.kind === "melee" ? rule.meleeRangeFt : rule.rangedRangeFt;
      const targets = legalTargets(reactor, setup, rangeFt, rule);
      if (!targets.length) return null;

      const score = reactor.state.template.ability_scores?.[rule.damageBonusAbility];
      const damageBonus = rule.damageBonusAbility
        ? Math.floor((score - 10) / 2)
        : 0;
      if (rule.damageBonusAbility && !Number.isInteger(score)) {
        throw new Error(`${rule.sourceName} requires a certified ${rule.damageBonusAbility} score.`);
      }

      const action = {
        id: rule.sourceId,
        name: rule.sourceName,
        actionCost: "reaction",
        saveAbility: rule.saveAbility,
        dc: rule.saveDc,
        range: rangeFt,
        damageDiceCount: rule.damageDiceCount,
        damageDiceSize: rule.damageDiceSize,
        damageBonus,
        damageType: attack.damageType,
        successDamage: "none",
        resourceId: rule.resourceId,
        resourceCost: rule.resourceCost || 1,
        requiresTargetSight: Boolean(rule.requiresSight),
        animation: "deflect",
      };
      const target = targets[0];
      return V().resolveAction(
        sequence,
        round,
        reactor,
        target,
        action,
        S().distance(reactor, target),
        { spendAction: false, setup },
      );
    } catch (error) {
      console.error("Browser zero-damage attack redirect failed", {
        source: source?.combatant_id, eventSequence: triggeringEvent?.sequence, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ATTACK_DAMAGE_REDIRECT = { attackById, legalTargets, resolve };
})();
