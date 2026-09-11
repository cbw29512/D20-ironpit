(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const F = () => window.IRON_PIT_BROWSER_SAVE_FAILURE_EFFECTS;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const RES = () => window.IRON_PIT_BROWSER_RESOURCES;
  const B2 = () => window.IRON_PIT_BROWSER_BARBARIAN2 || { dangerSenseAdvantage: () => 0 };
  const DG = () => window.IRON_PIT_BROWSER_DODGE || { dexSaveAdvantageSources: () => 0 };
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS || { applyD20Bonus: (_state, _kind, roll) => roll };
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const D = () => window.IRON_PIT_DICE;
  const E = () => window.IRON_PIT_ACTION_ECONOMY || { available: (state, cost) => cost === "action" && state.action_available,
    spend: (state) => { state.action_available = false; } };
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { autoFailStrDex: (state) => state.is_unconscious };
  const states = (setup) => setup ? [...setup.heroes, ...setup.monsters].map((member) => member.state) : [];

  function saveMode(state, ability, magicalEffect = false) {
    const advantage = (ability === "strength" && state.active_effect_ids.includes("rage") ? 1 : 0)
      + B2().dangerSenseAdvantage(state, ability) + DG().dexSaveAdvantageSources(state, ability)
      + R().bloodiedSaveAdvantage(state) + (magicalEffect && state.template.magic_resistance ? 1 : 0);
    const disadvantage = (ability === "dexterity" && state.active_effect_ids.includes("restrained") ? 1 : 0)
      + (T()?.d20Disadvantage(state, ability) || 0);
    return R().modeFromSources(advantage, disadvantage);
  }

  function indomitableRevision(original, replacement) {
    return {
      source_effect_id: "indomitable", kind: "full_reroll", original_rolls: [...original.rolls],
      replacement_rolls: [...replacement.rolls], original_modifier: original.modifier || 0,
      replacement_modifier: replacement.modifier || 0, original_selected: original.selected_roll,
      replacement_selected: replacement.selected_roll, original_total: original.total,
      replacement_total: replacement.total, accepted: "replacement", replaced_die_index: null,
    };
  }

  function resolveSavingThrow(state, ability, dc, magicalEffect = false) {
    if ((ability === "strength" || ability === "dexterity") && Q().autoFailStrDex(state)) return { roll: null, succeeded: false };
    const bonus = state.template.saving_throw_bonuses?.[ability];
    if (bonus == null) throw new Error(`${state.template.name} lacks a certified ${ability} saving throw bonus.`);
    let roll = M().applyD20Bonus(state, "saving-throw-bonus-die", R().d20(bonus, saveMode(state, ability, magicalEffect)));
    if (roll.total < dc) {
      const reroll = window.IRON_PIT_BROWSER_INDOMITABLE?.use(state, ability);
      if (reroll) roll = { ...reroll, revisions: [...(reroll.revisions || []), indomitableRevision(roll, reroll)] };
    }
    return { roll, succeeded: roll.total >= dc };
  }

  function legalAction(action, target, distance) {
    if (distance > action.range) return false;
    if (action.forbidTargetAffectedByAction && T()?.affectedByAction(target.state, action.id)) return false;
    return !action.targetMaxSize || S().sizeAtMost(target, action.targetMaxSize);
  }

  function pushAway(actor, target, action) {
    const distance = action.pushTargetAwayFt || 0;
    if (!distance || !target.state.is_alive || target.state.is_dead) return 0;
    if (action.pushTargetMaxSize && !S().sizeAtMost(target, action.pushTargetMaxSize)) return 0;
    const start = target.position_ft, direction = start >= actor.position_ft ? 1 : -1;
    target.position_ft = Math.max(0, start + direction * distance);
    return Math.abs(target.position_ft - start);
  }

  function damageRolls(action, count, shared) {
    if (shared == null) return D().rollMany(count, action.damageDiceSize);
    if (!Array.isArray(shared) || shared.length !== count) throw new Error(`${action.name} shared damage roll count is invalid.`);
    if (shared.some((roll) => !Number.isInteger(roll) || roll < 1 || roll > action.damageDiceSize)) throw new Error(`${action.name} shared damage rolls contain an invalid die result.`);
    return [...shared];
  }

  function resolveAction(sequence, round, actor, target, action, distance, options = {}) {
    try {
      const spendAction = options.spendAction !== false, spendResourceCost = options.spendResourceCost !== false;
      const resourceBacked = Boolean(action.resourceId), resources = resourceBacked ? RES() : null;
      if (resourceBacked && spendResourceCost && !resources) throw new Error("Browser resource API is not loaded.");
      if (spendAction && !E().available(actor.state, "action")) throw new Error("Action is unavailable for saving throw action.");
      if (!legalAction(action, target, distance)) throw new Error(`${action.name} has no legal target at ${distance} feet.`);
      if (resourceBacked && spendResourceCost && !resources.available(actor.state, action.resourceId, action.resourceCost || 1)) throw new Error(`${action.name} lacks its required resource.`);
      const save = resolveSavingThrow(target.state, action.saveAbility, action.dc, Boolean(action.magicalEffect));
      if (spendAction) E().spend(actor.state, "action");
      const resourceRemaining = resourceBacked && spendResourceCost ? resources.spend(actor.state, action.resourceId, action.resourceCost || 1) : null;
      const hpBefore = target.state.current_hp, temporaryHpBefore = target.state.temporary_hp;
      const deathSuccessBefore = target.state.death_save_successes, deathFailureBefore = target.state.death_save_failures;
      const concentrationBefore = target.state.concentration?.effect_id || null;
      const tracksPush = Boolean(action.pushTargetAwayFt), distanceBefore = tracksPush ? Math.abs(target.position_ft - actor.position_ft) : null;
      let damageRoll = null, damageComponents = [], damageOutcome = null;
      const count = action.damageDiceCount || 0, capture = options.captureSharedDamageRolls, establishShared = Array.isArray(capture);
      if (count && (!(save.succeeded && action.successDamage === "none") || establishShared)) {
        if (!action.damageType) throw new Error(`${action.name} has damage dice but no damage type.`);
        const rolls = damageRolls(action, count, options.sharedDamageRolls);
        if (establishShared) capture.splice(0, capture.length, ...rolls);
        if (!(save.succeeded && action.successDamage === "none")) {
          let total = rolls.reduce((sum, roll) => sum + roll, 0) + (action.damageBonus || 0);
          if (save.succeeded && action.successDamage === "half") total = Math.floor(total / 2);
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
      }
      let appliedConditions = [], movementFt = 0;
      if (!save.succeeded && target.state.is_alive && !target.state.is_dead) {
        if ((action.failureEffects || []).length) {
          if (!F()) throw new Error("Browser failed-save effect API is not loaded.");
          appliedConditions.push(...F().apply(target, actor.combatant_id, action.id, action.failureEffects, { round, range: action.range }));
        }
        movementFt = pushAway(actor, target, action);
        if (action.grappleEscapeDc) appliedConditions.push(...G().apply(target.state, actor.combatant_id, action.grappleEscapeDc, action.range, Boolean(action.restrainsWhileGrappled)));
        const affectedStates = states(options.setup);
        window.IRON_PIT_BROWSER_RAGE?.endIfIncapacitated(target.state); C()?.endIfIncapacitated(target.state, affectedStates);
      }
      appliedConditions = [...new Set(appliedConditions)];
      const distanceAfter = tracksPush ? Math.abs(target.position_ft - actor.position_ft) : null;
      let description = `${target.state.template.name} ${save.succeeded ? "SUCCEEDS" : "FAILS"} a DC ${action.dc} ${action.saveAbility} save against ${actor.state.template.name}'s ${action.name}.`;
      if (movementFt) description += ` ${target.state.template.name} is pushed ${movementFt} ft. straight away.`;
      if (damageOutcome === "undead_fortitude") description += ` ${target.state.template.name} succeeds on Undead Fortitude and remains at 1 HP.`;
      for (const condition of appliedConditions) description += ` ${target.state.template.name} is ${condition === "grappled" ? "Grappled" : condition === "restrained" ? "Restrained while Grappled" : condition[0].toUpperCase() + condition.slice(1)}.`;
      return { sequence, round_number: round, event_type: "saving_throw", actor_id: actor.combatant_id, actor_name: actor.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name, saving_throw_roll: save.roll, save_ability: action.saveAbility, save_dc: action.dc,
        save_succeeded: save.succeeded, damage_roll: damageRoll, damage_components: damageComponents, applied_condition_ids: appliedConditions,
        hp_before: hpBefore, hp_after: target.state.current_hp, temporary_hp_before: temporaryHpBefore, temporary_hp_after: target.state.temporary_hp,
        death_save_successes_before: deathSuccessBefore, death_save_failures_before: deathFailureBefore, death_save_successes: target.state.death_save_successes,
        death_save_failures: target.state.death_save_failures, is_stable: target.state.is_stable, is_dead: target.state.is_dead, feature_id: action.id,
        resource_remaining: resourceRemaining, movement_ft: movementFt, distance_before_ft: distanceBefore, distance_after_ft: distanceAfter,
        concentration_ended_effect_id: concentrationBefore && !target.state.concentration ? concentrationBefore : null,
        animation: action.animation || "save-effect", description };
    } catch (error) {
      console.error("Browser saving-throw action failed", { actor: actor.combatant_id, target: target.combatant_id, action: action.id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SAVES = { legalAction, resolveAction, resolveSavingThrow, saveMode };
})();