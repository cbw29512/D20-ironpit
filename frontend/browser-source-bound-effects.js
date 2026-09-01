(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const C = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };

  function endDamageSensitive(state) {
    const removed = [], handled = new Set();
    for (const effect of [...state.timed_effects]) {
      const key = `${effect.source_id}|${effect.source_effect_id || ""}`;
      if (!effect.ends_on_damage || handled.has(key)) continue;
      handled.add(key); removed.push(...T().removeGroup(state, effect));
    }
    return removed;
  }

  function cleanupDisabledSources(setup) {
    const members = [...setup.heroes, ...setup.monsters];
    const byId = new Map(members.map((member) => [member.combatant_id, member]));
    for (const target of members) {
      const handled = new Set();
      for (const effect of [...target.state.timed_effects]) {
        const key = `${effect.source_id}|${effect.source_effect_id || ""}`;
        if (handled.has(key)) continue;
        const source = byId.get(effect.source_id); if (!source) continue;
        const dead = source.state.is_dead || !source.state.is_alive;
        const incapacitated = C().incapacitated(source.state);
        if ((effect.ends_if_source_dead && dead) || (effect.ends_if_source_incapacitated && incapacitated)) {
          handled.add(key); T().removeGroup(target.state, effect);
        }
      }
    }
  }

  window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS = { cleanupDisabledSources, endDamageSensitive };
})();
