((root) => {
  "use strict";

  function appliesToTarget(effect, targetActorId = null) {
    try { return !effect.target_actor_id || effect.target_actor_id === targetActorId; }
    catch (error) { console.error("Preview effect target match failed", error); throw error; }
  }

  function resolveRollMode(baseMode = "normal", activeEffects = [], targetActorId = null) {
    try {
      let hasAdvantage = baseMode === "advantage";
      let hasDisadvantage = baseMode === "disadvantage";
      for (const effect of activeEffects || []) {
        if (!appliesToTarget(effect, targetActorId)) continue;
        if (effect.kind === "advantage") hasAdvantage = true;
        if (effect.kind === "disadvantage") hasDisadvantage = true;
      }
      if (hasAdvantage === hasDisadvantage) return "normal";
      return hasAdvantage ? "advantage" : "disadvantage";
    } catch (error) { console.error("Preview roll-mode resolution failed", error); throw error; }
  }

  function applySap(target, sourceActorId) {
    try {
      target.attackRollEffects = (target.attackRollEffects || []).filter(
        (effect) => !(effect.id === "sap" && effect.source_actor_id === sourceActorId),
      );
      target.attackRollEffects.push({
        id: "sap", source_actor_id: sourceActorId, kind: "disadvantage",
        target_actor_id: null, consume_on_attack: true,
        expires_at_start_of_source_turn: true, source_turns_remaining: null,
      });
    } catch (error) { console.error("Preview Sap application failed", error); throw error; }
  }

  function applyVex(actor, sourceActorId, targetActorId) {
    try {
      actor.attackRollEffects = (actor.attackRollEffects || []).filter(
        (effect) => !(effect.id === "vex" && effect.target_actor_id === targetActorId),
      );
      actor.attackRollEffects.push({
        id: "vex", source_actor_id: sourceActorId, kind: "advantage",
        target_actor_id: targetActorId, consume_on_attack: true,
        expires_at_start_of_source_turn: false, source_turns_remaining: 2,
      });
    } catch (error) { console.error("Preview Vex application failed", error); throw error; }
  }

  function applyWeaponMastery(actor, target, weapon, damageTotal) {
    try {
      if (!actor.template.weapon_masteries?.includes(weapon.id)) return null;
      if (weapon.masteryProperty === "sap") {
        applySap(target, actor.template.id);
        return "sap";
      }
      if (weapon.masteryProperty === "vex" && damageTotal > 0) {
        applyVex(actor, actor.template.id, target.template.id);
        return "vex";
      }
      return null;
    } catch (error) { console.error("Preview mastery application failed", error); throw error; }
  }

  function consumeAttackEffects(actor, targetActorId = null) {
    try {
      actor.attackRollEffects = (actor.attackRollEffects || []).filter(
        (effect) => !(effect.consume_on_attack && appliesToTarget(effect, targetActorId)),
      );
    } catch (error) { console.error("Preview attack-effect consumption failed", error); throw error; }
  }

  function expireAtSourceTurn(combatants, sourceActorId) {
    try {
      for (const combatant of combatants) {
        combatant.attackRollEffects = (combatant.attackRollEffects || []).filter(
          (effect) => !(effect.expires_at_start_of_source_turn && effect.source_actor_id === sourceActorId),
        );
      }
    } catch (error) { console.error("Preview turn-start effect expiry failed", error); throw error; }
  }

  function endSourceTurn(combatants, sourceActorId) {
    try {
      for (const combatant of combatants) {
        const retained = [];
        for (const effect of combatant.attackRollEffects || []) {
          if (effect.source_actor_id !== sourceActorId || effect.source_turns_remaining == null) retained.push(effect);
          else if (effect.source_turns_remaining > 1) {
            effect.source_turns_remaining -= 1;
            retained.push(effect);
          }
        }
        combatant.attackRollEffects = retained;
      }
    } catch (error) { console.error("Preview turn-end effect expiry failed", error); throw error; }
  }

  const api = {
    applySap, applyVex, applyWeaponMastery, consumeAttackEffects,
    endSourceTurn, expireAtSourceTurn, resolveRollMode,
  };
  root.IRON_PIT_EFFECTS = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
