(() => {
  "use strict";
  function resolve(source, target, rule, resolveSave) {
    try {
      // A terminal effect can kill a creature while positive HP remains.
      // Death is a fight-state transition, not a numeric HP equality.
      if (!source.state.is_dead) throw new Error("Death trigger source is not dead.");
      if (target.state.is_dead) return null;
      return resolveSave(rule.save, { spendAction: false, checkResource: false, spendResource: false });
    } catch (error) {
      console.error("Death trigger save failed", error);
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_DEATH_TRIGGER_SAVE = { resolve };
})();
