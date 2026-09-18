(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const V = () => window.IRON_PIT_BROWSER_SAVES;

  function apply(source, target, round, sourceEffectId, turnedEffectId) {
    const common = {
      sourceEffectId, appliedRound: round, expiresRound: round + 10,
      expiryTiming: "source_turn_start", endsOnDamage: true,
      endsIfSourceIncapacitated: true, endsIfSourceDead: true,
    };
    const applied = [T().apply(
      target.state, turnedEffectId, source.combatant_id,
      { ...common, turnBehavior: "forced_retreat" },
    )];
    for (const condition of ["frightened", "incapacitated"]) {
      if (!I().immune(target.state, condition)) {
        applied.push(T().apply(target.state, condition, source.combatant_id, common));
      }
    }
    return applied.filter(Boolean);
  }

  function resolve(sequence, round, source, targets, saveDc, sourceEffectId, turnedEffectId, resourceRemaining, featureName) {
    const events = [];
    for (const target of targets) {
      const save = V().resolveSavingThrow(target.state, "wisdom", saveDc);
      const applied = save.succeeded ? [] : apply(source, target, round, sourceEffectId, turnedEffectId);
      events.push({
        sequence: sequence++, round_number: round, event_type: "saving_throw",
        actor_id: source.combatant_id, actor_name: source.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        saving_throw_roll: save.roll, save_ability: "wisdom", save_dc: saveDc, save_succeeded: save.succeeded,
        applied_condition_ids: applied, feature_id: sourceEffectId, resource_remaining: resourceRemaining,
        animation: "turn-undead",
        description: target.state.template.name + " " + (save.succeeded ? "resists" : "fails")
          + " " + source.state.template.name + "'s " + featureName + ".",
      });
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_TURN_CREATURE_EFFECTS = { apply, resolve };
})();