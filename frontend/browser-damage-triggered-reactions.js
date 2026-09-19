(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function reactorCanReact(state) {
    return Boolean(
      state?.is_alive
      && !state.is_dead
      && state.current_hp > 0
      && !Q()?.incapacitated?.(state)
    );
  }

  function attackAllowedAgainst(attack, reactor, source) {
    try {
      if (!attack?.forbidSelfGrappledTarget) return true;
      return !(source.state.grapple_sources || []).some(
        (grapple) => grapple.source_id === reactor.combatant_id,
      );
    } catch (error) {
      console.error("Browser damage-reaction target legality failed", {
        reactor: reactor?.combatant_id, source: source?.combatant_id, attack: attack?.id, error,
      });
      throw error;
    }
  }

  function meleeAttackAgainstSource(reactor, source) {
    const distance = S().distance(reactor, source);
    for (const attack of reactor.state.template.attacks || []) {
      if (attack.kind !== "melee") continue;
      if (!attackAllowedAgainst(attack, reactor, source)) continue;
      if (distance > (attack.reach || 5)) continue;
      return { attack, distance };
    }
    return null;
  }

  function eligible(reactor, source, appliedDamage) {
    const rule = reactor?.state?.template?.damage_reaction_attack;
    if (!rule || rule.attack_kind !== "melee") return false;
    if (!(appliedDamage > 0)) return false;
    if (!source || source.combatant_id === reactor.combatant_id) return false;
    if (!source.state?.is_alive || source.state.is_dead || source.state.current_hp <= 0) return false;
    if (!reactorCanReact(reactor.state)) return false;
    if (!E().available(reactor.state, "reaction")) return false;
    const distance = S().distance(reactor, source);
    return distance >= 0 && distance <= rule.source_range_ft;
  }

  function resolve(sequence, round, reactor, source, setup, appliedDamage, turnKey = null) {
    try {
      if (!eligible(reactor, source, appliedDamage)) return null;
      const rule = reactor.state.template.damage_reaction_attack;
      const selected = meleeAttackAgainstSource(reactor, source);
      if (!selected) return null;
      E().spend(reactor.state, "reaction");
      return A().resolveAttack(sequence, round, reactor, source, selected.attack, selected.distance, {
        spendAction: false,
        featureId: rule.source_feature,
        setup,
        turnKey,
        allowReckless: false,
        offTurn: true,
        ignoreCloseThreat: true,
      });
    } catch (error) {
      console.error("Browser damage reaction resolution failed", {
        reactor: reactor?.combatant_id, source: source?.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DAMAGE_TRIGGERED_REACTIONS = {
    attackAllowedAgainst, eligible, meleeAttackAgainstSource, reactorCanReact, resolve,
  };
})();