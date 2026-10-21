(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function groups(source, setup, dueOnly) {
    const result = new Map();
    for (const target of [...setup.heroes, ...setup.monsters]) {
      for (const effect of target.state.timed_effects || []) {
        if (effect.source_id !== source.combatant_id
          || !effect.source_effect_id
          || (effect.source_maintenance_action_cost || "none") === "none") continue;
        if (dueOnly && ((effect.source_turn_count_at_application ?? Infinity)
          >= (source.state.turns_started || 0))) continue;
        const entries = result.get(effect.source_effect_id) || [];
        entries.push({ target, effect });
        result.set(effect.source_effect_id, entries);
      }
    }
    return result;
  }

  function selectGroup(source, grouped) {
    const ranked = [...grouped.entries()].map(([effectId, entries]) => ({
      effectId, entries,
      opponents: new Set(entries.filter(({ target }) => target.side !== source.side)
        .map(({ target }) => target.combatant_id)).size,
      targets: new Set(entries.map(({ target }) => target.combatant_id)).size,
    }));
    ranked.sort((a, b) => b.opponents - a.opponents
      || b.targets - a.targets || a.effectId.localeCompare(b.effectId));
    return ranked[0]?.effectId || null;
  }

  function endGroup(sequence, round, source, entries) {
    const events = [], handled = new Set();
    for (const { target, effect } of entries) {
      if (handled.has(target.combatant_id)) continue;
      handled.add(target.combatant_id);
      const removed = T().removeGroup(target.state, effect, { grantSourceImmunity: false });
      if (!removed.length) continue;
      events.push({
        sequence: sequence++, round_number: round, event_type: "feature",
        actor_id: source.combatant_id, actor_name: source.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        removed_condition_ids: removed, feature_id: effect.source_effect_id,
        animation: "condition-ended",
        description: `${source.state.template.name} does not continue ${effect.source_effect_id}; its effects on ${target.state.template.name} end.`,
      });
    }
    return { events, sequence };
  }

  function stop(sequence, round, source, setup) {
    try {
      const events = [];
      for (const entries of groups(source, setup, false).values()) {
        const ended = endGroup(sequence, round, source, entries);
        events.push(...ended.events); sequence = ended.sequence;
      }
      return { events, sequence };
    } catch (error) {
      console.error("Browser source-maintained effect stop failed", {
        source: source?.combatant_id, error,
      });
      throw error;
    }
  }

  function resolve(sequence, round, source, setup) {
    try {
      if (!E()?.available || !E()?.spend || !T()?.removeGroup) {
        throw new Error("Source maintenance requires action economy and timed conditions.");
      }
      const grouped = groups(source, setup, true);
      const selected = selectGroup(source, grouped);
      const selectedEntries = selected ? grouped.get(selected) : null;
      const cost = selectedEntries?.[0]?.effect.source_maintenance_action_cost;
      const canContinue = Boolean(selected && E().available(source.state, cost));
      const events = [];
      for (const [effectId, entries] of grouped) {
        if (effectId !== selected || !canContinue) {
          const ended = endGroup(sequence, round, source, entries);
          events.push(...ended.events); sequence = ended.sequence;
          continue;
        }
        E().spend(source.state, cost);
        for (const { effect } of entries) {
          effect.source_turn_count_at_application = source.state.turns_started || 0;
        }
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: source.combatant_id, actor_name: source.state.template.name,
          feature_id: effectId, animation: "feature",
          description: `${source.state.template.name} continues ${effectId} with its ${cost.replace("_", " ")}.`,
        });
      }
      return { events, sequence, claimed: canContinue };
    } catch (error) {
      console.error("Browser source-maintenance resolution failed", {
        source: source?.combatant_id, error,
      });
      throw error;
    }
  }

  function installHook() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) {
      window.IRON_PIT_PENDING_ABILITY_HOOK_INSTALLERS ||= [];
      window.IRON_PIT_PENDING_ABILITY_HOOK_INSTALLERS.push(installHook);
      return;
    }
    const phase = hooks.PHASES.BONUS_ACTION_WINDOW;
    if (hooks.abilitiesFor(phase).some((item) => item.id === "source-maintenance")) return;
    hooks.registerAbility(phase, {
      id: "source-maintenance", priority: 1, rulesets: ["2014", "2024"],
      appliesTo: (_member, ctx) => ctx.bonusActionCheckpoint === "sourceMaintenance",
      resolve: ({ sequence, round, member, setup }) => {
        const result = resolve(sequence, round, member, setup);
        return result.events.length ? result : null;
      },
    });
  }

  window.IRON_PIT_BROWSER_SOURCE_MAINTENANCE = { resolve, stop };
  installHook();
})();
