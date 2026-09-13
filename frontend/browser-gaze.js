(() => {
  "use strict";
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES;

  const opponents = (member, setup) => member.side === "heroes" ? setup.monsters : setup.heroes;
  const mutualSight = (target, source) => !Q().has(target.state, "blinded") && !Q().has(source.state, "blinded");

  function applyFailure(target, source, gaze, round, roll) {
    const immediate = gaze.immediateFailureMargin && gaze.immediateFailureConditionId && roll
      && roll.total <= gaze.saveDc - gaze.immediateFailureMargin;
    if (immediate) return T().apply(target.state, gaze.immediateFailureConditionId, source.combatant_id, {
      sourceEffectId: gaze.id, appliedRound: round,
    });
    return T().apply(target.state, gaze.failureConditionId, source.combatant_id, {
      sourceEffectId: gaze.id, appliedRound: round,
      repeatSaveAbility: gaze.saveAbility, repeatSaveDc: gaze.saveDc,
      repeatSaveTiming: gaze.repeatSaveTiming,
      repeatSaveFailureConditionId: gaze.repeatSaveFailureConditionId,
    });
  }

  function startTurn(sequence, round, target, setup) {
    const events = [];
    for (const source of opponents(target, setup)) {
      const gaze = source.state.template.startTurnGaze;
      if (!gaze || Q().incapacitated(source.state) || Q().incapacitated(target.state)) continue;
      if (S().distance(target, source) > gaze.rangeFt || !mutualSight(target, source)) continue;
      const save = V().resolveSavingThrow(target.state, gaze.saveAbility, gaze.saveDc, {
        magicalEffect: Boolean(gaze.magicalEffect), againstCondition: gaze.failureConditionId,
      });
      const applied = save.succeeded ? null : applyFailure(target, source, gaze, round, save.roll);
      let description = `${target.state.template.name} ${save.succeeded ? "SUCCEEDS" : "FAILS"} a DC ${gaze.saveDc} ${gaze.saveAbility} save against ${source.state.template.name}'s ${gaze.name}.`;
      if (applied) description += ` ${target.state.template.name} is ${applied}.`;
      events.push({ sequence: sequence++, round_number: round, event_type: "saving_throw",
        actor_id: source.combatant_id, actor_name: source.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        saving_throw_roll: save.roll, save_ability: gaze.saveAbility, save_dc: gaze.saveDc,
        save_succeeded: save.succeeded, applied_condition_ids: applied ? [applied] : [],
        feature_id: gaze.id, animation: "condition-save", description });
      if (Q().incapacitated(target.state)) break;
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_GAZE = { startTurn };
})();
