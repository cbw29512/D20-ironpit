(() => {
  "use strict";

  const members = (setup) => [...(setup?.heroes || []), ...(setup?.monsters || [])];

  function clear(target) {
    try {
      const effectId = target.state.damage_share_effect_id;
      const sourceId = target.state.damage_share_source_id;
      target.state.damage_share_source_id = null;
      target.state.damage_share_range_ft = 0;
      target.state.damage_share_effect_id = null;
      if (effectId && sourceId) {
        window.IRON_PIT_BROWSER_MODIFIERS?.removeSource([target.state], sourceId, effectId);
        for (const effect of [...(target.state.timed_effects || [])]) {
          if (effect.source_id === sourceId && effect.source_effect_id === effectId) {
            window.IRON_PIT_BROWSER_TIMED?.removeEffect(target.state, effect);
          }
        }
        target.state.active_buff_effect_ids = (target.state.active_buff_effect_ids || [])
          .filter((item) => item !== effectId);
      }
    } catch (error) {
      console.error("Failed to clear damage share.", { target: target?.combatant_id, error });
      throw error;
    }
  }

  function resolve(target, amount, setup) {
    try {
      const sourceId = target.state.damage_share_source_id;
      const rangeFt = target.state.damage_share_range_ft || 0;
      if (!sourceId || amount <= 0 || rangeFt <= 0) return 0;
      const source = members(setup).find((member) => member.combatant_id === sourceId);
      if (!source || source.combatant_id === target.combatant_id) return 0;
      if (source.state.is_dead || !source.state.is_alive || source.state.current_hp <= 0) {
        clear(target);
        return 0;
      }
      if (window.IRON_PIT_BROWSER_STATE.distance(target, source) > rangeFt) {
        clear(target);
        return 0;
      }
      window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(
        source.state, amount, false, [], members(setup).map((member) => member.state),
      );
      if (source.state.current_hp <= 0 || source.state.is_dead) clear(target);
      return amount;
    } catch (error) {
      console.error("Failed to share damage.", { target: target?.combatant_id, error });
      throw error;
    }
  }

  function resolveForState(targetState, amount, setup) {
    try {
      if (!setup || !targetState.damage_share_source_id) return 0;
      const target = members(setup).find((member) => member.state === targetState);
      return target ? resolve(target, amount, setup) : 0;
    } catch (error) {
      console.error("Failed state-level damage share lookup.", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DAMAGE_SHARE = { clear, resolve, resolveForState };
})();
