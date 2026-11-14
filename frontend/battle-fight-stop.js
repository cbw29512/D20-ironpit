(() => {
  "use strict";

  // State contract: a live Fight may request cancellation while the current
  // animation event finishes. Resolved engine evidence is immutable; only the
  // events actually displayed to the player are retained as the partial log.
  const el = (id) => document.getElementById(id);

  function begin(state, mode) {
    state.liveFightRunning = mode === "watch";
    state.stopFightRequested = false;
  }

  function request(api) {
    if (!api.state.liveFightRunning || !api.state.fighting) return false;
    try {
      api.state.stopFightRequested = true;
      api.state.session?.stop?.();
      el("status").textContent = "Stopping after the current combat event…";
      return true;
    } catch (error) {
      console.error("Could not request stop for the active fight", error);
      throw error;
    }
  }

  function beforeResolve(state) {
    if (!state.stopFightRequested) return false;
    el("status").textContent = "Fight stopped before the first event. No combat log was recorded.";
    return true;
  }

  function afterWatch(api, session, writeProgress) {
    if (!session.stopped && !api.state.stopFightRequested) return false;
    try {
      // Do NOT use the final engine outcome here. It contains future events
      // which have not been shown and would falsely imply a completed fight.
      writeProgress(session);
      api.state.hasRun = session.eventIndex > 0;
      const count = session.eventIndex, total = session.battle.events.length;
      el("lab-summary").textContent = `Stopped · ${count} / ${total} events viewed.`;
      el("status").textContent = count
        ? `Fight stopped after ${count} events. Partial combat log preserved.`
        : "Fight stopped before any combat events.";
      return true;
    } catch (error) {
      console.error("Could not preserve the stopped fight's partial log", error);
      throw error;
    }
  }

  function finish(state) {
    state.liveFightRunning = false;
    state.stopFightRequested = false;
  }

  window.IRON_PIT_FIGHT_STOP = { begin, request, beforeResolve, afterWatch, finish };
})();