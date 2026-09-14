(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_SAVES;
  const ST = () => window.IRON_PIT_BROWSER_STATE;
  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const TM = () => window.IRON_PIT_BROWSER_TACTICAL_MIND;
  const D = () => window.IRON_PIT_DICE;
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;
  const FM = () => window.IRON_PIT_BROWSER_FORCED_MOVEMENT;
  const CND = () => window.IRON_PIT_BROWSER_ON_HIT_SAVE_CONDITIONS;
  const OD = () => window.IRON_PIT_BROWSER_START_TURN_DAMAGE;

  function eligible(state, effect) {
    const type = String(state.template.creature_type || "").toLowerCase();
    const subtypes = new Set((state.template.creature_subtypes || []).map((item) => String(item).toLowerCase()));
    return !(effect.excludedCreatureTypes || []).includes(type) && !(effect.excludedCreatureSubtypes || []).some((item) => subtypes.has(item));
  }
  function adjustedDamage(state, amount, type) {
    if (!type || state.template.damage_immunities?.includes(type)) return 0;
    let value = amount;
    if (state.template.damage_resistances?.includes(type) || state.temporary_damage_resistances?.includes(type)) value = Math.floor(value / 2);
    if (state.template.damage_vulnerabilities?.includes(type)) value *= 2;
    return value;
  }

  function saveDamage(target, effect, succeeded, setup) {
    if (!effect.damageDiceCount || !effect.damageType) return { total: 0, component: null };
    if (!D() || !Z()) throw new Error("Browser save-damage dependencies are not loaded.");
    const rolls = D().rollMany(effect.damageDiceCount, effect.damageDiceSize);
    let raw = Math.max(0, rolls.reduce((sum, roll) => sum + roll, 0) + (effect.damageBonus || 0));
    if (succeeded) raw = effect.successDamage === "half" ? Math.floor(raw / 2) : 0;
    const total = adjustedDamage(target.state, raw, effect.damageType);
    if (total > 0) Z().applyDamage(target.state, total, false, [effect.damageType], setup ? [...setup.heroes, ...setup.monsters].map((member) => member.state) : []);
    return { total, component: { source: "on-hit save rider", notation: `${effect.damageDiceCount}d${effect.damageDiceSize}+${effect.damageBonus || 0}`, rolls, modifier: effect.damageBonus || 0, damage_type: effect.damageType, total: raw, applied_total: total } };
  }

  function reduceMaxHp(target, amount, killAtZero) {
    const state = target.state, before = ST().effectiveMaxHp(state), reduction = Math.min(Math.max(0, amount), before);
    state.max_hp_reduction = (state.max_hp_reduction || 0) + reduction;
    const after = ST().effectiveMaxHp(state); state.current_hp = Math.min(state.current_hp, after);
    if (killAtZero && after === 0) {
      state.current_hp = 0; state.is_alive = false; state.is_unconscious = false; state.is_stable = false; state.is_dead = true;
      state.death_save_successes = 0; state.death_save_failures = 0;
    }
    return { reduction, before, after };
  }

  function stableZeroHp(target, attack, effect, sourceId, round, damageTotal) {
    if (!damageTotal || !effect.zeroHpStable || target.state.current_hp !== 0) return [];
    if (!sourceId || round === null || !T()) throw new Error("Stable zero-HP rider lacks browser source context.");
    const state = target.state;
    state.is_alive = true; state.is_dead = false; state.is_unconscious = true; state.is_stable = true;
    state.death_save_successes = 0; state.death_save_failures = 0;
    const applied = [];
    for (const conditionId of effect.zeroHpConditionIds || []) {
      const result = T().apply(state, conditionId, sourceId, {
        sourceEffectId: attack.id, appliedRound: round,
        expiresRound: round + effect.zeroHpDurationRounds, expiryTiming: "source_turn_start",
      });
      if (result) applied.push(result);
    }
    return applied;
  }

  function failedSavePush(target, effect, sourceId, succeeded, setup) {
    if (succeeded || !effect.failurePushFt) return 0;
    if (!setup || !FM()) throw new Error("Failed-save forced movement lacks browser encounter context.");
    const source = [...setup.heroes, ...setup.monsters].find((member) => member.combatant_id === sourceId);
    if (!source) throw new Error("Failed-save forced movement source was not found.");
    return FM().pushAway(source, target, effect.failurePushFt, setup);
  }

  function resolve(target, attack, sourceId = null, round = null, setup = null, triggeringDamageTotal = 0) {
    const effect = attack.onHitSaveEffect;
    if (sourceId && OD()?.shouldSkipSave(target.state, attack, sourceId)) { OD().applyOnHit(target.state, attack, sourceId, null); return null; }
    if (!effect) { if (sourceId) OD()?.applyOnHit(target.state, attack, sourceId, null); return null; }
    if (!target.state.is_alive || target.state.is_dead || !eligible(target.state, effect)) return null;
    if (effect.maxTargetSize && !ST().sizeAtMost(target, effect.maxTargetSize)) return null;
    if (!S() || !CND()) throw new Error("Browser on-hit save dependencies are not loaded.");
    const save = S().resolveSavingThrow(target.state, effect.saveAbility, effect.dc, { againstCondition: effect.conditionId || null });
    const damage = saveDamage(target, effect, save.succeeded, setup);
    const appliedConditions = stableZeroHp(target, attack, effect, sourceId, round, damage.total);
    const maxHp = effect.maxHpReductionEqualsDamageTaken && !save.succeeded && target.state.is_alive && !target.state.is_dead
      ? reduceMaxHp(target, triggeringDamageTotal, Boolean(effect.zeroMaxHpKills)) : { reduction: 0, before: ST().effectiveMaxHp(target.state), after: ST().effectiveMaxHp(target.state) };
    const failed = CND().applyFailure(target, attack, effect, save, sourceId, round);
    appliedConditions.push(...failed.appliedConditions);
    const pushedFt = failedSavePush(target, effect, sourceId, save.succeeded, setup);
    if (sourceId) OD()?.applyOnHit(target.state, attack, sourceId, save.succeeded);
    return { saveRoll: save.roll, saveAbility: effect.saveAbility, saveDc: effect.dc, saveSucceeded: save.succeeded,
      appliedCondition: failed.appliedCondition, appliedConditions: [...new Set(appliedConditions)], damageTotal: damage.total, damageComponent: damage.component,
      pushedFt, maxHpReduction: maxHp.reduction, maxHpBefore: maxHp.before, maxHpAfter: maxHp.after };
  }

  function actualTarget(target, setup, targetId) {
    if (target.combatant_id === targetId || !setup) return target;
    return [...setup.heroes, ...setup.monsters].find((member) => member.combatant_id === targetId) || target;
  }

  function abilityModifier(state, ability) {
    const direct = state.template.ability_modifiers?.[ability];
    if (Number.isInteger(direct)) return direct;
    const attack = (state.template.attacks || []).find((item) => item.attackAbility === ability && Number.isInteger(item.attackAbilityModifier));
    if (attack) return attack.attackAbilityModifier;
    throw new Error(`${state.template.name} lacks a certified ${ability} ability modifier.`);
  }

  function abilityCheck(state, ability) {
    const advantage = ability === "strength" && state.active_effect_ids.includes("rage") ? 1 : 0;
    const disadvantage = (state.active_effect_ids.includes("poisoned") || state.active_effect_ids.includes("frightened") ? 1 : 0)
      + (T()?.abilityCheckDisadvantage?.(state) || 0) + (ability === "strength" ? (T()?.strengthD20Disadvantage?.(state) || 0) : 0);
    return R().d20(abilityModifier(state, ability), R().modeFromSources(advantage, disadvantage));
  }

  function applyContestedMovement(event, source, target, attack, setup) {
    const effect = attack.onHitContestedMovement;
    if (!event.hit || !effect || !setup || !target.state.is_alive || target.state.is_dead) return;
    if (effect.maxTargetSize && !ST().sizeAtMost(target, effect.maxTargetSize)) return;
    if (!FM() || !R()) throw new Error("Contested movement dependencies are not loaded.");
    const sourceRoll = abilityCheck(source.state, effect.sourceAbility), originalTargetRoll = abilityCheck(target.state, effect.targetAbility);
    let targetRoll = originalTargetRoll, succeeded = targetRoll.total >= sourceRoll.total, tactical = null;
    if (!succeeded && TM()) {
      tactical = TM().apply(target.state, targetRoll, sourceRoll.total);
      targetRoll = tactical.roll; succeeded = tactical.succeeded;
    }
    let moved = 0;
    if (!succeeded) moved = effect.direction === "away_from_source"
      ? FM().pushAway(source, target, effect.distanceFt, setup)
      : FM().pullToward(source, target, effect.distanceFt, setup);
    event.ability_check_roll = targetRoll; event.check_ability = effect.targetAbility;
    event.check_dc = sourceRoll.total; event.check_succeeded = succeeded;
    if (moved) event.movement_ft = (event.movement_ft || 0) + moved;
    const tacticalText = tactical?.used ? " after using Tactical Mind" : "";
    const outcome = succeeded ? "resists" : `is moved ${moved} feet`;
    event.description += ` ${target.state.template.name} ${outcome}${tacticalText} in the opposed ${effect.targetAbility} check (${targetRoll.total} vs. ${sourceRoll.total}).`;
  }

  function install() {
    const attackRuntime = window.IRON_PIT_BROWSER_ATTACK;
    if (!attackRuntime || attackRuntime.onHitSaveWrapped) return;
    const original = attackRuntime.resolveAttack;
    attackRuntime.resolveAttack = (...args) => {
      const event = original(...args), attack = args[4], extra = args[6] || {};
      const target = actualTarget(args[3], extra.setup, event.target_id), source = args[2];
      applyContestedMovement(event, source, target, attack, extra.setup);
      if (!event.hit || (!attack.onHitSaveEffect && !attack.ongoingDamageEffect)) return event;
      const triggeringDamageTotal = (event.damage_components || []).reduce((sum, part) => sum + (part.applied_total || 0), 0);
      const result = resolve(target, attack, source.combatant_id, args[1], extra.setup, triggeringDamageTotal);
      if (!result) return event;
      event.saving_throw_roll = result.saveRoll; event.save_ability = result.saveAbility;
      event.save_dc = result.saveDc; event.save_succeeded = result.saveSucceeded;
      event.max_hp_before = result.maxHpBefore; event.max_hp_after = result.maxHpAfter;
      if (result.damageComponent) {
        event.damage_components = [...(event.damage_components || []), result.damageComponent];
        if (event.damage_roll) event.damage_roll.total += result.damageTotal;
        event.hp_after = target.state.current_hp; event.is_stable = target.state.is_stable; event.is_dead = target.state.is_dead;
      }
      if (result.maxHpReduction) { event.hp_after = target.state.current_hp; event.is_dead = target.state.is_dead; event.description += ` Maximum HP reduced by ${result.maxHpReduction}.`; }
      if (result.appliedConditions.length) {
        event.applied_condition_ids = [...new Set([...(event.applied_condition_ids || []), ...result.appliedConditions])];
        for (const condition of result.appliedConditions) event.description += ` ${target.state.template.name} is ${condition}.`;
      }
      if (result.pushedFt) event.description += ` ${target.state.template.name} is pushed ${result.pushedFt} feet away.`;
      event.description += ` ${result.saveAbility} save DC ${result.saveDc}: ${target.state.template.name} ${result.saveSucceeded ? "succeeds" : "fails"}.`;
      return event;
    };
    attackRuntime.onHitSaveWrapped = true;
  }

  window.IRON_PIT_BROWSER_ON_HIT_SAVES = { applyContestedMovement, resolve, install };
  install();
})();
