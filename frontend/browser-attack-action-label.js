(() => {
  "use strict";
  // Label universal additional Attack Action slots, not monster-specific attacks.
  // The first slot remains "Attack"; later slots belong to Extra Attack.
  function featureId(definition, variant, slotIndex) {
    try {
      if (!Number.isInteger(slotIndex) || slotIndex < 1)
        throw new Error("Attack slot index must be a positive integer.");
      if (!definition || !variant?.id)
        throw new Error("Attack feature attribution requires a source action.");
      return definition.isAttackAction && slotIndex > 1 ? "extra-attack" : variant.id;
    } catch (error) {
      console.error("Failed universal Attack Action feature attribution.", error);
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_ATTACK_ACTION_LABEL = {featureId};
})();
