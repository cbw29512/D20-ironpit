(() => {
  "use strict";

  const WEAPON_EFFECT_ID = "weapon-mastery-sap";
  const TACTICAL_EFFECT_ID = "tactical-master-sap";
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const W = () => window.IRON_PIT_BROWSER_WEAPON_MASTERY;

  function applyEffect(attackerId, target, round, effectId, sourceEffectId) {
    void round; void sourceEffectId;
    if (target.state.is_dead || target.state.current_hp <= 0) return false;
    const before = M().nextAttackDisadvantage(target.state);
    M().add(target.state, {
      id: `${attackerId}:${effectId}`, source_id: attackerId, source_effect_id: effectId,
      kind: "next-attack-disadvantage", expires_at_start_of_source_turn: true,
    });
    return M().nextAttackDisadvantage(target.state) > before;
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
  const consume = (state) => M().consumeNextAttackDisadvantage(state);

  function applyTactical(attacker, target, attack, round) {
    if (!selected(attacker.state, attack)) return false;
    return applyEffect(attacker.combatant_id, target, round, TACTICAL_EFFECT_ID, "tactical-master");
  }

  window.IRON_PIT_BROWSER_SAP = { applyEffect, applyWeapon, consume, disadvantage, weaponEligible };
  window.IRON_PIT_BROWSER_TACTICAL_MASTER = { apply: applyTactical, eligible: selected, selected };
})();
