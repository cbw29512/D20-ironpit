(() => {
  "use strict";

  const DE = () => window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT;

  function resolve(sequence, round, actor, setup) {
    try {
      const rule = actor.state.template?.deferred_save_effect || null;
      if (!rule?.allow_attack_slot_activation) return null;
      const runtime = DE();
      if (!runtime) throw new Error("Deferred-effect attack-slot runtime requires browser-deferred-save-effect.js.");
      const target = runtime.candidate(actor, setup, { requireAction: false });
      if (!target) return null;
      return runtime.resolve(sequence, round, actor, setup, target.combatant_id, { spendAction: false });
    } catch (error) {
      console.error("Browser deferred-effect attack-slot activation failed", {
        combatant: actor?.combatant_id,
        error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DEFERRED_ATTACK_SLOT = { resolve };
})();
