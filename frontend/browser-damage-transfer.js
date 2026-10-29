(function () {
  "use strict";

  function members(setup) {
    return [...(setup.heroes || []), ...(setup.monsters || [])];
  }

  function resolve(state, amount, setup) {
    try {
      if (!amount || amount <= 0) return amount;
      const sourceId = state.template?.id || state.combatant_id;
      const victim = members(setup).find((member) =>
        (member.state.grapple_sources || []).some((g) => g.source_id === sourceId)
      );
      if (!victim || victim.state.is_dead) return amount;
      const keeps = Math.floor(amount / 2);
      const takes = amount - keeps;
      if (takes > 0) {
        window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(
          victim.state, takes, false, [], members(setup).map((m) => m.state), setup
        );
      }
      return keeps;
    } catch (error) {
      console.error("Failed to resolve Damage Transfer.", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DAMAGE_TRANSFER = { resolve };
})();
