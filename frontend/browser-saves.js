(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const CTRL = () => window.IRON_PIT_BROWSER_CONTROL;
  const H = () => window.IRON_PIT_BROWSER_SAVE_HELPERS;
  const U = () => window.IRON_PIT_BROWSER_RESOURCES;
  const E = () => window.IRON_PIT_ACTION_ECONOMY || {
    available: (state, cost) => cost === "action" && state.action_available,
    spend: (state) => { state.action_available = false; },
  };

  function resolveAction(sequence, round, actor, target, action, distance, options = {}) {
    const spendAction = options.spendAction !== false, spendResource = options.spendResource !== false;
    if (spendAction && !E().available(actor.state, "action")) throw new Error("Action is unavailable for saving throw action.");
    if (!H().resourceAvailable(actor, action)) throw new Error(`${action.name} resource is unavailable.`);
    if (!H().legalAction(action, target, distance)) throw new Error(`${action.name} has no legal target at ${distance} feet.`);
    const save = H().resolveSavingThrow(target.state, action.saveAbility, action.dc, Boolean(action.magicalEffect));
    if (spendAction) E().spend(actor.state, "action");
    if (spendResource) U().spendAttack(actor.state, action);
    const hpBefore = target.state.current_hp, temporaryHpBefore = target.state.temporary_hp;
    const deathSuccessBefore = target.state.death_save_successes, deathFailureBefore = target.state.death_save_failures;
    const concentrationBefore = target.state.concentration?.effect_id || null;
    let damageRoll = null, damageComponents = [], damageOutcome = null;
    const count = action.damageDiceCount || 0, evasion = H().evasionApplies(target.state, action);
    const evasionSuccess = evasion && save.succeeded;
    if (count && !(save.succeeded && action.successDamage === "none") && !evasionSuccess) {
      if (!action.damageType) throw new Error(`${action.name} has damage dice but no damage type.`);
      const rolls = H().damageRolls(action, count, options.sharedDamageRolls);
      let total = rolls.reduce((sum, roll) => sum + roll, 0) + (action.damageBonus || 0);
      if ((evasion && !save.succeeded) || (save.succeeded && action.successDamage === "half")) total = Math.floor(total / 2);
      const applied = A().adjustedDamage(target.state, Math.max(0, total), action.damageType);
      damageComponents = [{ source: action.name, notation: `${count}d${action.damageDiceSize}+${action.damageBonus || 0}`,
        rolls, modifier: action.damageBonus || 0, damage_type: action.damageType, total: Math.max(0, total), applied_total: applied }];
      damageRoll = { notation: damageComponents[0].notation, rolls, modifier: action.damageBonus || 0, total: applied };
      if (applied) {
        const affectedStates = H().states(options.setup);
        damageOutcome = A().applyDamage(target.state, applied, false, [action.damageType], affectedStates);
        window.IRON_PIT_BROWSER_RAGE?.endIfIncapacitated(target.state); C()?.endIfIncapacitated(target.state, affectedStates);
      }
    }
    const control = H().failureControl(action);
    const appliedConditions = !save.succeeded
      ? CTRL().applyPersistent(target, actor.combatant_id, action.id, control, action.range, round, H().states(options.setup)) : [];
    let description = `${target.state.template.name} ${save.succeeded ? "SUCCEEDS" : "FAILS"} a DC ${action.dc} ${action.saveAbility} save against ${actor.state.template.name}'s ${action.name}.`;
    if (evasion) description += " Evasion modifies the damage.";
    if (damageOutcome === "undead_fortitude") description += ` ${target.state.template.name} succeeds on Undead Fortitude and remains at 1 HP.`;
    if (appliedConditions.includes("grappled")) description += ` ${target.state.template.name} is Grappled.`;
    if (appliedConditions.includes("restrained")) description += ` ${target.state.template.name} is Restrained while Grappled.`;
    if (appliedConditions.includes("prone")) description += ` ${target.state.template.name} is knocked Prone.`;
    const event = { sequence, round_number: round, event_type: "saving_throw", actor_id: actor.combatant_id, actor_name: actor.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name, saving_throw_roll: save.roll,
      save_ability: action.saveAbility, save_dc: action.dc, save_succeeded: save.succeeded, damage_roll: damageRoll,
      damage_components: damageComponents, applied_condition_ids: appliedConditions, hp_before: hpBefore, hp_after: target.state.current_hp,
      temporary_hp_before: temporaryHpBefore, temporary_hp_after: target.state.temporary_hp,
      death_save_successes_before: deathSuccessBefore, death_save_failures_before: deathFailureBefore,
      death_save_successes: target.state.death_save_successes, death_save_failures: target.state.death_save_failures,
      is_stable: target.state.is_stable, is_dead: target.state.is_dead, feature_id: action.id,
      resource_remaining: action.resourceId ? actor.state.resources[action.resourceId] : null,
      concentration_ended_effect_id: concentrationBefore && !target.state.concentration ? concentrationBefore : null,
      animation: action.animation || "save-effect", description };
    if (!save.succeeded) CTRL().applyMovement(actor, target, control, event);
    return event;
  }

  window.IRON_PIT_BROWSER_SAVES = {
    evasionApplies: (...args) => H().evasionApplies(...args), legalAction: (...args) => H().legalAction(...args),
    resourceAvailable: (...args) => H().resourceAvailable(...args), resolveAction,
    resolveSavingThrow: (...args) => H().resolveSavingThrow(...args), saveMode: (...args) => H().saveMode(...args),
  };
})();
