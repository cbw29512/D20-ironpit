(() => {
  "use strict";

  // UI-only projection of fight state. Never changes the combat engine.
  const el = (id) => document.getElementById(id);

  function update(state) {
    try {
      const ready = state.heroSlots.some(Boolean) && state.monsterSlots.some(Boolean);
      const active = Boolean(state.session && !state.session.complete);
      const stoppable = Boolean(state.fighting && state.liveFightRunning);
      const fight = el("fight-button");
      fight.textContent = stoppable ? "Stop Fight" : "Fight";
      fight.disabled = !stoppable && (state.fighting || active || !ready);
      for (const id of ["step-fight-button", "turbo-button"])
        el(id).disabled = state.fighting || active || !ready;
      el("rerun-button").disabled = state.fighting || active || !state.hasRun;
      el("quick-test").disabled = state.fighting || active;
      if (el("bag-all-button")) el("bag-all-button").disabled = state.fighting || active;
      el("load-combat-button").disabled = state.fighting || active
        || !window.IRON_PIT_COMBAT_PRESETS?.selected?.();
      for (const id of ["reset-fight", "reset-board"])
        el(id).disabled = state.fighting;
      window.IRON_PIT_RULESET_UI?.syncDisabled(state);
      window.IRON_PIT_COMBAT_PRESETS?.sync(state);
    } catch (error) {
      console.error("Could not synchronize player battle controls", error);
      throw error;
    }
  }

  window.IRON_PIT_PLAYER_CONTROL_STATE = {update};
})();