(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const T = () => window.IRON_PIT_BROWSER_TACTICAL_MIND;
  const TD = () => window.IRON_PIT_BROWSER_TIMED || { strengthD20Disadvantage: () => 0 };

  function sources(state) {
    state.restraint_sources ||= [];
    return state.restraint_sources;
  }

  function sync(state) {
    const active = sources(state).length > 0;
    const grappled = (state.grapple_sources || []).some((source) => source.restrains);
    const timed = (state.timed_effects || []).some((effect) => effect.effect_id === "restrained");
    if (active && !state.active_effect_ids.includes("restrained")) state.active_effect_ids.push("restrained");
    if (!active && !grappled && !timed) state.active_effect_ids = state.active_effect_ids.filter((id) => id !== "restrained");
  }

  function apply(state, sourceId, attack) {
    const profile = attack.breakableRestraint;
    if (!profile || I().immune(state, profile.conditionId || "restrained")) return [];
    sources(state);
    state.restraint_sources = state.restraint_sources.filter((item) => !(item.source_id === sourceId && item.source_effect_id === attack.id));
    state.restraint_sources.push({
      source_id: sourceId, source_effect_id: attack.id, condition_id: profile.conditionId || "restrained",
      escape_ability: profile.escapeAbility, escape_dc: profile.escapeDc,
      object_ac: profile.objectAc, current_hp: profile.objectHp, max_hp: profile.objectHp,
      damage_vulnerabilities: profile.damageVulnerabilities || [], damage_immunities: profile.damageImmunities || [],
    });
    sync(state);
    return [profile.conditionId || "restrained"];
  }

  function release(state, source) {
    state.restraint_sources = sources(state).filter((item) => item !== source);
    sync(state);
  }

  const shouldEscape = (state) => E().available(state, "action") && sources(state).length > 0;

  function escape(sequence, round, member) {
    const state = member.state, source = sources(state)[0];
    if (!source || !E().available(state, "action")) throw new Error("Action is unavailable to escape restraint.");
    const ability = source.escape_ability, bonus = state.template.ability_modifiers?.[ability];
    if (bonus == null) throw new Error(`${state.template.name} lacks ${ability} modifier for restraint escape.`);
    const advantage = ability === "strength" && state.active_effect_ids.includes("rage") ? 1 : 0;
    const disadvantage = (state.active_effect_ids.includes("poisoned") || state.active_effect_ids.includes("frightened") ? 1 : 0)
      + (ability === "strength" ? TD().strengthD20Disadvantage(state) : 0);
    let roll = R().d20(bonus, R().modeFromSources(advantage, disadvantage));
    let success = roll.total >= source.escape_dc, tactical = null;
    if (!success && T()) {
      tactical = T().apply(state, roll, source.escape_dc); roll = tactical.roll; success = tactical.succeeded;
    }
    E().spend(state, "action");
    if (success) release(state, source);
    return {
      sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
      actor_name: state.template.name, target_id: source.source_id, ability_check_roll: roll,
      check_ability: ability, check_dc: source.escape_dc, check_succeeded: success,
      feature_id: "escape-restraint", resource_remaining: tactical?.used ? tactical.resource_remaining : null,
      animation: "escape-restraint",
      description: `${state.template.name} ${success ? "escapes" : "fails to escape"} ${source.source_effect_id}${tactical?.used ? " after using Tactical Mind" : ""} with a ${ability} check against DC ${source.escape_dc}.`,
    };
  }

  function installTurnControl() {
    const grapple = window.IRON_PIT_BROWSER_GRAPPLE;
    if (!grapple || grapple.breakableRestraintWrapped) return;
    const baseShould = grapple.shouldEscape.bind(grapple), baseEscape = grapple.escape.bind(grapple);
    grapple.shouldEscape = (state) => shouldEscape(state) || baseShould(state);
    grapple.escape = (sequence, round, member) => shouldEscape(member.state) ? escape(sequence, round, member) : baseEscape(sequence, round, member);
    grapple.breakableRestraintWrapped = true;
  }

  window.IRON_PIT_BROWSER_RESTRAINTS = { apply, escape, release, shouldEscape, sync };
  installTurnControl();
})();
