(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function sourceName(effect) {
    return String(effect.source_effect_id || effect.effect_id)
      .split("-")
      .map((part) => part ? part[0].toUpperCase() + part.slice(1) : "")
      .join(" ");
  }

  function consume(state, nondamageInstantDeath = false) {
    try {
      const effect = (state.timed_effects || []).find((item) =>
        (item.zero_hp_replacement_hp || 0) > 0
        && (!nondamageInstantDeath || item.prevents_nondamage_instant_death),
      );
      if (!effect) return false;
      T().removeGroup(state, effect);
      state.current_hp = effect.zero_hp_replacement_hp;
      state.is_alive = true;
      state.is_dead = false;
      state.is_unconscious = false;
      state.is_stable = false;
      const outcome = nondamageInstantDeath
        ? "negates the instant-death effect"
        : `keeps ${state.template.name} at ${effect.zero_hp_replacement_hp} HP`;
      state.pending_survival_save_logs.push(` ${sourceName(effect)} ${outcome}.`);
      return true;
    } catch (error) {
      console.error("Browser survival-ward resolution failed.", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SURVIVAL_WARDS = { consume };
})();
