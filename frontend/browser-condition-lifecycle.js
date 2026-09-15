(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const I = () => window.IRON_PIT_BROWSER_SOURCE_EFFECT_IMMUNITY;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES;

  const label = (id) => id.replaceAll("_", " ").replaceAll("-", " ").replace(/\b\w/g, (char) => char.toUpperCase());
  function repeatSaveDue(effect, round, timing, state) {
    if (effect.repeat_save_timing !== timing) return false;
    const arenaPoison = effect.effect_id === "poisoned" && state.template.ruleset !== "2014";
    return !(arenaPoison && effect.applied_round != null && round <= effect.applied_round);
  }
  const expiryDue = (effect, round, timing) => effect.expires_after_next_target_turn
    ? timing === "target_turn_end" && effect.target_turn_started_since_applied
    : effect.expiry_timing === timing && (effect.expires_round == null || round >= effect.expires_round);
  function grantEndImmunity(target, effect) {
    if (effect.source_effect_immunity_on_end && effect.source_effect_id) I().grant(target.state, effect.source_id, effect.source_effect_id);
  }
  function escalate(target, effect, round) {
    if (!effect.repeat_save_failure_condition_id) return { removed: [], applied: [] };
    const removed = T().removeGroup(target.state, effect);
    const applied = T().apply(target.state, effect.repeat_save_failure_condition_id, effect.source_id, {
      sourceEffectId: effect.source_effect_id, appliedRound: round,
    });
    return { removed, applied: applied ? [applied] : [] };
  }

  function resolveTargetTiming(sequence, round, target, timing) {
    const events = [];
    for (const effect of [...target.state.timed_effects]) {
      if (!target.state.timed_effects.includes(effect)) continue;
      if (timing === "target_turn_start" && effect.expires_after_next_target_turn) effect.target_turn_started_since_applied = true;
      if (repeatSaveDue(effect, round, timing, target.state)) {
        const save = V().resolveSavingThrow(target.state, effect.repeat_save_ability, effect.repeat_save_dc, { againstCondition: effect.effect_id });
        const removed = save.succeeded ? T().removeGroup(target.state, effect) : [];
        const escalated = save.succeeded ? { removed: [], applied: [] } : escalate(target, effect, round);
        if (save.succeeded) grantEndImmunity(target, effect);
        events.push({
          sequence: sequence++, round_number: round, event_type: "saving_throw",
          actor_id: target.combatant_id, actor_name: target.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          saving_throw_roll: save.roll, save_ability: effect.repeat_save_ability,
          save_dc: effect.repeat_save_dc, save_succeeded: save.succeeded,
          removed_condition_ids: [...removed, ...escalated.removed], applied_condition_ids: escalated.applied,
          feature_id: effect.source_effect_id || "condition-repeat-save", animation: "condition-save",
          description: `${target.state.template.name} repeats the ${effect.repeat_save_ability} save against ${label(effect.source_effect_id || effect.effect_id)}: ${save.succeeded ? "SUCCESS" : "FAILURE"}.`,
        });
        if (save.succeeded || escalated.applied.length) continue;
      }
      if (expiryDue(effect, round, timing)) {
        const removed = T().removeGroup(target.state, effect); if (!removed.length) continue;
        grantEndImmunity(target, effect);
        events.push({ sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: target.combatant_id, actor_name: target.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          removed_condition_ids: removed, feature_id: effect.source_effect_id || "condition-ended",
          animation: "condition-ended", description: `${label(effect.source_effect_id || effect.effect_id)} ends on ${target.state.template.name}.` });
      }
    }
    if (timing === "target_turn_end") M()?.expireTargetTurn(target.state);
    return { events, sequence };
  }

  function resolveSourceTiming(sequence, round, source, setup, timing) {
    const events = [];
    for (const target of [...setup.heroes, ...setup.monsters]) {
      const expiring = target.state.timed_effects.filter((effect) => effect.source_id === source.combatant_id && expiryDue(effect, round, timing));
      for (const effect of expiring) {
        if (!target.state.timed_effects.includes(effect)) continue;
        const removed = T().removeGroup(target.state, effect); if (!removed.length) continue;
        grantEndImmunity(target, effect);
        events.push({ sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: source.combatant_id, actor_name: source.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          removed_condition_ids: removed, feature_id: effect.source_effect_id || "condition-ended",
          animation: "condition-ended", description: `${label(effect.source_effect_id || effect.effect_id)} ends on ${target.state.template.name}.` });
      }
    }
    return { events, sequence };
  }

  function resolveAuraStart(sequence, round, target, setup) {
    const events = [];
    for (const source of [...setup.heroes, ...setup.monsters]) {
      if (source.combatant_id === target.combatant_id || source.state.is_dead || source.state.current_hp <= 0) continue;
      for (const aura of source.state.template.startTurnAuras || []) {
        if (S().distance(target, source) > aura.rangeFt || I().immune(target.state, source.combatant_id, aura.id)) continue;
        const save = V().resolveSavingThrow(target.state, aura.saveAbility, aura.saveDc, { magicalEffect: Boolean(aura.magicalEffect), againstCondition: aura.failureConditionId });
        let applied = null;
        if (save.succeeded && aura.successGrantsSourceImmunity) I().grant(target.state, source.combatant_id, aura.id);
        else if (!save.succeeded) applied = T().apply(target.state, aura.failureConditionId, source.combatant_id, {
          sourceEffectId: aura.id, appliedRound: round, expiresRound: round + aura.failureDurationRounds,
          expiryTiming: aura.failureExpiryTiming,
        });
        let description = `${target.state.template.name} ${save.succeeded ? "SUCCEEDS" : "FAILS"} a DC ${aura.saveDc} ${aura.saveAbility} save against ${source.state.template.name}'s ${aura.name}.`;
        if (applied) description += ` ${target.state.template.name} is ${applied}.`;
        events.push({ sequence: sequence++, round_number: round, event_type: "saving_throw", actor_id: source.combatant_id,
          actor_name: source.state.template.name, target_id: target.combatant_id, target_name: target.state.template.name,
          saving_throw_roll: save.roll, save_ability: aura.saveAbility, save_dc: aura.saveDc, save_succeeded: save.succeeded,
          applied_condition_ids: applied ? [applied] : [], feature_id: aura.id, animation: "condition-save", description });
      }
    }
    return { events, sequence };
  }

  const gazeOpponents = (member, setup) => member.side === "heroes" ? setup.monsters : setup.heroes;
  function gazeFailure(target, source, gaze, round, roll) {
    const immediate = gaze.immediateFailureMargin && gaze.immediateFailureConditionId && roll && roll.total <= gaze.saveDc - gaze.immediateFailureMargin;
    if (immediate) return T().apply(target.state, gaze.immediateFailureConditionId, source.combatant_id, { sourceEffectId: gaze.id, appliedRound: round });
    return T().apply(target.state, gaze.failureConditionId, source.combatant_id, {
      sourceEffectId: gaze.id, appliedRound: round, repeatSaveAbility: gaze.saveAbility,
      repeatSaveDc: gaze.saveDc, repeatSaveTiming: gaze.repeatSaveTiming,
      repeatSaveFailureConditionId: gaze.repeatSaveFailureConditionId,
    });
  }
  function resolveGazeStart(sequence, round, target, setup) {
    const rel = window.IRON_PIT_BROWSER_START_TURN_DAMAGE?.startTurn(sequence, round, target, setup) || { events: [], sequence };
    const aura = resolveAuraStart(rel.sequence, round, target, setup), events = [...rel.events, ...aura.events]; sequence = aura.sequence;
    for (const source of gazeOpponents(target, setup)) {
      const gaze = source.state.template.startTurnGaze;
      if (!gaze || Q().incapacitated(source.state) || Q().incapacitated(target.state)) continue;
      if (S().distance(target, source) > gaze.rangeFt || Q().has(target.state, "blinded") || Q().has(source.state, "blinded")) continue;
      const save = V().resolveSavingThrow(target.state, gaze.saveAbility, gaze.saveDc, { magicalEffect: Boolean(gaze.magicalEffect), againstCondition: gaze.failureConditionId });
      const applied = save.succeeded ? null : gazeFailure(target, source, gaze, round, save.roll);
      let description = `${target.state.template.name} ${save.succeeded ? "SUCCEEDS" : "FAILS"} a DC ${gaze.saveDc} ${gaze.saveAbility} save against ${source.state.template.name}'s ${gaze.name}.`;
      if (applied) description += ` ${target.state.template.name} is ${applied}.`;
      events.push({ sequence: sequence++, round_number: round, event_type: "saving_throw", actor_id: source.combatant_id,
        actor_name: source.state.template.name, target_id: target.combatant_id, target_name: target.state.template.name,
        saving_throw_roll: save.roll, save_ability: gaze.saveAbility, save_dc: gaze.saveDc, save_succeeded: save.succeeded,
        applied_condition_ids: applied ? [applied] : [], feature_id: gaze.id, animation: "condition-save", description });
      if (Q().incapacitated(target.state)) break;
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE = { resolveSourceTiming, resolveTargetTiming };
  window.IRON_PIT_BROWSER_GAZE = { startTurn: resolveGazeStart };
})();