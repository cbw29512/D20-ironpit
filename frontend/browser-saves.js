(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const B2 = () => window.IRON_PIT_BROWSER_BARBARIAN2 || { dangerSenseAdvantage: () => 0 };
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS || { applyD20Bonus: (_state, _kind, roll) => roll };
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const D = () => window.IRON_PIT_DICE;
  const E = () => window.IRON_PIT_ACTION_ECONOMY || {
    available: (state, cost) => cost === "action" && state.action_available,
    spend: (state) => { state.action_available = false; },
  };
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { autoFailStrDex: (state) => state.is_unconscious };
  const states = (setup) => setup ? [...setup.heroes, ...setup.monsters].map((member) => member.state) : [];

  function saveMode(state, ability) {
    const advantage = (ability === "strength" && state.active_effect_ids.includes("rage") ? 1 : 0)
      + B2().dangerSenseAdvantage(state, ability);
    const disadvantage = ability === "dexterity" && state.active_effect_ids.includes("restrained") ? 1 : 0;
    return R().modeFromSources(advantage, disadvantage);
  }

  function resolveSavingThrow(state, ability, dc) {
    if ((ability === "strength" || ability === "dexterity") && Q().autoFailStrDex(state)) return { roll: null, succeeded: false };
    const bonus = state.template.saving_throw_bonuses?.[ability];
    if (bonus == null) throw new Error(`${state.template.name} lacks a certified ${ability} saving throw bonus.`);
    const roll = M().applyD20Bonus(state, "saving-throw-bonus-die", R().d20(bonus, saveMode(state, ability)));
    return { roll, succeeded: roll.total >= dc };
  }

  function legalAction(action, target, distance) {
    if (distance > action.range) return false;
    return !action.targetMaxSize || S().sizeAtMost(target, action.targetMaxSize);
  }

  function damageRolls(action, count, shared) {
    if (shared == null) return D().rollMany(count, action.damageDiceSize);
    if (!Array.isArray(shared) || shared.length !== count) throw new Error(`${action.name} shared damage roll count is invalid.`);
    if (shared.some((roll) => !Number.isInteger(roll) || roll < 1 || roll > action.damageDiceSize)) throw new Error(`${action.name} shared damage rolls contain an invalid die result.`);
    return [...shared];
  }

  function resolveAction(sequence, round, actor, target, action, distance, options = {}) {
    const spendAction = options.spendAction !== false;
    if (spendAction && !E().available(actor.state, "action")) throw new Error("Action is unavailable for saving throw action.");
    if (!legalAction(action, target, distance)) throw new Error(`${action.name} has no legal target at ${distance} feet.`);
    const save = resolveSavingThrow(target.state, action.saveAbility, action.dc);
    if (spendAction) E().spend(actor.state, "action");
    const hpBefore = target.state.current_hp, temporaryHpBefore = target.state.temporary_hp;
    const deathSuccessBefore = target.state.death_save_successes, deathFailureBefore = target.state.death_save_failures;
    const concentrationBefore = target.state.concentration?.effect_id || null;
    let damageRoll = null, damageComponents = [], damageOutcome = null;
    const count = action.damageDiceCount || 0;
    if (count && !(save.succeeded && action.successDamage === "none")) {
      if (!action.damageType) throw new Error(`${action.name} has damage dice but no damage type.`);
      const rolls = damageRolls(action, count, options.sharedDamageRolls);
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
    let appliedConditions = [];
    if (!save.succeeded && target.state.is_alive && !target.state.is_dead && action.grappleEscapeDc) {
      appliedConditions = G().apply(target.state, actor.combatant_id, action.grappleEscapeDc, action.range, Boolean(action.restrainsWhileGrappled));
    }
    let description = `${target.state.template.name} ${save.succeeded ? "SUCCEEDS" : "FAILS"} a DC ${action.dc} ${action.saveAbility} save against ${actor.state.template.name}'s ${action.name}.`;
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
      concentration_ended_effect_id: concentrationBefore && !target.state.concentration ? concentrationBefore : null,
      animation: action.animation || "save-effect", description };
  }

  window.IRON_PIT_BROWSER_SAVES = { legalAction, resolveAction, resolveSavingThrow, saveMode };
})();
