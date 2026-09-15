(() => {
  "use strict";

  const D = () => window.IRON_PIT_DICE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const members = (setup) => [...setup.heroes, ...setup.monsters];
  const marker = (action) => `death-trigger:${action.id}`;

  function pending(setup) {
    const found = [];
    for (const source of members(setup)) {
      if (!source.state.is_dead) continue;
      for (const action of source.state.template.death_trigger_actions || []) {
        if (!source.state.feature_last_turn_keys[marker(action)]) found.push({ source, action });
      }
    }
    return found;
  }

  function targets(source, action, setup) {
    return members(setup).filter((target) => target.combatant_id !== source.combatant_id
      && target.state.is_alive && !target.state.is_dead
      && S().distance(source, target) <= action.range);
  }

  function resolvePending(sequence, round, setup) {
    try {
      const events = [];
      while (true) {
        const work = pending(setup);
        if (!work.length) return { events, sequence };
        for (const { source, action } of work) {
          source.state.feature_last_turn_keys[marker(action)] = "fired";
          const count = action.damageDiceCount || 0;
          const sharedDamageRolls = count
            ? Array.from({ length: count }, () => D().roll(action.damageDiceSize))
            : null;
          for (const target of targets(source, action, setup)) {
            const event = V().resolveAction(
              sequence++, round, source, target, action, S().distance(source, target), {
                spendAction: false, checkResource: false, spendResource: false,
                sharedDamageRolls, setup,
              },
            );
            events.push(event);
          }
        }
      }
    } catch (error) {
      console.error("Failed browser death-trigger resolution", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DEATH_TRIGGERS = { resolvePending };
})();