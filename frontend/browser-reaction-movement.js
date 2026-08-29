(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const X = () => window.IRON_PIT_BROWSER_REACTIONS;
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;

  function preview(mover, target, desired) {
    if (desired < 0) throw new Error("Desired distance cannot be negative.");
    const before = S().distance(mover, target);
    const moved = Math.min(Math.max(0, before - desired), mover.state.movement_remaining_ft);
    const direction = mover.position_ft < target.position_ft ? 1 : -1;
    return { position: mover.position_ft + direction * moved, moved };
  }

  function moveToward(sequence, round, mover, target, setup, desired, movementSource = "speed", options = {}) {
    const proposal = preview(mover, target, desired);
    if (!proposal.moved) return { events: [], sequence, movement: null };
    const events = [], wasProne = mover.state.active_effect_ids.includes("prone");
    if (setup && X()) {
      const reactors = mover.side === "heroes" ? setup.monsters : setup.heroes;
      for (const reactor of reactors) {
        const before = Math.abs(reactor.position_ft - mover.position_ft);
        const after = Math.abs(reactor.position_ft - proposal.position);
        const event = X().resolveOpportunityAttack(
          sequence, round, reactor, mover, setup, before, after, movementSource, options,
        );
        if (!event) continue;
        events.push(event); sequence += 1;
        const newlyProne = !wasProne && mover.state.active_effect_ids.includes("prone");
        if (mover.state.is_dead || mover.state.is_unconscious || G()?.speedIsZero(mover.state) || newlyProne) {
          return { events, sequence, movement: null };
        }
      }
    }
    const movement = S().moveToward(mover, target, desired);
    return { events, sequence, movement };
  }

  window.IRON_PIT_BROWSER_REACTION_MOVEMENT = { moveToward };
})();
