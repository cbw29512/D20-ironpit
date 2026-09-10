(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { speedZero: (state) => state.active_effect_ids.includes("restrained") };
  const T = () => window.IRON_PIT_BROWSER_TACTICAL_MIND;
  const F = () => window.IRON_PIT_BROWSER_FRIGHTENED;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const E = () => window.IRON_PIT_ACTION_ECONOMY || {
    available: (state, cost) => cost === "action" && state.action_available,
    spend: (state) => { state.action_available = false; },
  };

  function dropOrphanedLinked(state, removed) {
    const remaining = new Set(state.grapple_sources.flatMap((source) => source.linked_conditions || []));
    const timed = new Set((state.timed_effects || []).map((effect) => effect.effect_id));
    state.active_effect_ids = state.active_effect_ids.filter((id) => !removed.has(id) || remaining.has(id) || timed.has(id));
  }
  function sync(state) {
    const grappled = state.grapple_sources.length > 0;
    const restrained = state.grapple_sources.some((source) => source.restrains);
    state.active_effect_ids = state.active_effect_ids.filter((id) => id !== "grappled" && id !== "restrained");
    if (grappled) {
      state.active_effect_ids.push("grappled");
      state.active_effect_ids = state.active_effect_ids.filter((id) => id !== "dodge");
    }
    if (restrained) state.active_effect_ids.push("restrained");
    for (const condition of new Set(state.grapple_sources.flatMap((source) => source.linked_conditions || []))) {
      if (!state.active_effect_ids.includes(condition)) state.active_effect_ids.push(condition);
    }
  }

  function apply(state, sourceId, escapeDc, rangeFt, restrains = false, linkedConditions = []) {
    if (I().immune(state, "grappled")) return [];
    const replaced = state.grapple_sources.filter((source) => source.source_id === sourceId);
    state.grapple_sources = state.grapple_sources.filter((source) => source.source_id !== sourceId);
    const effectiveRestrains = restrains && !I().immune(state, "restrained");
    const linked = linkedConditions.filter((condition) => !I().immune(state, condition));
    state.grapple_sources.push({ source_id: sourceId, escape_dc: escapeDc, range_ft: rangeFt, restrains: effectiveRestrains, linked_conditions: linked });
    dropOrphanedLinked(state, new Set(replaced.flatMap((source) => source.linked_conditions || [])));
    sync(state);
    return ["grappled", ...(effectiveRestrains ? ["restrained"] : []), ...linked];
  }

  function release(state, sourceId) {
    const removed = state.grapple_sources.filter((source) => source.source_id === sourceId);
    state.grapple_sources = state.grapple_sources.filter((source) => source.source_id !== sourceId);
    dropOrphanedLinked(state, new Set(removed.flatMap((source) => source.linked_conditions || [])));
    sync(state);
  }

  const speedIsZero = (state) => state.grapple_sources.length > 0 || Q().speedZero(state);
  function attackDisadvantage(state, targetId) {
    if (!state.grapple_sources.length) return 0;
    return state.grapple_sources.some((source) => source.source_id === targetId) ? 0 : 1;
  }

  function cleanup(setup) {
    const members = new Map([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
    for (const target of members.values()) {
      const removed = new Set();
      target.state.grapple_sources = target.state.grapple_sources.filter((source) => {
        const grappler = members.get(source.source_id);
        const keep = Boolean(grappler && !grappler.state.is_dead && !grappler.state.is_unconscious
          && Math.abs(grappler.position_ft - target.position_ft) <= source.range_ft);
        if (!keep) for (const condition of source.linked_conditions || []) removed.add(condition);
        return keep;
      });
      dropOrphanedLinked(target.state, removed);
      sync(target.state);
    }
  }

  const shouldEscape = (state) => E().available(state, "action") && state.grapple_sources.some((source) => source.restrains);
  function escape(sequence, round, member, setup = null) {
    const state = member.state;
    if (!E().available(state, "action")) throw new Error("Action is unavailable to escape grapple.");
    const source = state.grapple_sources.find((item) => item.restrains) || state.grapple_sources[0];
    const athletics = state.template.skill_bonuses?.athletics;
    const acrobatics = state.template.skill_bonuses?.acrobatics;
    if (athletics == null && acrobatics == null) throw new Error(`${state.template.name} lacks certified grapple escape bonuses.`);
    const useAthletics = athletics != null && (acrobatics == null || athletics >= acrobatics);
    const bonus = useAthletics ? athletics : acrobatics;
    const advantage = useAthletics && (state.active_effect_ids.includes("rage") || state.template.athletics_advantage) ? 1 : 0;
    let disadvantage = state.active_effect_ids.includes("poisoned") ? 1 : 0;
    if (state.active_effect_ids.includes("frightened")) { if (!setup || !F()) throw new Error("Frightened grapple check requires encounter context."); disadvantage += F().d20Disadvantage(state, setup); }
    let roll = R().d20(bonus, R().modeFromSources(advantage, disadvantage));
    if (M()) roll = M().applyD20Bonus(state, "ability-check-bonus-die", roll);
    let success = roll.total >= source.escape_dc, tactical = null;
    if (!success && T()) {
      tactical = T().apply(state, roll, source.escape_dc);
      roll = tactical.roll; success = tactical.succeeded;
    }
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
      feature_id: "escape-grapple", resource_remaining: tactical?.used ? tactical.resource_remaining : null,
      animation: "escape-grapple",
      description: `${state.template.name} ${success ? "escapes" : "fails to escape"} the grapple${tactical?.used ? " after using Tactical Mind" : ""} with ${check} against DC ${source.escape_dc}.`,
    };
  }

  window.IRON_PIT_BROWSER_GRAPPLE = { apply, attackDisadvantage, cleanup, escape, release, shouldEscape, speedIsZero };
})();
