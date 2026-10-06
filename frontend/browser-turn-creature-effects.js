(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const DD = () => {
    const rules = window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES;
    if (!rules?.resolveDamage) throw new Error("Turn-creature damage requires the shared damage resolver.");
    return rules;
  };
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;
  const D = () => window.IRON_PIT_DICE;

  function fraction(value) {
    const text = String(value);
    if (!text.includes("/")) {
      const parsed = Number(text);
      if (!Number.isFinite(parsed)) throw new Error(`Invalid Challenge Rating: ${text}`);
      return parsed;
    }
    const [numerator, denominator] = text.split("/").map(Number);
    if (!Number.isFinite(numerator) || !Number.isFinite(denominator) || denominator === 0) {
      throw new Error(`Invalid Challenge Rating: ${text}`);
    }
    return numerator / denominator;
  }

  function challengeRatingAtOrBelow(target, maximum) {
    if (maximum == null || target.state.template.challenge_rating == null) return false;
    return fraction(target.state.template.challenge_rating) <= fraction(maximum);
  }

  function apply(source, target, round, sourceEffectId, turnedEffectId, options = {}) {
    const expiresRounds = Object.prototype.hasOwnProperty.call(options, "expiresRounds") ? options.expiresRounds : 10;
    const expiryTiming = Object.prototype.hasOwnProperty.call(options, "expiryTiming") ? options.expiryTiming : "source_turn_start";
    const common = {
      sourceEffectId, appliedRound: round, sourceTemplate: source.state.template, sourceIsMagical: true,
      expiresRound: expiresRounds == null ? null : round + expiresRounds,
      expiryTiming, endsOnDamage: true,
      endsIfSourceIncapacitated: options.endsIfSourceIncapacitated !== false,
      endsIfSourceDead: options.endsIfSourceDead !== false,
    };
    const applied = [T().apply(
      target.state, turnedEffectId, source.combatant_id,
      {
        ...common,
        turnBehavior: options.turnBehavior || "forced_retreat",
        suppressAction: Boolean(options.suppressAction),
        suppressBonusAction: Boolean(options.suppressBonusAction),
        suppressReactions: Boolean(options.suppressReactions),
        suppressMovement: Boolean(options.suppressMovement),
        repeatSaveAbility: options.repeatSaveTiming ? "wisdom" : null,
        repeatSaveDc: options.repeatSaveTiming ? options.saveDc : null,
        repeatSaveTiming: options.repeatSaveTiming || null,
        repeatSaveContext: options.repeatSaveTiming ? { magical_effect: true,
          source_creature_type: source.state.template.creature_type,
          condition_id: options.includeFrightened === false ? null : "frightened",
          effect_tags: ["turning", ...(options.includeFrightened === false ? [] : ["frightened"])] } : null,
      },
    )];
    const conditions = [];
    if (options.includeFrightened !== false) conditions.push("frightened");
    if (options.includeIncapacitated !== false) conditions.push("incapacitated");
    for (const condition of conditions) {
      if (!I().immune(target.state, condition)) {
        applied.push(T().apply(target.state, condition, source.combatant_id, common));
      }
    }
    return applied.filter(Boolean);
  }

  function resolve(sequence, round, source, targets, saveDc, sourceEffectId, turnedEffectId, resourceRemaining, featureName, options = {}) {
    try {
    const events = [];
    const rider = source.state.template.turning_failure_damage || null;
    const destroyMaxCr = source.state.template.turning_failure_destroy_max_cr || null;
    let sharedRolls = [];
    if (rider) {
      const score = source.state.template.ability_scores?.[rider.ability];
      if (!Number.isInteger(score)) throw new Error("Ability-scaled turning damage requires ability scores.");
      const diceCount = Math.max(1, Math.floor((score - 10) / 2));
      sharedRolls = Array.from({ length: diceCount }, () => D().roll(rider.dice_size));
    }
    const affectedStates = options.affectedStates || targets.map((target) => target.state);
    for (const target of targets) {
      const hpBefore = target.state.current_hp;
      const setup = options.setup;
      const auraRuntime = window.IRON_PIT_BROWSER_FRIENDLY_SAVE_AURAS;
      const members = setup ? [...setup.heroes, ...setup.monsters] : targets;
      if (members.some((m) => (m.state.template.timed_self_buff_actions || []).some((a) => a.friendlySaveAdvantageAura))
          && (!setup || !auraRuntime)) throw new Error("Turning save buffs require encounter and aura runtime.");
      if (setup && auraRuntime) auraRuntime.sync(setup);
      const context = { magicalEffect: true, sourceCreatureType: source.state.template.creature_type,
        conditionId: options.includeFrightened === false ? null : "frightened",
        effectTags: ["turning", ...(options.includeFrightened === false ? [] : ["frightened"])],
        roundNumber: round, encounterRoller: target, setup };
      const buffs = window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS?.saveAdvantageSourceNames?.(target.state, "wisdom", context) || [];
      const save = V().resolveSavingThrow(target.state, "wisdom", saveDc, context);
      let damageRoll = null, damageComponents = [];
      if (!save.succeeded && rider) {
        const raw = sharedRolls.reduce((sum, value) => sum + value, 0);
        const resolvedDamage = DD().resolveDamage(target.state, raw, rider.damage_type);
        const appliedDamage = resolvedDamage.applied;
        if (appliedDamage) A().applyDamage(target.state, appliedDamage, false, [rider.damage_type], affectedStates);
        damageRoll = { notation: `${sharedRolls.length}d${rider.dice_size}`, rolls: [...sharedRolls], modifier: 0, total: appliedDamage };
        damageComponents = [{
          source: rider.source_id, notation: damageRoll.notation, rolls: [...sharedRolls], modifier: 0,
          damage_type: rider.damage_type, total: raw, applied_total: appliedDamage,
          absorbed_healing: resolvedDamage.healed || 0,
          absorption_source_name: resolvedDamage.sourceName || null,
        }];
      }
      let destroyed = false;
      if (!save.succeeded && !target.state.is_dead && challengeRatingAtOrBelow(target, destroyMaxCr)) {
        if (!Z()?.reduceToZero) throw new Error("Turning destruction requires browser-zero-hp.js.");
        Z().reduceToZero(target.state, affectedStates);
        destroyed = true;
      }
      const applied = save.succeeded || target.state.is_dead || destroyed ? [] : apply(
        source, target, round, sourceEffectId, turnedEffectId, { ...options, saveDc },
      );
      events.push({
        sequence: sequence++, round_number: round, event_type: "saving_throw",
        actor_id: source.combatant_id, actor_name: source.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        saving_throw_roll: save.roll, save_ability: "wisdom", save_dc: saveDc, save_succeeded: save.succeeded,
        damage_roll: damageRoll, damage_components: damageComponents,
        applied_condition_ids: applied, feature_id: sourceEffectId, resource_remaining: resourceRemaining,
        hp_before: hpBefore, hp_after: target.state.current_hp, is_dead: target.state.is_dead,
        animation: "turn-undead",
        description: target.state.template.name + " " + (save.succeeded ? "resists" : "fails")
          + " " + source.state.template.name + "'s " + featureName
          + (destroyed ? " and is destroyed." : ".")
          + (buffs.length ? ` Save Advantage: ${buffs.join(", ")}.` : ""),
      });
    }
    return { events, sequence };
    } catch (error) {
      console.error("Failed browser turning saves.", { source: source?.combatant_id, round, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TURN_CREATURE_EFFECTS = { apply, resolve };
})();