(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;

  function grantZeroHpTemporaryHp(sequence, round, source, rule, allyKill) {
    const scores = source.state.template.ability_scores;
    const level = source.state.template.level;
    if (!scores || !Number.isInteger(level)) {
      throw new Error("Zero-HP Temporary HP trigger requires certified ability scores and level.");
    }
    const score = scores[rule.ability];
    if (!Number.isFinite(score)) throw new Error("Zero-HP Temporary HP trigger ability score is unavailable.");
    const amount = Math.max(
      rule.minimum ?? 1,
      (rule.flat_bonus || 0) + (rule.per_level || 0) * level + Math.floor((score - 10) / 2),
    );
    const before = source.state.temporary_hp || 0;
    const stateRuntime = S();
    if (!stateRuntime?.grantTemporaryHp) throw new Error("Browser Temporary HP runtime is not loaded.");
    const after = stateRuntime.grantTemporaryHp(source.state, amount);
    const trigger = allyKill
      ? "after an ally reduced a nearby hostile creature to 0 HP"
      : "after reducing a hostile creature to 0 HP";
    return {
      sequence: sequence + 1,
      event: {
        sequence,
        round_number: round,
        event_type: "feature",
        actor_id: source.combatant_id,
        actor_name: source.state.template.name,
        target_id: source.combatant_id,
        target_name: source.state.template.name,
        hp_before: source.state.current_hp,
        hp_after: source.state.current_hp,
        temporary_hp_before: before,
        temporary_hp_after: after,
        feature_id: rule.source_id,
        animation: "feature",
        description: `${source.state.template.name} gains ${amount} Temporary HP from ${rule.source_name} ${trigger}.`,
      },
    };
  }

  function resolveWitnessedZeroHpTriggers(sequence, round, killer, triggeringEvent, setup, memberById) {
    const target = memberById(setup, triggeringEvent.target_id);
    if (!target || !Number.isFinite(triggeringEvent.hp_before) || !Number.isFinite(triggeringEvent.hp_after)) {
      return { events: [], sequence };
    }
    if (triggeringEvent.hp_before <= 0 || triggeringEvent.hp_after !== 0) {
      return { events: [], sequence };
    }
    const events = [];
    const geometry = window.IRON_PIT_BROWSER_GRID_GEOMETRY;
    for (const member of [...(setup?.heroes || []), ...(setup?.monsters || [])]) {
      if (member.combatant_id === killer.combatant_id) continue;
      const rule = member.state?.template?.source_reduces_hostile_to_zero_hp_temporary_hp;
      if (!rule || !(rule.ally_zero_hp_range_ft > 0)) continue;
      if (target.combatant_id === member.combatant_id || target.side === member.side) continue;
      if (!member.state.position || !target.state.position || !geometry?.footprintDistanceFt) continue;
      const distance = geometry.footprintDistanceFt(
        member.state.position, member.state.template.size,
        target.state.position, target.state.template.size,
      );
      if (distance > rule.ally_zero_hp_range_ft) continue;
      const granted = grantZeroHpTemporaryHp(sequence, round, member, rule, true);
      events.push(granted.event);
      sequence = granted.sequence;
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_ZERO_HP_BLESSING = {
    grantZeroHpTemporaryHp,
    resolveWitnessedZeroHpTriggers,
  };
})();
