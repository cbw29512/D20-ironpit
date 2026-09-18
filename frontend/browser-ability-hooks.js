(() => {
  "use strict";

  const PHASES = Object.freeze({
    TURN_START: "turnStart",
    BONUS_ACTION_WINDOW: "bonusActionWindow",
    MAIN_ACTION: "mainAction",
    TURN_FINALIZE: "turnFinalize",
    BEFORE_ATTACK_ROLL: "beforeAttackRoll",
    ON_HIT: "onHit",
    ON_MISS: "onMiss",
  });
  const PHASE_NAMES = Object.freeze(Object.values(PHASES));
  const PHASE_CONFIG = Object.freeze({
    [PHASES.TURN_START]: Object.freeze({ exclusive: false }),
    [PHASES.BONUS_ACTION_WINDOW]: Object.freeze({ exclusive: true }),
    [PHASES.MAIN_ACTION]: Object.freeze({ exclusive: true }),
    [PHASES.TURN_FINALIZE]: Object.freeze({ exclusive: false }),
    [PHASES.BEFORE_ATTACK_ROLL]: Object.freeze({ exclusive: false }),
    [PHASES.ON_HIT]: Object.freeze({ exclusive: false }),
    [PHASES.ON_MISS]: Object.freeze({ exclusive: false }),
  });
  const RULESETS = Object.freeze(["2014", "2024"]);
  const registry = new Map(PHASE_NAMES.map((phase) => [phase, []]));
  let registrationOrder = 0;

  function requirePhase(phase) {
    if (!PHASE_CONFIG[phase]) throw new Error(`Unknown ability-hook phase: ${String(phase)}.`);
    return PHASE_CONFIG[phase];
  }

  function validateDescriptor(phase, descriptor) {
    requirePhase(phase);
    if (!descriptor || typeof descriptor !== "object" || Array.isArray(descriptor)) {
      throw new Error("registerAbility requires a descriptor object.");
    }
    if (typeof descriptor.id !== "string" || !descriptor.id.trim()) {
      throw new Error("Ability descriptor requires a stable non-empty string id.");
    }
    if (descriptor.priority != null && (!Number.isFinite(descriptor.priority))) {
      throw new Error(`Ability "${descriptor.id}" priority must be a finite number.`);
    }
    if (!Array.isArray(descriptor.rulesets) || descriptor.rulesets.length === 0) {
      throw new Error(`Ability "${descriptor.id}" must declare one or more rulesets.`);
    }
    const invalid = descriptor.rulesets.filter((ruleset) => !RULESETS.includes(ruleset));
    if (invalid.length > 0) throw new Error(`Ability "${descriptor.id}" has unsupported ruleset: ${invalid[0]}.`);
    if (new Set(descriptor.rulesets).size !== descriptor.rulesets.length) {
      throw new Error(`Ability "${descriptor.id}" rulesets must not contain duplicates.`);
    }
    if (descriptor.appliesTo != null && typeof descriptor.appliesTo !== "function") {
      throw new Error(`Ability "${descriptor.id}" appliesTo must be a function.`);
    }
    if (typeof descriptor.resolve !== "function") {
      throw new Error(`Ability "${descriptor.id}" must provide a resolve(ctx) function.`);
    }
  }

  function registerAbility(phase, descriptor) {
    validateDescriptor(phase, descriptor);
    const list = registry.get(phase);
    const id = descriptor.id.trim();
    if (list.some((entry) => entry.id === id)) {
      throw new Error(`Ability "${id}" is already registered for phase "${phase}".`);
    }
    list.push({
      id,
      priority: descriptor.priority ?? 100,
      rulesets: [...descriptor.rulesets],
      appliesTo: descriptor.appliesTo || (() => true),
      resolve: descriptor.resolve,
      registrationOrder: registrationOrder++,
    });
    list.sort((a, b) => (a.priority - b.priority) || (a.registrationOrder - b.registrationOrder));
  }

  function unregisterAbility(phase, id) {
    requirePhase(phase);
    if (typeof id !== "string" || !id.trim()) throw new Error("unregisterAbility requires a non-empty id.");
    const list = registry.get(phase);
    registry.set(phase, list.filter((entry) => entry.id !== id.trim()));
  }

  function validateContext(phase, ctx) {
    requirePhase(phase);
    if (!ctx || typeof ctx !== "object" || Array.isArray(ctx)) throw new Error("runPhase requires a context object.");
    if (!Number.isInteger(ctx.sequence) || ctx.sequence < 0) throw new Error("runPhase requires a non-negative integer sequence.");
    if (ctx.events != null && !Array.isArray(ctx.events)) throw new Error("runPhase context events must be an array.");
    const ruleset = ctx.member?.state?.template?.ruleset;
    if (!RULESETS.includes(ruleset)) throw new Error(`runPhase requires a member with ruleset 2014 or 2024; received ${String(ruleset)}.`);
    return ruleset;
  }

  function normalizeResult(phase, abilityId, result, sequence) {
    if (result == null) return null;
    if (typeof result !== "object" || Array.isArray(result)) {
      throw new Error(`Ability "${abilityId}" must return null or a hook result object.`);
    }
    const { events, sequence: nextSequence, claimed } = result;
    if (!Array.isArray(events)) throw new Error(`Ability "${abilityId}" result.events must be an array.`);
    if (!Number.isInteger(nextSequence) || nextSequence < sequence) {
      throw new Error(`Ability "${abilityId}" result.sequence must be an integer >= the incoming sequence.`);
    }
    if (typeof claimed !== "boolean") throw new Error(`Ability "${abilityId}" result.claimed must be boolean.`);
    if (claimed && !PHASE_CONFIG[phase].exclusive) {
      throw new Error(`Ability "${abilityId}" cannot claim non-exclusive phase "${phase}".`);
    }
    if (events.some((event) => !event || typeof event !== "object" || typeof event.event_type !== "string")) {
      throw new Error(`Ability "${abilityId}" result.events must contain BattleEvent-like objects with event_type.`);
    }
    return { events, sequence: nextSequence, claimed };
  }

  function phaseFailure(phase, ability, stage, ctx, error) {
    console.error("Ability-hook phase failed", {
      phase, abilityId: ability.id, stage, combatant: ctx.member?.combatant_id,
      ruleset: ctx.member?.state?.template?.ruleset, error,
    });
    const wrapped = new Error(`Ability hook "${ability.id}" failed during ${stage} in phase "${phase}".`);
    wrapped.cause = error;
    throw wrapped;
  }

  function runPhase(phase, ctx) {
    const config = requirePhase(phase);
    const ruleset = validateContext(phase, ctx);
    let sequence = ctx.sequence;
    const events = ctx.events ? [...ctx.events] : [];
    let claimed = false;

    for (const ability of registry.get(phase)) {
      if (!ability.rulesets.includes(ruleset)) continue;
      let applies;
      try { applies = Boolean(ability.appliesTo(ctx.member, { ...ctx, sequence, events: [...events] })); }
      catch (error) { phaseFailure(phase, ability, "appliesTo", ctx, error); }
      if (!applies) continue;

      let result;
      try { result = ability.resolve({ ...ctx, sequence, events: [...events] }); }
      catch (error) { phaseFailure(phase, ability, "resolve", ctx, error); }
      const normalized = normalizeResult(phase, ability.id, result, sequence);
      if (!normalized) continue;
      events.push(...normalized.events);
      sequence = normalized.sequence;
      claimed = claimed || normalized.claimed;
      if (config.exclusive && normalized.claimed) break;
    }
    return { sequence, events, claimed };
  }

  function abilitiesFor(phase) {
    requirePhase(phase);
    return registry.get(phase).map(({ registrationOrder: _order, ...entry }) => ({ ...entry, rulesets: [...entry.rulesets] }));
  }

  function knownPhases() { return [...PHASE_NAMES]; }
  function _resetForTests() {
    for (const phase of PHASE_NAMES) registry.set(phase, []);
    registrationOrder = 0;
  }

  window.IRON_PIT_BROWSER_ABILITY_HOOKS = {
    PHASES, registerAbility, unregisterAbility, runPhase, abilitiesFor, knownPhases, _resetForTests,
  };
})();
