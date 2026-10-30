(() => {
  "use strict";
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;

  function apply(state, sourceId, attack, round, turnOwnerId) {
    try {
      for (const [index, effect] of (attack.onHitSelfModifiers || []).entries()) {
        M().applyEffect(state, sourceId, attack.id, effect, index, "self-hit", round, turnOwnerId);
      }
    } catch (error) {
      console.error("Failed browser source hit modifiers.", { attack: attack?.id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SELF_HIT_MODIFIERS = { apply };
})();
