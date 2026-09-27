(() => {
  "use strict";
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const DF = () => window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS || { saveAdvantage: () => 0, saveAdvantageSourceNames: () => [] };
  const RD = () => window.IRON_PIT_BROWSER_ROGUE_DEFENSES || { evasionDamage: (_state, _ability, succeeded, successDamage, total) => succeeded && successDamage === "half" ? Math.floor(total / 2) : total };
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const SD = () => window.IRON_PIT_BROWSER_SAVE_DAMAGE;
  const D = () => window.IRON_PIT_DICE;
  const DO = () => window.IRON_PIT_BROWSER_D20_TEST_OVERRIDE || { apply: (_state, roll) => ({ roll, featureId: null, sourceName: null }), sourceNameForRoll: () => null };
  const E = () => window.IRON_PIT_ACTION_ECONOMY || {
    available: (state, cost) => cost === "action" && state.action_available,
    spend: (state) => { state.action_available = false; },
  };
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { autoFailStrDex: (state) => state.is_unconscious };
  const states = (setup) => setup ? [...setup.heroes, ...setup.monsters].map((member) => member.state) : [];
  // Preserve the shared save API while keeping roll policy in its own module.
  const resolveSavingThrow = (...args) => window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow(...args);
  const saveMode = (...args) => window.IRON_PIT_BROWSER_SAVING_THROWS.saveMode(...args);

  function resolveOnHitConditionSave(target, attack, sourceTemplate = null, round = null) {
    const effect = attack.onHitConditionSave;
    if (!effect || target.state.is_dead || !target.state.is_alive) return null;
    if (effect.maxTargetSize && !S().sizeAtMost(target, effect.maxTargetSize)) return null;
    if (I().immune(target.state, effect.conditionId, sourceTemplate)) return null;
    const effectTags = effect.conditionId === "poisoned" ? ["poison"] : [];
    const save = resolveSavingThrow(target.state, effect.saveAbility, effect.dc, { conditionId: effect.conditionId, effectTags, roundNumber: round });
    let appliedCondition = null;
    if (!save.succeeded && !target.state.active_effect_ids.includes(effect.conditionId)) {
      target.state.active_effect_ids.push(effect.conditionId); appliedCondition = effect.conditionId;
    }
    return { saveRoll: save.roll, saveAbility: effect.saveAbility, saveDc: effect.dc,
      saveSucceeded: save.succeeded, appliedCondition };
  }

  function legalAction(action, target, distance) {
    if (distance > action.range) return false;
    if (action.requiresTargetHearing && target.state.active_effect_ids.includes("deafened")) return false;
    return !action.targetMaxSize || S().sizeAtMost(target, action.targetMaxSize);
  }

  function damageRolls(action, count, shared) {
    if (shared == null) return D().rollMany(count, action.damageDiceSize);
    if (!Array.isArray(shared) || shared.length !== count) throw new Error(`${action.name} shared damage roll count is invalid.`);
    if (shared.some((roll) => !Number.isInteger(roll) || roll < 1 || roll > action.damageDiceSize)) throw new Error(`${action.name} shared damage rolls contain an invalid die result.`);
    return [...shared];
  }

  function resolveAction(sequence, round, actor, target, action, distance, options = {}) {
    const spendAction = options.spendAction !== false, checkResource = options.checkResource !== false;
    if (spendAction && !E().available(actor.state, "action")) throw new Error("Action is unavailable for saving throw action.");
    if (checkResource && action.resourceId && (actor.state.resources[action.resourceId] || 0) < (action.resourceCost || 1)) throw new Error(`${action.name} resource is unavailable.`);
    if (!legalAction(action, target, distance)) throw new Error(`${action.name} has no legal target at ${distance} feet.`);
    if (action.requiresTargetSight && !Q().canSee(actor.state, target.state)) throw new Error(`${action.name} requires the actor to see the target.`);
    const effectTags = [...new Set([...(action.effectTags || []).map((tag) => String(tag).trim().toLowerCase()).filter(Boolean), ...(String(action.damageType || "").trim().toLowerCase() === "poison" ? ["poison"] : [])])];
    const saveContext = {
      magicalEffect: Boolean(action.magicalEffect), spellEffect: Boolean(options.spellEffect),
      sourceCreatureType: actor.state.template.creature_type || null, effectTags, roundNumber: round,
      disadvantageSources: [...(options.saveDisadvantageSources || [])],
    };
    const advantageSources = DF().saveAdvantageSourceNames?.(
      target.state, action.saveAbility, saveContext,
    ) || [];
    const save = resolveSavingThrow(target.state, action.saveAbility, action.dc, saveContext);
    let resourceRemaining = options.resourceRemaining ?? null;
    if (action.resourceId && options.spendResource !== false) {
      actor.state.resources[action.resourceId] -= action.resourceCost || 1; resourceRemaining = actor.state.resources[action.resourceId];
    }
    if (spendAction) E().spend(actor.state, "action");
    const hpBefore = target.state.current_hp, temporaryHpBefore = target.state.temporary_hp;
    const deathSuccessBefore = target.state.death_save_successes, deathFailureBefore = target.state.death_save_failures;
    const concentrationBefore = target.state.concentration?.effect_id || null;
    let damageRoll = null, damageComponents = [], damageOutcome = null;
    if (action.damageComponents?.length) {
      if (!SD()) throw new Error("Multi-component save damage runtime is not loaded.");
      const resolved = SD().resolve(target.state, action, save.succeeded, options.sharedDamageRolls);
      damageComponents = resolved.components; damageRoll = resolved.roll;
      if (resolved.appliedTotal) {
        const affectedStates = states(options.setup);
        damageOutcome = A().applyDamage(target.state, resolved.appliedTotal, false, resolved.damageTypes, affectedStates);
        window.IRON_PIT_BROWSER_RAGE?.endIfIncapacitated(target.state); C()?.endIfIncapacitated(target.state, affectedStates);
      }
    }
    const count = action.damageDiceCount || 0;
    if (!action.damageComponents?.length && count && !(save.succeeded && action.successDamage === "none")) {
      if (!action.damageType) throw new Error(`${action.name} has damage dice but no damage type.`);
      const rolls = damageRolls(action, count, options.sharedDamageRolls);
      const rawTotal = rolls.reduce((sum, roll) => sum + roll, 0) + (action.damageBonus || 0);
      const total = RD().evasionDamage(target.state, action.saveAbility, save.succeeded, action.successDamage, rawTotal);
      const applied = A().adjustedDamage(target.state, Math.max(0, total), action.damageType);
      damageComponents = [{ source: action.name, notation: `${count}d${action.damageDiceSize}+${action.damageBonus || 0}`,
        rolls, modifier: action.damageBonus || 0, damage_type: action.damageType, total: Math.max(0, total), applied_total: applied }];
      damageRoll = { notation: damageComponents[0].notation, rolls, modifier: action.damageBonus || 0, total: applied };
      if (applied) {
        const affectedStates = states(options.setup);
        damageOutcome = A().applyDamage(target.state, applied, false, [action.damageType], affectedStates);
        window.IRON_PIT_BROWSER_RAGE?.endIfIncapacitated(target.state); C()?.endIfIncapacitated(target.state, affectedStates);
      }
    }
    let appliedConditions = [];
    if (!save.succeeded && target.state.is_alive && !target.state.is_dead && action.failedSaveTimedEffect) {
      const rider = action.failedSaveTimedEffect;
      const timed = window.IRON_PIT_BROWSER_TIMED;
      if (!timed) throw new Error("Failed-save timed effect requires browser-timed-conditions.js.");
      timed.apply(target.state, rider.effectId, actor.combatant_id, {
        sourceEffectId: action.id,
        sourceTemplate: actor.state.template,
        sourceIsMagical: Boolean(action.magicalEffect),
        appliedRound: round,
        expiryTiming: rider.expiryTiming || "target_turn_end",
        nextAttackDisadvantage: Boolean(rider.nextAttackDisadvantage),
        useDefaultPoisonRecovery: false,
      });
    }
    if (!save.succeeded && target.state.is_alive && !target.state.is_dead && action.grappleEscapeDc) {
      appliedConditions = G().apply(
        target.state,
        actor.combatant_id,
        action.grappleEscapeDc,
        action.range,
        Boolean(action.restrainsWhileGrappled),
        Boolean(action.magicalEffect),
      );
    }
    const survivalLog = window.IRON_PIT_BROWSER_UNDEAD_FORTITUDE?.consumeLog(target.state) || "";
    let description = `${target.state.template.name} ${save.succeeded ? "SUCCEEDS" : "FAILS"} a DC ${action.dc} ${action.saveAbility} save against ${actor.state.template.name}'s ${action.name}.`;
    if (advantageSources.length) description += ` ${advantageSources.join(" and ")} grants Advantage on the save.`;
    if (saveContext.disadvantageSources.length) description += ` ${saveContext.disadvantageSources.join(" and ")} imposes Disadvantage on the save.`;
    const d20OverrideName = DO().sourceNameForRoll(target.state, save.roll);
    if (d20OverrideName) description += ` ${d20OverrideName} turns the failed saving throw roll into a 20.`;
    if (target.state.template.evasion && action.saveAbility === "dexterity" && action.successDamage === "half") description += " Evasion reduces the damage.";
    if (damageOutcome === "undead_fortitude") description += ` ${target.state.template.name} succeeds on Undead Fortitude and remains at 1 HP.`;
    if (appliedConditions.includes("grappled")) description += ` ${target.state.template.name} is Grappled.`;
    if (appliedConditions.includes("restrained")) description += ` ${target.state.template.name} is Restrained while Grappled.`;
    return { sequence, round_number: round, event_type: "saving_throw", actor_id: actor.combatant_id, actor_name: actor.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name, saving_throw_roll: save.roll,
      save_ability: action.saveAbility, save_dc: action.dc, save_succeeded: save.succeeded, damage_roll: damageRoll,
      damage_components: damageComponents, applied_condition_ids: appliedConditions, hp_before: hpBefore, hp_after: target.state.current_hp,
      temporary_hp_before: temporaryHpBefore, temporary_hp_after: target.state.temporary_hp,
      death_save_successes_before: deathSuccessBefore, death_save_failures_before: deathFailureBefore,
      death_save_successes: target.state.death_save_successes, death_save_failures: target.state.death_save_failures,
      is_stable: target.state.is_stable, is_dead: target.state.is_dead, feature_id: action.id,
      resource_remaining: resourceRemaining,
      concentration_ended_effect_id: concentrationBefore && !target.state.concentration ? concentrationBefore : null,
      animation: action.animation || "save-effect", description: description + survivalLog + (window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT?.consumeLog(target.state) || "") };
  }

  window.IRON_PIT_BROWSER_SAVES = { legalAction, resolveAction, resolveOnHitConditionSave, resolveSavingThrow, saveMode };
})();
