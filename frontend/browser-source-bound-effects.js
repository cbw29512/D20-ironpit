(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const C = () => window.IRON_PIT_BROWSER_CONDITION_RULES
    || { incapacitated: (state) => state.is_unconscious };
  const L = () => window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE;

  function endDamageSensitive(state) {
    const removed = [], handled = new Set();
    for (const effect of [...state.timed_effects]) {
      const key = `${effect.source_id}|${effect.source_effect_id || ""}`;
      if (!effect.ends_on_damage || handled.has(key)) continue;
      handled.add(key); removed.push(...T().removeGroup(state, effect));
    }
    return removed;
  }

  function resolveDamageRepeatSaves(sequence, round, damageSource, target, setup) {
    if (target.state.is_dead || !target.state.is_alive) return { events: [], sequence };
    if (!L()?.repeatSave) throw new Error("Damage repeat saves require condition lifecycle.");
    const events = [], handled = new Set();
    for (const effect of [...(target.state.timed_effects || [])]) {
      const key = `${effect.source_id}|${effect.source_effect_id || ""}`;
      if (handled.has(key) || (effect.damage_repeat_save_trigger || "none") === "none") continue;
      handled.add(key);
      if (effect.damage_repeat_save_trigger === "other_than_effect_source"
        && damageSource.combatant_id === effect.source_id) continue;
      const save = L().repeatSave(target, effect, round, setup);
      const removed = save.succeeded ? T().removeGroup(target.state, effect) : [];
      if (!save.succeeded) effect.repeat_save_failure_count = (effect.repeat_save_failure_count || 0) + 1;
      events.push({
        sequence: sequence++, round_number: round, event_type: "saving_throw",
        actor_id: target.combatant_id, actor_name: target.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        saving_throw_roll: save.roll, save_ability: effect.repeat_save_ability,
        save_dc: effect.repeat_save_dc, save_succeeded: save.succeeded,
        removed_condition_ids: removed,
        feature_id: effect.source_effect_id || "condition-damage-repeat-save",
        animation: "condition-save",
        description: `${target.state.template.name} repeats the ${effect.repeat_save_ability} save after damage from ${damageSource.state.template.name}: ${save.succeeded ? "SUCCESS" : "FAILURE"}.`
          + (save.buffs.length ? ` Save Advantage: ${save.buffs.join(", ")}.` : ""),
      });
    }
    return { events, sequence };
  }

  function cleanupDisabledSources(setup) {
    const members = [...setup.heroes, ...setup.monsters];
    const byId = new Map(members.map((member) => [member.combatant_id, member]));
    for (const target of members) {
      const handled = new Set();
      for (const effect of [...target.state.timed_effects]) {
        const key = `${effect.source_id}|${effect.source_effect_id || ""}`;
        if (handled.has(key)) continue;
        const source = byId.get(effect.source_id); if (!source) continue;
        const dead = source.state.is_dead || !source.state.is_alive || source.state.current_hp <= 0;
        const incapacitated = C().incapacitated(source.state);
        if ((effect.ends_if_source_dead && dead) || (effect.ends_if_source_incapacitated && incapacitated)) {
          handled.add(key); T().removeGroup(target.state, effect);
        }
      }
    }
  }

  window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS = {
    cleanupDisabledSources, endDamageSensitive, resolveDamageRepeatSaves,
  };
})();
