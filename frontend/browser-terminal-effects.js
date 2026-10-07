(() => {
  "use strict";

  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const RF = () => window.IRON_PIT_BROWSER_REPLACEMENT_FORMS;

  function applyTerminalDeath(state, affectedStates = []) {
    try {
      if (state.is_dead) return "unchanged";
      // Missing lifecycle dependencies must not silently preserve an active buff.
      if (state.concentration && !C()?.endIfIncapacitated) throw new Error("Browser concentration runtime is not loaded.");
      if (state.replacement_form && !RF()?.revertIfIncapacitated) throw new Error("Browser replacement-form runtime is not loaded.");
      state.current_hp = 0;
      state.is_alive = false;
      state.is_dead = true;
      state.is_unconscious = false;
      state.is_stable = false;
      state.active_effect_ids = (state.active_effect_ids || []).filter((id) => id !== "dodge");
      RF()?.revertIfIncapacitated(state);
      if (state.concentration) C().endIfIncapacitated(state, affectedStates);
      return "dead";
    } catch (error) {
      console.error("Browser terminal-death resolution failed", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  function applyTerminalEffectTag(state, effectTag, affectedStates = []) {
    try {
      const normalized = String(effectTag || "").trim().toLowerCase();
      if (!normalized) throw new Error("Terminal effect tag must be non-empty.");
      const tags = (state.template.terminal_effect_tags || [])
        .map((item) => String(item).trim().toLowerCase())
        .filter(Boolean);
      if (!tags.includes(normalized)) return "not_susceptible";
      return applyTerminalDeath(state, affectedStates);
    } catch (error) {
      console.error("Browser terminal effect-tag resolution failed", { combatant: state?.template?.name, effectTag, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TERMINAL_EFFECTS = { applyTerminalDeath, applyTerminalEffectTag };
})();
