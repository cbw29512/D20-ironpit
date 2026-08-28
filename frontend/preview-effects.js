((root) => {
  "use strict";

  function resolveRollMode(baseMode = "normal", activeEffects = []) {
    try {
      let hasAdvantage = baseMode === "advantage";
      let hasDisadvantage = baseMode === "disadvantage";
      for (const effect of activeEffects || []) {
        if (effect.kind === "advantage") hasAdvantage = true;
        if (effect.kind === "disadvantage") hasDisadvantage = true;
      }
      if (hasAdvantage === hasDisadvantage) return "normal";
      return hasAdvantage ? "advantage" : "disadvantage";
    } catch (error) {
      console.error("Preview roll-mode resolution failed", error);
      throw error;
    }
  }

  function applySap(target, sourceActorId) {
    try {
      target.attackRollEffects = (target.attackRollEffects || []).filter(
        (effect) => !(effect.id === "sap" && effect.source_actor_id === sourceActorId),
      );
      target.attackRollEffects.push({
        id: "sap",
        source_actor_id: sourceActorId,
        kind: "disadvantage",
        consume_on_attack: true,
        expires_at_start_of_source_turn: true,
      });
    } catch (error) {
      console.error("Preview Sap application failed", error);
      throw error;
    }
  }

  function consumeAttackEffects(actor) {
    try {
      actor.attackRollEffects = (actor.attackRollEffects || []).filter(
        (effect) => !effect.consume_on_attack,
      );
    } catch (error) {
      console.error("Preview attack-effect consumption failed", error);
      throw error;
    }
  }

  function expireAtSourceTurn(combatants, sourceActorId) {
    try {
      for (const combatant of combatants) {
        combatant.attackRollEffects = (combatant.attackRollEffects || []).filter(
          (effect) => !(
            effect.expires_at_start_of_source_turn
            && effect.source_actor_id === sourceActorId
          ),
        );
      }
    } catch (error) {
      console.error("Preview turn-start effect expiry failed", error);
      throw error;
    }
  }

  const api = { applySap, consumeAttackEffects, expireAtSourceTurn, resolveRollMode };
  root.IRON_PIT_EFFECTS = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
