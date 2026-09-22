(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const D = () => window.IRON_PIT_DICE;

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
    const rider = source.state.template.turning_failure_damage || null;
    let sharedRolls = [];
    if (rider) {
      const score = source.state.template.ability_scores?.[rider.ability];
      if (!Number.isInteger(score)) throw new Error("Ability-scaled turning damage requires ability scores.");
      const diceCount = Math.max(1, Math.floor((score - 10) / 2));
      sharedRolls = Array.from({ length: diceCount }, () => D().roll(rider.dice_size));
    }
    const affectedStates = targets.map((target) => target.state);
    for (const target of targets) {
      const save = V().resolveSavingThrow(target.state, "wisdom", saveDc);
      let damageRoll = null, damageComponents = [];
      if (!save.succeeded && rider) {
        const raw = sharedRolls.reduce((sum, value) => sum + value, 0);
        const appliedDamage = A().adjustedDamage(target.state, raw, rider.damage_type);
        if (appliedDamage) A().applyDamage(target.state, appliedDamage, false, [rider.damage_type], affectedStates);
        damageRoll = { notation: `${sharedRolls.length}d${rider.dice_size}`, rolls: [...sharedRolls], modifier: 0, total: appliedDamage };
        damageComponents = [{
          source: rider.source_id, notation: damageRoll.notation, rolls: [...sharedRolls], modifier: 0,
          damage_type: rider.damage_type, total: raw, applied_total: appliedDamage,
        }];
      }
      const applied = save.succeeded || target.state.is_dead ? [] : apply(source, target, round, sourceEffectId, turnedEffectId);
      events.push({
        sequence: sequence++, round_number: round, event_type: "saving_throw",
        actor_id: source.combatant_id, actor_name: source.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        saving_throw_roll: save.roll, save_ability: "wisdom", save_dc: saveDc, save_succeeded: save.succeeded,
        damage_roll: damageRoll, damage_components: damageComponents,
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