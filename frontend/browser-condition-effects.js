(() => {
  "use strict";

  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function markProne(state) {
    if (I().immune(state, "prone")) return null;
    if (!state.active_effect_ids.includes("prone")) state.active_effect_ids.push("prone");
    return "prone";
  }

  function applyHit(target, attackerId, attack, extra = {}) {
    const state = target.state;
    if (!state.is_alive || state.is_dead) return [];
    const applied = [];
    const proneMaxSize = extra.proneMaxSize || attack.proneMaxSize;
    if (S().canProne(target, proneMaxSize)) {
      const prone = markProne(state);
      if (prone) applied.push(prone);
    }
    const control = attack.controlEffect;
    if (control?.grappleEscapeDc && (!control.maxTargetSize || S().sizeAtMost(target, control.maxTargetSize))) {
      applied.push(...G().apply(state, attackerId, control.grappleEscapeDc, attack.reach || 5, Boolean(control.restrainsWhileGrappled)));
    }
    if (control?.conditionId) {
      const timed = T().apply(state, control.conditionId, attackerId, Boolean(control.expiresAtStartOfSourceTurn));
      if (timed) applied.push(timed);
    }
    return [...new Set(applied)];
  }

  window.IRON_PIT_BROWSER_CONDITION_EFFECTS = { applyHit, markProne };
})();
