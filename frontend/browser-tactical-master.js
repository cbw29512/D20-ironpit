(() => {
  "use strict";

  const WEAPON_EFFECT_ID = "weapon-mastery-sap";
  const TACTICAL_EFFECT_ID = "tactical-master-sap";
  const SAP_EFFECT_IDS = new Set([WEAPON_EFFECT_ID, TACTICAL_EFFECT_ID]);
  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function applyEffect(attackerId, target, round, effectId, sourceEffectId) {
    if (target.state.is_dead || target.state.current_hp <= 0) return false;
    return Boolean(T().apply(target.state, effectId, attackerId, {
      sourceEffectId, appliedRound: round, expiresRound: round + 1, expiryTiming: "source_turn_start",
    }));
  }

  function weaponEligible(state, attack) {
    return attack.masteryProperty === "Sap"
      && Boolean(attack.weaponId)
      && (state.template.weapon_masteries || []).includes(attack.weaponId);
  }

  function applyWeapon(attacker, target, attack, round) {
    if (!weaponEligible(attacker.state, attack)) return false;
    return applyEffect(attacker.combatant_id, target, round, WEAPON_EFFECT_ID, "weapon-mastery");
  }

  const disadvantage = (state) => state.timed_effects.some((effect) => SAP_EFFECT_IDS.has(effect.effect_id)) ? 1 : 0;

  function consume(state) {
    const effects = state.timed_effects.filter((effect) => SAP_EFFECT_IDS.has(effect.effect_id));
    for (const effect of [...effects]) T().removeEffect(state, effect);
    return effects.length;
  }

  function tacticalEligible(state, attack) {
    return Boolean(state.template.tactical_master_sap)
      && Boolean(attack.weaponId)
      && (state.template.weapon_masteries || []).includes(attack.weaponId);
  }

  function applyTactical(attacker, target, attack, round) {
    if (!tacticalEligible(attacker.state, attack)) return false;
    return applyEffect(attacker.combatant_id, target, round, TACTICAL_EFFECT_ID, "tactical-master");
  }

  window.IRON_PIT_BROWSER_SAP = { applyEffect, applyWeapon, consume, disadvantage, weaponEligible };
  window.IRON_PIT_BROWSER_TACTICAL_MASTER = { apply: applyTactical, eligible: tacticalEligible };
})();
