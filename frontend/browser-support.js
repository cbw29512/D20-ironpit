(() => {
  "use strict";

  const H = () => window.IRON_PIT_BROWSER_HEALING;
  const C = () => window.IRON_PIT_BROWSER_CONDITION_REMOVAL;

  function resolve(sequence, round, member, setup) {
    const events = [];

    // RAW does not impose this priority; this is Iron Pit's deterministic support AI.
    // A dying ally is rescued first, then debilitating removable conditions are cleared,
    // then ordinary healing can use any remaining Action/Bonus Action economy.
    let healing = H()?.chooseAction(member, setup);
    if (healing?.target.state.current_hp === 0) {
      events.push(H().resolve(sequence++, round, member, healing.target, healing.action));
    }

    const removal = C()?.chooseAction(member, setup);
    if (removal) {
      events.push(C().resolve(sequence++, round, member, removal.target, removal.action, removal.conditions));
    }

    healing = H()?.chooseAction(member, setup);
    if (healing) {
      events.push(H().resolve(sequence++, round, member, healing.target, healing.action));
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_SUPPORT = { resolve };
})();
