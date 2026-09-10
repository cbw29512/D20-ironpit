(() => {
  "use strict";
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || {
    has: (state, id) => state.active_effect_ids?.includes(id) === true,
  };
  const V = () => window.IRON_PIT_BROWSER_VISIBILITY;

  function sourceIds(state) {
    if (!Q().has(state, "frightened")) return [];
    const ids = [...new Set((state.timed_effects || [])
      .filter((effect) => effect.effect_id === "frightened")
      .map((effect) => effect.source_id))];
    if (!ids.length) throw new Error("Active Frightened condition lacks source-bound lifecycle state.");
    return ids;
  }

  function sources(state, setup) {
    const members = new Map([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
    return sourceIds(state).map((id) => {
      const source = members.get(id);
      if (!source) throw new Error(`Frightened source ${id} is missing from the encounter.`);
      return source;
    });
  }

  function d20Disadvantage(state, setup) {
    if (!V()) throw new Error("Browser visibility runtime is not loaded.");
    return sources(state, setup).some((source) => V().hasLineOfSight(state, source.state)) ? 1 : 0;
  }

  window.IRON_PIT_BROWSER_FRIGHTENED = { sourceIds, sources, d20Disadvantage };
})();
