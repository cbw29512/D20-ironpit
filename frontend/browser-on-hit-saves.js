(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_SAVES;
  const ST = () => window.IRON_PIT_BROWSER_STATE;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const D = () => window.IRON_PIT_DICE;
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;
  const FM = () => window.IRON_PIT_BROWSER_FORCED_MOVEMENT;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };

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

  function resolve(target, attack, sourceId = null, round = null, setup = null) {
    const effect = attack.onHitSaveEffect;
    if (!effect || !target.state.is_alive || target.state.is_dead) return null;
    if (effect.maxTargetSize && !ST().sizeAtMost(target, effect.maxTargetSize)) return null;
    if (!S()) throw new Error("Browser saving-throw runtime is not loaded.");
    const save = S().resolveSavingThrow(target.state, effect.saveAbility, effect.dc);
    const damage = saveDamage(target, effect, save.succeeded, setup);
    const appliedConditions = stableZeroHp(target, attack, effect, sourceId, round, damage.total);
    let appliedCondition = null;
    if (effect.conditionId && !save.succeeded && target.state.is_alive && !target.state.is_dead && !I().immune(target.state, effect.conditionId)) {
      const timed = Boolean(effect.durationRounds || effect.repeatSaveTiming || effect.endsOnDamage);
      if (timed) {
        if (!sourceId || round === null || !T()) throw new Error("Timed on-hit save effect lacks browser source context.");
        appliedCondition = T().apply(target.state, effect.conditionId, sourceId, {
          sourceEffectId: attack.id, appliedRound: round,
          expiresRound: effect.durationRounds ? round + effect.durationRounds : null,
          repeatSaveAbility: effect.repeatSaveTiming ? effect.saveAbility : null,
          repeatSaveDc: effect.repeatSaveTiming ? effect.dc : null,
          repeatSaveTiming: effect.repeatSaveTiming || null, endsOnDamage: Boolean(effect.endsOnDamage),
        });
      } else {
        if (!target.state.active_effect_ids.includes(effect.conditionId)) target.state.active_effect_ids.push(effect.conditionId);
        appliedCondition = effect.conditionId;
      }
      if (appliedCondition) appliedConditions.push(appliedCondition);
    }
    const pushedFt = failedSavePush(target, effect, sourceId, save.succeeded, setup);
    return { saveRoll: save.roll, saveAbility: effect.saveAbility, saveDc: effect.dc, saveSucceeded: save.succeeded,
      appliedCondition, appliedConditions: [...new Set(appliedConditions)], damageTotal: damage.total, damageComponent: damage.component, pushedFt };
  }

  function actualTarget(target, setup, targetId) {
    if (target.combatant_id === targetId || !setup) return target;
    return [...setup.heroes, ...setup.monsters].find((member) => member.combatant_id === targetId) || target;
  }

  function install() {
    const attackRuntime = window.IRON_PIT_BROWSER_ATTACK;
    if (!attackRuntime || attackRuntime.onHitSaveWrapped) return;
    const original = attackRuntime.resolveAttack;
    attackRuntime.resolveAttack = (...args) => {
      const event = original(...args), attack = args[4], extra = args[6] || {};
      const target = actualTarget(args[3], extra.setup, event.target_id);
      if (!event.hit || !attack.onHitSaveEffect) return event;
      const result = resolve(target, attack, args[2].combatant_id, args[1], extra.setup);
      if (!result) return event;
      event.saving_throw_roll = result.saveRoll; event.save_ability = result.saveAbility;
      event.save_dc = result.saveDc; event.save_succeeded = result.saveSucceeded;
      if (result.damageComponent) {
        event.damage_components = [...(event.damage_components || []), result.damageComponent];
        if (event.damage_roll) event.damage_roll.total += result.damageTotal;
        event.hp_after = target.state.current_hp; event.is_stable = target.state.is_stable; event.is_dead = target.state.is_dead;
      }
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

  window.IRON_PIT_BROWSER_ON_HIT_SAVES = { resolve, install };
  install();
})();