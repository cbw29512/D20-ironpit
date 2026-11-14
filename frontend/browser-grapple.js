(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const A = () => window.IRON_PIT_BROWSER_ABILITY_CHECKS;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { speedZero: (state) => state.active_effect_ids.includes("restrained"), incapacitated: (state) => state.is_unconscious };
  const C = () => window.IRON_PIT_BROWSER_DEBUFF_COUNTERS || {
    movementCost: () => null,
    prevented: () => false,
  };
  const E = () => window.IRON_PIT_ACTION_ECONOMY || {
    available: (state, cost) => cost === "action" && state.action_available,
    spend: (state) => { state.action_available = false; },
  };

  function sync(state) {
    const grappled = state.grapple_sources.length > 0;
    // Do not erase an unrelated timed/innate Restrained condition when a
    // Grapple ends; all three sources share one canonical condition id.
    const restrained = Boolean(state.swallowed)
      || state.grapple_sources.some((source) => source.restrains)
      || (state.timed_effects || []).some((effect) => effect.effect_id === "restrained")
      || (state.template?.innate_condition_ids || []).includes("restrained");
    state.active_effect_ids = state.active_effect_ids.filter((id) => id !== "grappled" && id !== "restrained");
    if (grappled) {
      state.active_effect_ids.push("grappled");
      state.active_effect_ids = state.active_effect_ids.filter((id) => id !== "dodge");
    }
    if (restrained) state.active_effect_ids.push("restrained");
    if (state.grapple_sources.some(source => source.blinds)
      && !state.active_effect_ids.includes("blinded")) state.active_effect_ids.push("blinded");
  }

  function apply(state, sourceId, escapeDc, rangeFt, restrains = false, sourceIsMagical = false, periodicDamage = null, linked = {}) {
    if (I().immune(state, "grappled", null, { sourceIsMagical })) return [];
    const blindedPreexisting = (state.active_effect_ids || []).includes("blinded");
    state.grapple_sources = state.grapple_sources.filter((source) => source.source_id !== sourceId);
    const effectiveRestrains = restrains && !I().immune(state, "restrained", null, { sourceIsMagical });
    state.grapple_sources.push({
      source_id: sourceId, escape_dc: escapeDc, range_ft: rangeFt,
      restrains: effectiveRestrains, source_is_magical: Boolean(sourceIsMagical),
      periodic_damage: periodicDamage,
      blinds: Boolean(linked.blinds) && !I().immune(state, "blinded", null, {sourceIsMagical}),
      prevents_breathing: Boolean(linked.preventsBreathing),
      blinded_preexisting: blindedPreexisting,
      linked_effect_id: linked.effectId || null,
      breakable_object: linked.breakableObject ? {
        armor_class: linked.breakableObject.armorClass,
        current_hp: linked.breakableObject.hitPoints,
        damage_immunities: [...(linked.breakableObject.damageImmunities || [])],
        damage_vulnerabilities: [...(linked.breakableObject.damageVulnerabilities || [])],
      } : null,
      check_save_disadvantage_abilities: [...(linked.checkSaveDisadvantageAbilities || [])],
    });
    sync(state);
    return effectiveRestrains ? ["grappled", "restrained"] : ["grappled"];
  }

  function release(state, sourceId) {
    const removed = state.grapple_sources.filter(source => source.source_id === sourceId);
    state.grapple_sources = state.grapple_sources.filter((source) => source.source_id !== sourceId);
    sync(state);
    if (!state.grapple_sources.some((source) => source.prevents_breathing)) {
      // Reset while resolving the release, before any later healing Action.
      state.breath_hold_rounds_remaining = null;
      state.breath_survival_rounds_remaining = null;
      state.suffocating_at_zero = false;
    }
    if (removed.some(source => source.blinds)
      && !removed.some(source => source.blinded_preexisting)
      && !state.grapple_sources.some(source => source.blinds)
      && !(state.timed_effects || []).some(effect => effect.effect_id === "blinded")) {
      state.active_effect_ids = state.active_effect_ids.filter(id => id !== "blinded");
    }
  }

  function resolveMovementCounters(state) {
    const resolved = [];
    for (const source of [...state.grapple_sources]) {
      const ids = source.restrains ? ["grappled", "restrained"] : ["grappled"];
      const costs = ids.map((id) => C().movementCost(state, id, { sourceIsMagical: Boolean(source.source_is_magical) }))
        .filter((cost) => cost != null);
      if (!costs.length) continue;
      const cost = Math.min(...costs);
      if (state.movement_remaining_ft < cost) continue;
      state.movement_remaining_ft -= cost;
      release(state, source.source_id);
      resolved.push({ debuffId: source.restrains ? "restrained" : "grappled", sourceId: source.source_id, movementCost: cost });
    }
    return resolved;
  }

  const speedIsZero = (state) => state.grapple_sources.some((source) =>
    !C().prevented(state, "speed-reduction", { sourceIsMagical: Boolean(source.source_is_magical) }))
    || Q().speedZero(state);
  function checkSaveDisadvantage(state, ability) {
    try {
      if (!ability) return 0;
      return (state.grapple_sources || []).filter(source =>
        (source.check_save_disadvantage_abilities || []).includes(ability)).length;
    } catch (error) {
      console.error("Grapple-linked check/save disadvantage failed", { ability, error });
      throw error;
    }
  }

  function attackDisadvantage(state, targetId) {
    if (!state.grapple_sources.length) return 0;
    return state.grapple_sources.some((source) => source.source_id === targetId) ? 0 : 1;
  }

  function sourceGrappleCount(setup, sourceId) {
    if (!setup) throw new Error("Source-limited grapple requires encounter setup.");
    return [...setup.heroes, ...setup.monsters].filter((member) =>
      member.combatant_id !== sourceId && member.state.is_alive && !member.state.is_dead
      && (member.state.grapple_sources || []).some((grapple) => grapple.source_id === sourceId)).length;
  }

  function sourceHasActiveGrapple(setup, sourceId) {
    return sourceGrappleCount(setup, sourceId) > 0;
  }

  function cleanup(setup) {
    const members = new Map([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
    for (const target of members.values()) {
      if (target.state.is_dead || !target.state.is_alive) {
        for (const source of [...target.state.grapple_sources]) {
          release(target.state, source.source_id);
        }
        sync(target.state);
        continue;
      }
      const stale = target.state.grapple_sources.filter((source) => {
        const grappler = members.get(source.source_id);
        if (!grappler || grappler.state.is_dead || !grappler.state.is_alive || Q().incapacitated(grappler.state)) return true;
        return setup.arena_mode !== "formation"
          && Math.abs(grappler.position_ft - target.position_ft) > source.range_ft;
      });
      for (const source of stale) release(target.state, source.source_id);
      sync(target.state);
    }
  }

  const shouldEscape = (state) => E().available(state, "action") && state.grapple_sources.some((source) => source.restrains);
  function escape(sequence, round, member, setup = null) {
    const state = member.state;
    if (!E().available(state, "action")) throw new Error("Action is unavailable to escape grapple.");
    const source = state.grapple_sources.find((item) => item.restrains) || state.grapple_sources[0];
    // Use the same universal skill-check resolver as all other ability checks:
    // missing proficiency means untrained ability modifier, not a missing action.
    if (typeof A()?.skillBonus !== "function")
      throw new Error("Canonical skill-check runtime is unavailable for grapple escape.");
    const athletics = A().skillBonus(state, "strength", "athletics");
    const acrobatics = A().skillBonus(state, "dexterity", "acrobatics");
    const useAthletics = athletics >= acrobatics;
    const bonus = useAthletics ? athletics : acrobatics;
    const ability = useAthletics ? "strength" : "dexterity";
    const advantage = useAthletics && (state.active_effect_ids.includes("rage") || state.template.athletics_advantage) ? 1 : 0;
    const disadvantage = (state.active_effect_ids.includes("poisoned") || Q().has(state, "frightened", setup) ? 1 : 0)
      + (window.IRON_PIT_BROWSER_TIMED_CONTROL?.abilityD20Disadvantage(state, ability) || 0);
    let roll = R().d20(
      bonus,
      A()?.mode ? A().mode(state, advantage, disadvantage, { ability }) : R().modeFromSources(advantage, disadvantage),
    );
    const needsCheckRuntime = (state.template.ability_check_minimums || []).some(
      (rule) => rule.ability === ability,
    ) || (state.template.failed_d20_test_override_grants || []).some(
      (grant) => (grant.test_kinds || []).includes("ability_check"),
    ) || (state.template.resource_backed_d20_bonus_dice || []).some(
      (grant) => (grant.test_kinds || []).includes("ability_check"),
    );
    if (needsCheckRuntime && !A()) throw new Error("Ability-check runtime is not loaded.");
    const resolved = A()?.resolve
      ? A().resolve(state, ability, roll, source.escape_dc, {
          roller: member,
          setup,
        })
      : { roll, succeeded: roll.total >= source.escape_dc };
    roll = resolved.roll;
    const success = resolved.succeeded;
    E().spend(state, "action");
    if (success) {
      release(state, source.source_id);
      if (!speedIsZero(state)) state.movement_remaining_ft = Math.max(state.movement_remaining_ft, state.template.speed_ft);
    }
    const check = useAthletics ? "strength (athletics)" : "dexterity (acrobatics)";
    return {
      sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
      actor_name: state.template.name, target_id: source.source_id, ability_check_roll: roll,
      check_ability: check, check_dc: source.escape_dc, check_succeeded: success,
      feature_id: "escape-grapple",
      animation: "escape-grapple",
      description: `${state.template.name} ${success ? "escapes" : "fails to escape"} the grapple with ${check} against DC ${source.escape_dc}.`,
    };
  }

  window.IRON_PIT_BROWSER_GRAPPLE = { apply, attackDisadvantage, checkSaveDisadvantage, cleanup, escape, release, resolveMovementCounters, shouldEscape, sourceGrappleCount, sourceHasActiveGrapple, speedIsZero };
})();
