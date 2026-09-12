(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_SAVES;
  const ST = () => window.IRON_PIT_BROWSER_STATE;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };

  function resolve(target, attack, sourceId = null, round = null) {
    const effect = attack.onHitSaveEffect;
    if (!effect || !target.state.is_alive || target.state.is_dead) return null;
    if (effect.maxTargetSize && !ST().sizeAtMost(target, effect.maxTargetSize)) return null;
    if (!S()) throw new Error("Browser saving-throw runtime is not loaded.");
    const save = S().resolveSavingThrow(target.state, effect.saveAbility, effect.dc);
    let appliedCondition = null;
    if (!save.succeeded && !I().immune(target.state, effect.conditionId)) {
      const timed = Boolean(effect.durationRounds || effect.repeatSaveTiming || effect.endsOnDamage);
      if (timed) {
        if (!sourceId || !round || !T()) throw new Error("Timed on-hit save effect lacks browser source context.");
        appliedCondition = T().apply(target.state, effect.conditionId, sourceId, {
          sourceEffectId: attack.id, appliedRound: round,
          expiresRound: effect.durationRounds ? round + effect.durationRounds : null,
          repeatSaveAbility: effect.repeatSaveTiming ? effect.saveAbility : null,
          repeatSaveDc: effect.repeatSaveTiming ? effect.dc : null,
          repeatSaveTiming: effect.repeatSaveTiming || null,
          endsOnDamage: Boolean(effect.endsOnDamage),
        });
      } else {
        if (!target.state.active_effect_ids.includes(effect.conditionId)) target.state.active_effect_ids.push(effect.conditionId);
        appliedCondition = effect.conditionId;
      }
    }
    return { saveRoll: save.roll, saveAbility: effect.saveAbility, saveDc: effect.dc,
      saveSucceeded: save.succeeded, appliedCondition };
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
      const result = resolve(target, attack, args[2].combatant_id, args[1]);
      if (!result) return event;
      event.saving_throw_roll = result.saveRoll;
      event.save_ability = result.saveAbility;
      event.save_dc = result.saveDc;
      event.save_succeeded = result.saveSucceeded;
      if (result.appliedCondition) {
        event.applied_condition_ids = [...new Set([...(event.applied_condition_ids || []), result.appliedCondition])];
        event.description += ` ${target.state.template.name} is ${result.appliedCondition === "prone" ? "knocked Prone" : result.appliedCondition}.`;
      }
      event.description += ` ${result.saveAbility} save DC ${result.saveDc}: ${target.state.template.name} ${result.saveSucceeded ? "succeeds" : "fails"}.`;
      return event;
    };
    attackRuntime.onHitSaveWrapped = true;
  }

  window.IRON_PIT_BROWSER_ON_HIT_SAVES = { resolve, install };
  install();
})();
