(() => {
  "use strict";

  function resolveEntries(sequence, round, mover, setup, turnKey) {
    try {
      const events = [];
      window.IRON_PIT_BROWSER_EMANATION_SPEED?.sync(setup);
      if (!mover.state.is_alive || mover.state.is_dead) return { events, sequence };
      for (const source of [...setup.heroes, ...setup.monsters]) {
        if (source.side === mover.side) continue;
        const activeIds = new Set((source.state.timed_effects || [])
          .filter((effect) => effect.source_id === source.combatant_id && effect.source_effect_id)
          .map((effect) => effect.source_effect_id));
        for (const action of source.state.template.timed_self_buff_actions || []) {
          const emanation = action.startTurnEmanationDamage;
          if (!activeIds.has(action.id) || !emanation || emanation.trigger !== "enter_or_start") continue;
          const result = window.IRON_PIT_BROWSER_EMANATION_SAVE_DAMAGE.resolveHit(
            sequence, round, source, mover, action, setup, turnKey,
          );
          if (result.event) {
            events.push(result.event);
            sequence = result.sequence;
          }
        }
      }
      return { events, sequence };
    } catch (error) {
      console.error("Emanation entry resolution failed.", { mover: mover?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_EMANATION_ENTER = { resolveEntries };
})();
