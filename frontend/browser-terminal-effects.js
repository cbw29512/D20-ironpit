(() => {
  "use strict";

  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const RF = () => window.IRON_PIT_BROWSER_REPLACEMENT_FORMS;

  function applyTerminalDeath(state, affectedStates = []) {
    if (state.is_dead) return "unchanged";
    state.current_hp = 0;
    state.is_alive = false;
    state.is_dead = true;
    state.is_unconscious = false;
    state.is_stable = false;
    state.active_effect_ids = (state.active_effect_ids || []).filter((id) => id !== "dodge");
    RF()?.revertIfIncapacitated(state);
    if (state.concentration && C()) C().endIfIncapacitated(state, affectedStates);
    return "dead";
  }

  function applyTerminalEffectTag(state, effectTag, affectedStates = []) {
    const normalized = String(effectTag || "").trim().toLowerCase();
    if (!normalized) throw new Error("Terminal effect tag must be non-empty.");
    const tags = (state.template.terminal_effect_tags || [])
      .map((item) => String(item).trim().toLowerCase())
      .filter(Boolean);
    if (!tags.includes(normalized)) return "not_susceptible";
    return applyTerminalDeath(state, affectedStates);
  }

  window.IRON_PIT_BROWSER_TERMINAL_EFFECTS = { applyTerminalDeath, applyTerminalEffectTag };
})();
