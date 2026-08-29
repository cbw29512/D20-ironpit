(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { speedZero: (state) => state.active_effect_ids.includes("restrained") };

  function sync(state) {
    const grappled = state.grapple_sources.length > 0;
    const restrained = state.grapple_sources.some((source) => source.restrains);
    state.active_effect_ids = state.active_effect_ids.filter((id) => id !== "grappled" && id !== "restrained");
    if (grappled) {
      state.active_effect_ids.push("grappled");
      state.active_effect_ids = state.active_effect_ids.filter((id) => id !== "dodge");
    }
    if (restrained) state.active_effect_ids.push("restrained");
  }

  function apply(state, sourceId, escapeDc, rangeFt, restrains = false) {
    if (I().immune(state, "grappled")) return [];
    state.grapple_sources = state.grapple_sources.filter((source) => source.source_id !== sourceId);
    const effectiveRestrains = restrains && !I().immune(state, "restrained");
    state.grapple_sources.push({ source_id: sourceId, escape_dc: escapeDc, range_ft: rangeFt, restrains: effectiveRestrains });
    sync(state);
    return effectiveRestrains ? ["grappled", "restrained"] : ["grappled"];
  }

  function release(state, sourceId) {
    state.grapple_sources = state.grapple_sources.filter((source) => source.source_id !== sourceId);
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
      target.state.grapple_sources = target.state.grapple_sources.filter((source) => {
        const grappler = members.get(source.source_id);
        if (!grappler || grappler.state.is_dead || grappler.state.is_unconscious) return false;
        return Math.abs(grappler.position_ft - target.position_ft) <= source.range_ft;
      });
      sync(target.state);
    }
  }

  const shouldEscape = (state) => state.action_available && state.grapple_sources.some((source) => source.restrains);

  function escape(sequence, round, member) {
    const state = member.state;
    const source = state.grapple_sources.find((item) => item.restrains) || state.grapple_sources[0];
    const athletics = state.template.skill_bonuses?.athletics;
    const acrobatics = state.template.skill_bonuses?.acrobatics;
    if (athletics == null && acrobatics == null) throw new Error(`${state.template.name} lacks certified grapple escape bonuses.`);
    const useAthletics = athletics != null && (acrobatics == null || athletics >= acrobatics);
    const bonus = useAthletics ? athletics : acrobatics;
    const advantage = useAthletics && state.active_effect_ids.includes("rage") ? 1 : 0;
    const disadvantage = state.active_effect_ids.includes("poisoned") ? 1 : 0;
    const roll = R().d20(bonus, R().modeFromSources(advantage, disadvantage));
    const success = roll.total >= source.escape_dc;
    state.action_available = false;
    if (success) {
      release(state, source.source_id);
      if (!speedIsZero(state)) state.movement_remaining_ft = Math.max(state.movement_remaining_ft, state.template.speed_ft);
    }
    const check = useAthletics ? "strength (athletics)" : "dexterity (acrobatics)";
    return {
      sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
      actor_name: state.template.name, target_id: source.source_id, ability_check_roll: roll,
      check_ability: check, check_dc: source.escape_dc, check_succeeded: success,
      feature_id: "escape-grapple", animation: "escape-grapple",
      description: `${state.template.name} ${success ? "escapes" : "fails to escape"} the grapple with ${check} against DC ${source.escape_dc}.`,
    };
  }

  window.IRON_PIT_BROWSER_GRAPPLE = { apply, attackDisadvantage, cleanup, escape, release, shouldEscape, speedIsZero };
})();
