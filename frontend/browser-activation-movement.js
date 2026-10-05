(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_REACTION_MOVEMENT;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;

  function resolve(sequence, round, mover, setup, options = {}) {
    try {
      const speedFraction = Number(options.speedFraction || 0);
      const desiredDistanceFt = options.desiredDistanceFt ?? 5;
      if (!(speedFraction > 0 && speedFraction <= 1)) throw new Error("Activation movement speedFraction must be in (0, 1].");
      const opponents = mover.side === "heroes" ? setup.monsters : setup.heroes;
      const living = opponents.filter((member) => !member.state.is_dead && !member.state.is_unconscious);
      if (!living.length) return { events: [], sequence };
      living.sort((a, b) => S().distance(mover, a) - S().distance(mover, b) || a.combatant_id.localeCompare(b.combatant_id));
      const target = living[0];
      const allowance = G()?.speedIsZero?.(mover.state) ? 0 : Math.floor(M().effectiveSpeed(mover.state) * speedFraction);
      if (allowance <= 0) return { events: [], sequence };
      const normalRemaining = mover.state.movement_remaining_ft;
      mover.state.movement_remaining_ft = allowance;
      try {
        const result = R().moveToward(sequence, round, mover, target, setup, desiredDistanceFt, "speed", { turnKey: options.turnKey, disengaged: options.provokesOpportunityAttacks === false });
        return { events: result.events, sequence: result.sequence };
      } finally {
        mover.state.movement_remaining_ft = normalRemaining;
      }
    } catch (error) {
      console.error("Browser activation-triggered movement failed", { mover: mover?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ACTIVATION_MOVEMENT = { resolve };
})();
