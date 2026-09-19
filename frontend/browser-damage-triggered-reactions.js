(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const S = () => window.IRON_PIT_BROWSER_STATE;

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
    try {
      const distance = S().distance(reactor, source);
      for (const attack of reactor.state.template.attacks || []) {
        if (attack.kind !== "melee") continue;
        if (!attackAllowedAgainst(attack, reactor, source)) continue;
        if (distance > (attack.reach || 5)) continue;
        return { attack, distance };
      }
      return null;
    } catch (error) {
      console.error("Browser damage-triggered melee attack selection failed", {
        reactor: reactor?.combatant_id, source: source?.combatant_id, error,
      });
      throw error;
    }
  }

  function resolve(sequence, round, reactor, source, setup, turnKey = null) {
    try {
      const rule = reactor.state.template.damage_triggered_melee_reaction;
      if (!rule || !E().available(reactor.state, "reaction")) return null;
      if (source.combatant_id === reactor.combatant_id) return null;
      if (!source.state.is_alive || source.state.is_dead || source.state.current_hp <= 0) return null;
      if (S().distance(reactor, source) > rule.trigger_range_ft) return null;
      const selected = meleeAttackAgainstSource(reactor, source);
      if (!selected) return null;
      E().spend(reactor.state, "reaction");
      return A().resolveAttack(sequence, round, reactor, source, selected.attack, selected.distance, {
        spendAction: false,
        featureId: rule.id,
        setup,
        turnKey,
        allowReckless: false,
        offTurn: true,
        ignoreCloseThreat: true,
      });
    } catch (error) {
      console.error("Browser damage-triggered melee reaction failed", {
        reactor: reactor?.combatant_id, source: source?.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DAMAGE_TRIGGERED_REACTIONS = {
    attackAllowedAgainst, meleeAttackAgainstSource, resolve,
  };
})();
