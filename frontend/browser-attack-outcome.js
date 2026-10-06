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
      exileApplied: null,
      postHitSelfBuffApplied: null,
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

  function resolveD20(
    attackerState, defenderState, attack, attackRoll, baseTargetAc,
    attackerMember = null, setup = null,
  ) {
    try {
      const originalNatural = attackRoll.selected_roll;
      const initialHit = originalNatural !== 1 && (originalNatural === 20 || attackRoll.total >= baseTargetAc);
      const parry = window.IRON_PIT_BROWSER_REACTIONS?.parryHit?.(
        defenderState, attack, attackRoll, initialHit, baseTargetAc,
      ) || { hit: initialHit, used: false };
      const targetAc = baseTargetAc + (parry.used ? defenderState.template.parry_reaction.ac_bonus : 0);
      let preAdjustmentRoll = attackRoll;
      let preAdjustmentHit = parry.hit;
      const attackBonusRules = (attackerState.template.resource_backed_d20_bonus_dice || [])
        .filter((rule) => (rule.test_kinds || []).includes("attack"));
      if (!preAdjustmentHit && ![1, 20].includes(originalNatural) && attackBonusRules.length) {
        const bonus = window.IRON_PIT_BROWSER_D20_BONUS_DICE;
        if (!bonus) throw new Error("Resource-backed d20 bonus runtime is not loaded for attacks.");
        preAdjustmentRoll = bonus.applyResourceBackedIfUseful(
          attackerState, "attack", preAdjustmentRoll, targetAc,
        ).roll;
        preAdjustmentHit = preAdjustmentRoll.total >= targetAc;
      }
      const adjustment = attackerMember && setup
        ? window.IRON_PIT_BROWSER_D20_OUTCOME_ADJUSTMENTS?.applyIfUseful(
            attackerMember, setup, "attack", preAdjustmentRoll, targetAc, originalNatural,
          ) || { roll: preAdjustmentRoll, featureId: null, sourceName: null }
        : { roll: preAdjustmentRoll, featureId: null, sourceName: null };
      attackRoll = adjustment.roll;
      const adjustedNatural = attackRoll.selected_roll;
      const adjustedHit = adjustedNatural !== 1
        && (adjustedNatural === 20 || attackRoll.total >= targetAc);
      const grants = attackerState.template.failed_d20_test_override_grants || [];
      const eligible = grants.some((grant) => (grant.test_kinds || []).includes("attack"));
      if (eligible && !window.IRON_PIT_BROWSER_D20_TEST_OVERRIDE) {
        throw new Error("Failed-D20 override runtime is not loaded for a declared attack capability.");
      }
      const d20 = window.IRON_PIT_BROWSER_D20_TEST_OVERRIDE?.apply(
        attackerState, attackRoll, !adjustedHit, "attack",
      ) || { roll: attackRoll, featureId: null, sourceName: null };
      const roll = d20.roll, natural = roll.selected_roll;
      const revisedHit = d20.featureId ? (natural === 20 || roll.total >= targetAc) : adjustedHit;
      const miss = window.IRON_PIT_BROWSER_MISS_TO_HIT_OVERRIDE?.apply(attackerState, revisedHit)
        || { hit: revisedHit, featureId: null, sourceName: null };
      return { roll, natural, targetAc, hit: miss.hit, parry, adjustment, d20, miss };
    } catch (error) {
      console.error("Browser attack D20 outcome failed", { attacker: attackerState?.template?.name, error });
      throw error;
    }
  }

  function buildEvent(ctx) {
    try {
      const { sequence, round, attacker, target, actualTarget, attack, targetAc, resolvedAttackRoll,
        hit, critical, naturalOne, naturalOneEndsTurn, automaticHit, outcomeAdjustment, d20Override,
        override, heroic, d20Bonus, rollPenalty, recklessStarted, redirected, parry, damageRoll,
        damageComponents, damageOutcome, hitSave, saveDamage, topple, sapApplied, vexApplied,
        studiedApplied, deferredEffectArmed, exileApplied, maximumHpSave, contestedMovement,
        cunningStrikeTrip, cunningStrikeObscure, applied, hpBefore, temporaryHpBefore,
        deathSuccessBefore, deathFailureBefore, concentrationBefore, extra, outcome } = ctx;
      const attackSave = saveDamage?.saveDc != null ? saveDamage
        : hitSave?.saveDc != null ? hitSave
        : maximumHpSave?.saveDc != null ? maximumHpSave
        : cunningStrikeObscure?.saveDc != null ? {
            saveRoll: cunningStrikeObscure.saveRoll, saveAbility: "dexterity",
            saveDc: cunningStrikeObscure.saveDc, saveSucceeded: cunningStrikeObscure.saveSucceeded,
          }
        : cunningStrikeTrip?.saveDc != null ? {
            saveRoll: cunningStrikeTrip.saveRoll, saveAbility: "dexterity",
            saveDc: cunningStrikeTrip.saveDc, saveSucceeded: cunningStrikeTrip.saveSucceeded,
          }
        : null;
      const survivalLog = window.IRON_PIT_BROWSER_UNDEAD_FORTITUDE?.consumeLog(actualTarget.state) || "";
      let description = `${attacker.state.template.name}: ${critical ? "CRITICAL HIT" : hit ? "HIT" : "MISS"} with ${attack.name}.`;
      if (automaticHit) description += " The attack automatically hits its source-owned Grappled target.";
      if (outcomeAdjustment?.featureId) description += ` ${outcomeAdjustment.sourceName || outcomeAdjustment.featureId} adjusts the attack roll by ${outcomeAdjustment.adjustmentTotal}.`;
      if (d20Override.featureId) description += ` ${d20Override.sourceName || d20Override.featureId} turns the failed attack roll into a 20.`;
      else if (override.featureId) description += ` ${override.sourceName || override.featureId} turns the miss into a hit.`;
      else if (naturalOneEndsTurn) description += " Natural 1: Iron Pit immediately ends the attacker's turn.";
      else if (naturalOne) description += " Natural 1: automatic miss; this off-turn attack does not terminate a future turn.";
      if (heroic.used) description += " Heroic Inspiration rerolls one d20.";
      if (d20Bonus?.sourceName) description += ` ${d20Bonus.sourceName} adds its bonus die to the attack roll.`;
      if (rollPenalty?.restorationName) description += ` ${rollPenalty.sourceName} uses ${rollPenalty.restorationName}.`;
      if (rollPenalty) description += ` ${rollPenalty.sourceName} uses ${rollPenalty.actionId} to subtract ${rollPenalty.penaltyTotal} from the attack roll.`;
      if (!hit && damageRoll !== null) description += ` Graze deals ${damageRoll.total} ${attack.damageType} damage.`;
      if (studiedApplied) description += ` Studied Attacks primes the next attack against ${target.state.template.name}.`;
      if (outcome.damageReductionReaction) description += ` ${actualTarget.state.template.name} uses ${outcome.damageReductionReaction.damageReductionReactionSourceName || "Reaction"} to reduce the attack's damage by ${outcome.damageReductionReaction.damageReductionReactionReduction}.`;
      if (recklessStarted) description += ` ${attacker.state.template.name} uses Reckless Attack.`;
      if (outcome.brutalStrikeEffects?.length) description += ` Brutal Strike applies ${outcome.brutalStrikeEffects.map((item) => item.replaceAll("-", " ").replace(/\b\w/g, (c) => c.toUpperCase())).join(", ")}.`;
      if (redirected) description += ` ${target.state.template.name} uses Redirect Attack; ${actualTarget.state.template.name} becomes the target.`;
      if (parry.used) description += ` ${actualTarget.state.template.name} uses Parry.`;
      if (sapApplied === "weapon") description += ` Sap mastery affects ${actualTarget.state.template.name}.`;
      if (sapApplied === "tactical") description += ` Tactical Master applies Sap to ${actualTarget.state.template.name}.`;
      if (vexApplied) description += ` Vex primes the next attack against ${actualTarget.state.template.name}.`;
      if (deferredEffectArmed) description += ` ${deferredEffectArmed.sourceName} is armed on ${actualTarget.state.template.name}; ${deferredEffectArmed.resourceRemaining} uses remain.`;
      if (exileApplied) description += ` ${actualTarget.state.template.name} is Banished by ${exileApplied.sourceName} until the source-relative return point.`;
      if (outcome.postHitSelfBuffApplied) description += ` ${outcome.postHitSelfBuffApplied.sourceName} activates.`;
      if (attackSave) description += ` ${attackSave.saveAbility} save DC ${attackSave.saveDc}: ${actualTarget.state.template.name} ${attackSave.saveSucceeded ? "succeeds" : "fails"}.`;
      if (hitSave?.forcedMovementFt) description += ` ${actualTarget.state.template.name} is pushed ${hitSave.forcedMovementFt} feet away.`;
      if (maximumHpSave?.reductionApplied) description += ` ${actualTarget.state.template.name}'s hit point maximum is reduced by ${maximumHpSave.reductionApplied}.`;
      if (maximumHpSave?.killedByZeroMaximum) description += ` ${actualTarget.state.template.name} dies as its hit point maximum reaches 0.`;
      if (contestedMovement?.targetRoll) {
        description += ` ${actualTarget.state.template.name} ${contestedMovement.targetSucceeded ? "wins" : "loses"} the ${contestedMovement.targetAbility} contest (${contestedMovement.targetRoll.total} vs ${contestedMovement.sourceRoll.total}).`;
        if (contestedMovement.movementFt) description += ` ${actualTarget.state.template.name} is moved ${contestedMovement.movementFt} feet ${contestedMovement.direction === "toward_source" ? "toward the source" : "away from the source"}.`;
      }
      if (topple.saveDc !== null) description += ` Topple save DC ${topple.saveDc}: ${actualTarget.state.template.name} ${topple.saveSucceeded ? "succeeds" : "fails"}.`;
      if (damageOutcome === "relentless_endurance") description += ` ${actualTarget.state.template.name} uses Relentless Endurance and remains at 1 HP.`;
      if (damageOutcome === "undead_fortitude") description += ` ${actualTarget.state.template.name} succeeds on Undead Fortitude and remains at 1 HP.`;
      for (const condition of [...new Set(applied)]) description += ` ${actualTarget.state.template.name} is ${condition === "prone" ? "knocked Prone" : condition === "restrained" ? "Restrained while Grappled" : condition.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase())}.`;
      return { sequence, round_number: round, event_type: "attack", actor_id: attacker.combatant_id, actor_name: attacker.state.template.name,
        target_id: actualTarget.combatant_id, target_name: actualTarget.state.template.name, attack_name: attack.name, target_ac: targetAc,
        attack_roll: resolvedAttackRoll, saving_throw_roll: attackSave?.saveRoll || topple.saveRoll, save_ability: attackSave?.saveAbility || (topple.saveDc === null ? null : "constitution"), save_dc: attackSave?.saveDc || topple.saveDc, save_succeeded: attackSave?.saveSucceeded ?? topple.saveSucceeded,
        damage_roll: damageRoll, damage_components: damageComponents, applied_condition_ids: [...new Set(applied)], hit, critical, damage_reduction_zeroed_attack: Boolean(outcome.damageReductionReaction?.damageReductionZeroedAttack),
        turn_terminated: naturalOneEndsTurn, turn_termination_reason: naturalOneEndsTurn ? "iron-pit-natural-1-attack" : null,
        hp_before: hpBefore, hp_after: actualTarget.state.current_hp, temporary_hp_before: temporaryHpBefore, temporary_hp_after: actualTarget.state.temporary_hp,
        death_save_successes_before: deathSuccessBefore, death_save_failures_before: deathFailureBefore,
        death_save_successes: actualTarget.state.death_save_successes, death_save_failures: actualTarget.state.death_save_failures,
        is_stable: actualTarget.state.is_stable, is_dead: actualTarget.state.is_dead, attack_id: attack.id, weapon_id: attack.id, projectile: attack.projectile || null,
        feature_id: d20Override.featureId || override.featureId || extra.featureId || (recklessStarted ? "reckless-attack" : null), concentration_ended_effect_id: concentrationBefore && !actualTarget.state.concentration ? concentrationBefore : null,
        resource_remaining: exileApplied?.resourceRemaining ?? deferredEffectArmed?.resourceRemaining ?? null,
        animation: attack.animation || (attack.kind === "ranged" ? "projectile" : "slash"),
        description: description + survivalLog + (window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT?.consumeLog(actualTarget.state) || "") };
    } catch (error) {
      console.error("Browser attack event construction failed", { attacker: ctx?.attacker?.state?.template?.name, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ATTACK_OUTCOME = {
    buildEvent, create, emptyTopple, noEventResult, requireOutcome, resolveD20,
  };
})();
