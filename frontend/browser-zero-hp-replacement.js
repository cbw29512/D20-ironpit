(() => {
  "use strict";

  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;

  function replacement(state) {
    return (state.active_modifiers || [])
      .filter((item) => item.kind === "zero-hp-replacement")
      .sort((a, b) => (b.replacement_hp || 0) - (a.replacement_hp || 0) || a.id.localeCompare(b.id))[0] || null;
  }

  function consumeModifier(state, modifier, reason) {
    M().removeSource([state], modifier.source_id, modifier.source_effect_id);
    state.active_buff_effect_ids = (state.active_buff_effect_ids || [])
      .filter((id) => id !== modifier.source_effect_id);
    const source = modifier.source_name || modifier.source_effect_id;
    state.pending_zero_hp_replacement_logs.push(`${source} ${reason}`);
  }

  function consumeZero(state) {
    const modifier = replacement(state);
    if (!modifier) return false;
    state.current_hp = modifier.replacement_hp;
    state.is_alive = true;
    state.is_dead = false;
    state.is_unconscious = false;
    state.is_stable = false;
    state.death_save_successes = 0;
    state.death_save_failures = 0;
    consumeModifier(
      state,
      modifier,
      `prevents the drop to 0 HP; ${state.template.name} remains at ${modifier.replacement_hp} HP.`,
    );
    return true;
  }

  function consumeInstantDeath(state) {
    const modifier = (state.active_modifiers || [])
      .filter((item) => item.kind === "zero-hp-replacement" && item.prevents_instant_death)
      .sort((a, b) => (b.replacement_hp || 0) - (a.replacement_hp || 0) || a.id.localeCompare(b.id))[0] || null;
    if (!modifier) return false;
    consumeModifier(state, modifier, `negates an instant-death effect against ${state.template.name}.`);
    return true;
  }

  function consumeLog(state) {
    const result = (state.pending_zero_hp_replacement_logs || []).join(" ");
    state.pending_zero_hp_replacement_logs = [];
    return result ? ` ${result}` : "";
  }

  window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT = { consumeInstantDeath, consumeLog, consumeZero };
})();
