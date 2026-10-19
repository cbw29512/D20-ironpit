(() => {
  "use strict";
  function resolve(source, target, rule, resolveSave) {
    try {
      if (!source.state.is_dead || source.state.current_hp !== 0) throw new Error("Death trigger source is not dead.");
      if (target.state.is_dead) return null;
      return resolveSave(rule.save, { spendAction: false, checkResource: false, spendResource: false });
    } catch (error) {
      console.error("Death trigger save failed", error);
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_DEATH_TRIGGER_SAVE = { resolve };
})();
