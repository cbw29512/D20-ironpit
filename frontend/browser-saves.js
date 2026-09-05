(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
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

  function saveMode(state, ability, magical = false) {
    const advantage = (ability === "strength" && state.active_effect_ids.includes("rage") ? 1 : 0)
      + B2().dangerSenseAdvantage(state, ability)
      + (state.template.saving_throw_advantage_triggers?.includes("attacker_bloodied") && state.current_hp * 2 <= S().effectiveMaxHp(state) ? 1 : 0)
      + (magical && state.template.saving_throw_advantage_triggers?.includes("magical_effect") ? 1 : 0);
    const disadvantage = ability === "dexterity" && state.active_effect_ids.includes("restrained") ? 1 : 0;
    return R().modeFromSources(advantage, disadvantage);
  }

  function resolveSavingThrow(state, ability, dc, magical = false) {
    if ((ability === "strength" || ability === "dexterity") && Q().autoFailStrDex(state)) return { roll: null, succeeded: false };
    const bonus = state.template.saving_throw_bonuses?.[ability];
    if (bonus == null) throw new Error(`${state.template.name} lacks a certified ${ability} saving throw bonus.`);
    let roll = M().applyD20Bonus(state, "saving-throw-bonus-die", R().d20(bonus, saveMode(state, ability, magical)));
    if (roll.total < dc) {
      const reroll = window.IRON_PIT_BROWSER_INDOMITABLE?.use(state, ability, magical);
      if (reroll) roll = reroll;
    }
    return { roll, succeeded: roll.total >= dc };
  }

  function resourceAvailable(state, action) {
    return !action.resourceId || (state.resources?.[action.resourceId] ?? 0) >= (action.resourceCost || 1);
  }
  function consumeResource(state, action) {
    if (!action.resourceId) return null;
    if (!resourceAvailable(state, action)) throw new Error(`${action.name} has no remaining resource use.`);
    state.resources[action.resourceId] -= action.resourceCost || 1;
    return state.resources[action.resourceId];
  }
  function rechargeStart(state) {
    for (const [id, threshold] of Object.entries(state.template.resource_recharge || {})) {
      const maximum = state.template.resources?.[id] ?? 0;
      if ((state.resources?.[id] ?? 0) < maximum && D().roll(6) >= threshold) state.resources[id] = maximum;
    }
  }

  function legalAction(action, target, distance) {
    if (distance > action.range) return false;
    return !action.targetMaxSize || S().sizeAtMost(target, action.targetMaxSize);
  }

  function chooseAction(member, setup, priorityOnly = false) {
    const actions = [...(member.state.template.saving_throw_actions || [])]
      .filter((action) => resourceAvailable(member.state, action) && (!priorityOnly || (action.priority || 0) > 0))
      .sort((left, right) => (right.priority || 0) - (left.priority || 0) || left.id.localeCompare(right.id));
    for (const action of actions) {
      const targets = [];
      for (const target of F().targetOrder(member, setup)) {
        const distance = F().saveDistance(member, target, action.range);
        if (legalAction(action, target, distance)) targets.push({ target, distance });
        if (targets.length >= (action.areaSlots || 1)) break;
      }
      if (targets.length) return { action, targets };
    }
    return null;
  }

  function damageRolls(action, count, shared) {
    if (shared == null) return D().rollMany(count, action.damageDiceSize);
    if (!Array.isArray(shared) || shared.length !== count) throw new Error(`${action.name} shared damage roll count is invalid.`);
    if (shared.some((roll) => !Number.isInteger(roll) || roll < 1 || roll > action.damageDiceSize)) throw new Error(`${action.name} shared damage rolls contain an invalid die result.`);
    return [...shared];
  }

  function resolveAction(sequence, round, actor, target, action, distance, options = {}) {
    const spendAction = options.spendAction !== false, spendResource = options.spendResource !== false;
    if (spendAction && !E().available(actor.state, "action")) throw new Error("Action is unavailable for saving throw action.");
    if (!legalAction(action, target, distance)) throw new Error(`${action.name} has no legal target at ${distance} feet.`);
    if (spendResource && !resourceAvailable(actor.state, action)) throw new Error(`${action.name} has no remaining resource use.`);
    const save = resolveSavingThrow(target.state, action.saveAbility, action.dc, Boolean(action.magical));
    if (spendAction) E().spend(actor.state, "action");
    const resourceRemaining = spendResource ? consumeResource(actor.state, action) : null;
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
      is_stable: target.state.is_stable, is_dead: target.state.is_dead, feature_id: action.id, resource_remaining: resourceRemaining,
      concentration_ended_effect_id: concentrationBefore && !target.state.concentration ? concentrationBefore : null,
      animation: action.animation || "save-effect", description };
  }

  function resolveChoice(sequence, round, member, setup, choice) {
    const events = []; let sharedDamageRolls = null;
    choice.targets.forEach(({ target, distance }, index) => {
      const event = resolveAction(sequence++, round, member, target, choice.action, distance, {
        spendAction: index === 0, spendResource: index === 0, sharedDamageRolls, setup,
      });
      events.push(event);
      if (sharedDamageRolls === null && event.damage_components?.length) sharedDamageRolls = [...event.damage_components[0].rolls];
    });
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_SAVES = {
    chooseAction, consumeResource, legalAction, rechargeStart, resolveAction, resolveChoice, resolveSavingThrow, resourceAvailable, saveMode,
  };
})();
