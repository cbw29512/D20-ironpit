(() => {
  "use strict";

  function sync(setup) {
    try {
      const wanted = new Set();
      const members = [...setup.heroes, ...setup.monsters];
      for (const source of members) {
        const activeIds = new Set((source.state.timed_effects || [])
          .filter((effect) => effect.source_id === source.combatant_id && effect.source_effect_id)
          .map((effect) => effect.source_effect_id));
        for (const action of source.state.template.timed_self_buff_actions || []) {
          const emanation = action.startTurnEmanationDamage;
          if (!activeIds.has(action.id) || !emanation || !(emanation.speed_multiplier < 1)) continue;
          const enemies = source.side === "heroes" ? setup.monsters : setup.heroes;
          for (const target of enemies) {
            if (!target.state.is_alive || target.state.is_dead) continue;
            if (window.IRON_PIT_BROWSER_STATE.distance(source, target) > emanation.radius_ft) continue;
            const modifierId = `${source.combatant_id}:${action.id}:speed:${target.combatant_id}`;
            wanted.add(modifierId);
            if ((target.state.active_modifiers || []).some((item) => item.id === modifierId)) continue;
            window.IRON_PIT_BROWSER_MODIFIERS.add(target.state, {
              id: modifierId, source_id: source.combatant_id, source_effect_id: action.id,
              source_name: action.name, source_is_magical: true, kind: "speed-multiplier",
              multiplier: emanation.speed_multiplier, concentration_required: Boolean(action.concentration),
            });
          }
        }
      }
      for (const member of members) {
        member.state.active_modifiers = (member.state.active_modifiers || []).filter((item) => !(
          item.kind === "speed-multiplier"
          && item.id.includes(":speed:")
          && item.id.endsWith(`:speed:${member.combatant_id}`)
          && !wanted.has(item.id)
        ));
      }
    } catch (error) {
      console.error("Failed to sync emanation speed multipliers.", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_EMANATION_SPEED = { sync };
})();
