(() => {
  "use strict";

  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const MODIFIER_KINDS = new Set(["attacks-against-advantage", "speed"]);

  const sizeAllowed = (target, maximum) => !maximum || S().sizeAtMost(target, maximum);

  function applyCondition(target, sourceId, sourceEffectId, effect, options) {
    const condition = T().apply(target.state, effect.condition, sourceId, {
      sourceEffectId, appliedRound: options.round,
      expiresAtStartOfSourceTurn: Boolean(effect.expiresAtStartOfSourceTurn),
      expiryTiming: effect.expiryTiming || null,
      repeatSaveAbility: effect.repeatSaveAbility || null,
      repeatSaveDc: effect.repeatSaveDc || null,
      repeatSaveTiming: effect.repeatSaveTiming || null,
      repeatSaveDelayRounds: effect.repeatSaveDelayRounds || 0,
      repeatSaveFailureCondition: effect.repeatSaveFailureCondition || null,
      repeatSaveFailureContinues: effect.repeatSaveFailureContinues !== false,
      repeatSaveFailureDurationRounds: effect.repeatSaveFailureDurationRounds ?? null,
      repeatSaveFailureEndsOnDamage: Boolean(effect.repeatSaveFailureEndsOnDamage),
      repeatSaveFailureAllowedRemovalActionIds: effect.repeatSaveFailureAllowedRemovalActionIds || [],
      automaticSuccessAfterRounds: effect.automaticSuccessAfterRounds ?? null,
      allowedRemovalActionIds: effect.allowedRemovalActionIds || [],
      periodicDamage: effect.periodicDamage || null,
    });
    if (!condition) return [];
    const applied = [condition];
    for (const linked of (effect.linkedConditions || [])) {
      const linkedId = T().apply(target.state, linked, sourceId, {
        sourceEffectId, appliedRound: options.round,
      });
      if (linkedId) applied.push(linkedId);
    }
    return applied;
  }

  function apply(target, sourceId, sourceEffectId, effects, options = {}) {
    if (target.state.is_dead || !target.state.is_alive) return [];
    const applied = [];
    for (const [index, effect] of (effects || []).entries()) {
      if (effect.kind === "prone") {
        if (sizeAllowed(target, effect.maxTargetSize) && !I().immune(target.state, "prone")) {
          if (!target.state.active_effect_ids.includes("prone")) target.state.active_effect_ids.push("prone");
          applied.push("prone");
        }
      } else if (effect.kind === "grapple") {
        if (sizeAllowed(target, effect.maxTargetSize)) {
          applied.push(...G().apply(target.state, sourceId, effect.escapeDc, options.range || 0, Boolean(effect.restrains)));
        }
      } else if (effect.kind === "condition") {
        if (!sizeAllowed(target, effect.maxTargetSize)) continue;
        applied.push(...applyCondition(target, sourceId, sourceEffectId, effect, options));
      } else if (effect.kind === "turn-restriction") {
        if (effect.requiresCondition && !target.state.active_effect_ids.includes(effect.requiresCondition)) continue;
        const restriction = T().apply(target.state, "turn-restriction", sourceId, {
          sourceEffectId, appliedRound: options.round,
          expiryTiming: effect.expiryTiming,
          actionOrBonusOnly: Boolean(effect.actionOrBonusOnly),
          reactionsDisabled: Boolean(effect.reactionsDisabled),
          speedMultiplier: effect.speedMultiplier == null ? 1 : effect.speedMultiplier,
          requiresActiveEffectId: effect.requiresCondition || null,
          trackActiveEffect: false,
        });
        if (restriction) applied.push(restriction);
      } else if (effect.kind === "timed-penalty") {
        const penalty = T().applyPenalty(target.state, sourceId, sourceEffectId, options.round, effect);
        if (penalty) applied.push(penalty);
      } else if (MODIFIER_KINDS.has(effect.kind)) {
        M().applyEffect(target.state, sourceId, sourceEffectId, effect, index, "failed-save");
      } else {
        throw new Error(`Unsupported failed-save effect kind: ${effect.kind}.`);
      }
    }
    return [...new Set(applied)];
  }

  function eligible(state, filter = {}) {
    const creatureType = String(state.template.creature_type || "").toLowerCase();
    const tags = new Set((state.template.creature_tags || []).map((item) => String(item).toLowerCase()));
    if ((filter.excludedCreatureTypes || []).some((item) => String(item).toLowerCase() === creatureType)) return false;
    return !(filter.excludedTags || []).some((item) => tags.has(String(item).toLowerCase()));
  }

  function hitSave(attacker, target, attack, round, distance, setup = null) {
    const rider = attack.onHitSavingThrow;
    if (!rider || target.state.is_dead || !target.state.is_alive) return null;
    if (!eligible(target.state, rider.targetFilter)) return { eligible: false, applied: [] };
    const saves = window.IRON_PIT_BROWSER_SAVES;
    if (!saves) throw new Error("Browser save resolver is not loaded.");
    const aura = window.IRON_PIT_BROWSER_AURAS || { savingThrowAdvantageSources: () => 0 };
    const result = saves.resolveSavingThrow(
      target.state, rider.saveAbility, rider.dc, Boolean(rider.magicalEffect), aura.savingThrowAdvantageSources(target, setup),
    );
    const applied = result.succeeded ? [] : apply(
      target, attacker.combatant_id, attack.id, rider.failureEffects || [], { round, range: attack.reach || distance },
    );
    return { eligible: true, roll: result.roll, ability: rider.saveAbility, dc: rider.dc, succeeded: result.succeeded, applied };
  }

  function installHitSaveBridge() {
    const attackApi = window.IRON_PIT_BROWSER_ATTACK;
    if (!attackApi || attackApi.__hitSaveBridgeInstalled) return;
    const base = attackApi.resolveAttack;
    attackApi.resolveAttack = function (...args) {
      const [, round, attacker, target, attack, distance, extra = {}] = args;
      const event = base(...args);
      if (!event.hit || !attack.onHitSavingThrow) return event;
      const members = extra.setup ? [...extra.setup.heroes, ...extra.setup.monsters] : [];
      const actual = members.find((item) => item.combatant_id === event.target_id) || target;
      const outcome = hitSave(attacker, actual, attack, round, distance, extra.setup || null);
      if (!outcome?.eligible) return event;
      event.saving_throw_roll = outcome.roll; event.save_ability = outcome.ability;
      event.save_dc = outcome.dc; event.save_succeeded = outcome.succeeded;
      event.applied_condition_ids = [...new Set([...(event.applied_condition_ids || []), ...outcome.applied])];
      event.description += ` ${actual.state.template.name} ${outcome.succeeded ? "succeeds" : "fails"} the DC ${outcome.dc} ${outcome.ability} hit-effect save.`;
      return event;
    };
    attackApi.__hitSaveBridgeInstalled = true;
  }

  window.IRON_PIT_BROWSER_SAVE_FAILURE_EFFECTS = { apply, eligible, hitSave };
  installHitSaveBridge();
})();