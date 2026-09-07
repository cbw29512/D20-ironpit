(() => {
  "use strict";

  const WEAPON_EFFECT_ID = "weapon-mastery-sap";
  const TACTICAL_EFFECT_ID = "tactical-master-sap";
  const SAP_EFFECT_IDS = new Set([WEAPON_EFFECT_ID, TACTICAL_EFFECT_ID]);
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const W = () => window.IRON_PIT_BROWSER_WEAPON_MASTERY;

  function applyEffect(attackerId, target, round, effectId, sourceEffectId) {
    void sourceEffectId;
    if (target.state.is_dead || target.state.current_hp <= 0) return false;
    const before = M().nextAttackDisadvantage(target.state);
    M().add(target.state, {
      id: `${attackerId}:${effectId}`, source_id: attackerId, source_effect_id: effectId,
      kind: "next-attack-disadvantage", expires_at_start_of_source_turn: true,
    });
    const named = T().apply(target.state, effectId, attackerId, {
      sourceEffectId: effectId, appliedRound: round, expiresRound: round + 1, expiryTiming: "source_turn_start",
    });
    return Boolean(named) || M().nextAttackDisadvantage(target.state) > before;
  }

  function selected(state, attack) {
    return W().mastered(state, attack)
      && (state.template.tactical_master_sap_weapon_ids || []).includes(attack.weaponId);
  }

  function weaponEligible(state, attack) {
    return W().active(state, attack, "Sap");
  }

  function applyWeapon(attacker, target, attack, round) {
    if (!weaponEligible(attacker.state, attack)) return false;
    return applyEffect(attacker.combatant_id, target, round, WEAPON_EFFECT_ID, "weapon-mastery");
  }

  const disadvantage = (state) => M().nextAttackDisadvantage(state);

  function consume(state) {
    const removed = M().consumeNextAttackDisadvantage(state);
    for (const effect of [...state.timed_effects]) if (SAP_EFFECT_IDS.has(effect.effect_id)) T().removeEffect(state, effect);
    return removed;
  }

  function applyTactical(attacker, target, attack, round) {
    if (!selected(attacker.state, attack)) return false;
    return applyEffect(attacker.combatant_id, target, round, TACTICAL_EFFECT_ID, "tactical-master");
  }

  window.IRON_PIT_BROWSER_SAP = { applyEffect, applyWeapon, consume, disadvantage, weaponEligible };
  window.IRON_PIT_BROWSER_TACTICAL_MASTER = { apply: applyTactical, eligible: selected, selected };
})();
