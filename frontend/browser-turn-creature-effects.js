(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };

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

  window.IRON_PIT_BROWSER_TURN_CREATURE_EFFECTS = { apply };
})();
