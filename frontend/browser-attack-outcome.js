(() => {
  "use strict";

  function emptyTopple() {
    return { saveRoll: null, saveDc: null, saveSucceeded: null, applied: false };
  }

  function create() {
    return {
      damageRoll: null,
      damageComponents: [],
      damageOutcome: null,
      hitSave: null,
      saveDamage: null,
      topple: emptyTopple(),
      sapApplied: "",
      vexApplied: false,
      studiedApplied: false,
      deferredEffectArmed: null,
      appliedConditions: [],
    };
  }

  function requireOutcome(ctx) {
    const outcome = ctx?.attackOutcome;
    if (!outcome || typeof outcome !== "object" || Array.isArray(outcome)) {
      throw new Error("Attack outcome hook requires a mutable attackOutcome object.");
    }
    if (!Array.isArray(outcome.damageComponents) || !Array.isArray(outcome.appliedConditions)) {
      throw new Error("Attack outcome accumulator has an invalid schema.");
    }
    if (!outcome.topple || typeof outcome.topple !== "object") {
      throw new Error("Attack outcome accumulator requires Topple state.");
    }
    return outcome;
  }

  function noEventResult(sequence) {
    if (!Number.isInteger(sequence) || sequence < 0) throw new Error("Attack outcome hook requires a valid sequence.");
    return { events: [], sequence, claimed: false };
  }

  function resolveD20(attackerState, defenderState, attack, attackRoll, baseTargetAc) {
    try {
      const originalNatural = attackRoll.selected_roll;
      const initialHit = originalNatural !== 1 && (originalNatural === 20 || attackRoll.total >= baseTargetAc);
      const parry = window.IRON_PIT_BROWSER_REACTIONS?.parryHit?.(
        defenderState, attack, attackRoll, initialHit, baseTargetAc,
      ) || { hit: initialHit, used: false };
      const grants = attackerState.template.failed_d20_test_override_grants || [];
      const eligible = grants.some((grant) => (grant.test_kinds || []).includes("attack"));
      if (eligible && !window.IRON_PIT_BROWSER_D20_TEST_OVERRIDE) {
        throw new Error("Failed-D20 override runtime is not loaded for a declared attack capability.");
      }
      const d20 = window.IRON_PIT_BROWSER_D20_TEST_OVERRIDE?.apply(
        attackerState, attackRoll, !parry.hit, "attack",
      ) || { roll: attackRoll, featureId: null, sourceName: null };
      const roll = d20.roll, natural = roll.selected_roll;
      const targetAc = baseTargetAc + (parry.used ? defenderState.template.parry_reaction.ac_bonus : 0);
      const revisedHit = d20.featureId ? (natural === 20 || roll.total >= targetAc) : parry.hit;
      const miss = window.IRON_PIT_BROWSER_MISS_TO_HIT_OVERRIDE?.apply(attackerState, revisedHit)
        || { hit: revisedHit, featureId: null, sourceName: null };
      return { roll, natural, targetAc, hit: miss.hit, parry, d20, miss };
    } catch (error) {
      console.error("Browser attack D20 outcome failed", { attacker: attackerState?.template?.name, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ATTACK_OUTCOME = {
    create, emptyTopple, noEventResult, requireOutcome, resolveD20,
  };
})();
