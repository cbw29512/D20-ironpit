(() => {
  "use strict";
  // Source identity is a combatant ID, not an ability's printed name.
  function validate(observerId, sourceId, turn) {
    try {
      if (typeof observerId !== "string" || !observerId.trim()) throw Error("Invalid observer ID");
      if (typeof sourceId !== "string" || !sourceId.trim()) throw Error("Invalid visual source ID");
      if (!Number.isInteger(turn) || turn < 0) throw Error("Invalid observer turn");
    } catch (error) { console.error("Invalid visual aversion input", error); throw error; }
  }
  function checked(windows) {
    try {
      if (!Array.isArray(windows)) throw Error("Invalid visual aversion state");
      for (const w of windows) {
        if (!w || typeof w !== "object") throw Error("Invalid visual aversion window");
        validate(w.observerId, w.sourceId, w.expiresOnObserverTurnStart);
      }
      return windows;
    } catch (error) { console.error("Invalid visual aversion state", error); throw error; }
  }
  function record(windows, observerId, sourceId, turn) {
    try {
      validate(observerId, sourceId, turn);
      const retained = checked(windows).filter(w =>
        !(w.observerId === observerId && w.sourceId === sourceId) &&
        !(w.observerId === observerId && w.expiresOnObserverTurnStart <= turn));
      return [...retained, { observerId, sourceId, expiresOnObserverTurnStart: turn + 1 }];
    } catch (error) { console.error("Failed recording visual aversion", error); throw error; }
  }
  function active(windows, observerId, sourceId, turn) {
    try {
      validate(observerId, sourceId, turn);
      return checked(windows).some(w => w.observerId === observerId && w.sourceId === sourceId &&
        turn < w.expiresOnObserverTurnStart);
    } catch (error) { console.error("Failed checking visual aversion", error); throw error; }
  }
  function perceive(windows, observerId, sourceId, turn, visualSight, nonvisualPerception) {
    try {
      if (typeof visualSight !== "boolean" || typeof nonvisualPerception !== "boolean") {
        throw Error("Perception facts must be booleans");
      }
      checked(windows); // Invalid sourced aversion state must fail closed even without visual sight.
      const visual = visualSight && !active(windows, observerId, sourceId, turn);
      return { visualSight: visual, canPerceive: visual || nonvisualPerception };
    } catch (error) { console.error("Failed source-scoped visual perception", error); throw error; }
  }
  function attackDisadvantage(windows, observerId, targetId, turn) {
    return active(windows, observerId, targetId, turn) ? 1 : 0;
  }
  window.IRON_PIT_BROWSER_VISUAL_SOURCE_AVERSION = { record, active, perceive, attackDisadvantage };
})();
