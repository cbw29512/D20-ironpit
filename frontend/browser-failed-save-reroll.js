(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const A = () => window.IRON_PIT_ACTION_ECONOMY || {
    available: (state, cost) => cost !== "reaction" || state.reaction_available,
    spend: (state, cost) => { if (cost === "reaction") state.reaction_available = false; },
  };

  function d20Count(mode) {
    return mode === "normal" ? 1 : 2;
  }

  function effectTags(context = {}) {
    const tags = new Set((context.effectTags || []).map((item) => String(item).trim().toLowerCase()).filter(Boolean));
    if (context.conditionId) tags.add(String(context.conditionId).trim().toLowerCase());
    return tags;
  }

  function replacementMode(grant, original) {
    if (grant.reroll_mode === "advantage") return "advantage";
    if (grant.reroll_mode === "disadvantage") return "disadvantage";
    return original.mode || "normal";
  }

  function candidates(state, context = {}) {
    const roller = context.encounterRoller || null, setup = context.setup || null;
    const values = [{ state, member: null }];
    if (!roller || !setup) return values;
    const allies = roller.side === "heroes" ? setup.heroes : setup.monsters;
    for (const member of [...allies].sort((a, b) => a.combatant_id.localeCompare(b.combatant_id))) {
      if (member.combatant_id !== roller.combatant_id) values.push({ state: member.state, member });
    }
    return values;
  }

  function apply(state, original, context = {}) {
    try {
      const tags = effectTags(context);
      for (const source of candidates(state, context)) {
        for (const grant of source.state.template.failed_save_reroll_grants || []) {
          if (source.member && grant.target_mode !== "self_or_ally") continue;
          if (source.member) {
            if (!context.encounterRoller || !context.setup) continue;
            if (window.IRON_PIT_BROWSER_STATE.distance(source.member, context.encounterRoller) > (grant.range_ft || 0)) continue;
          }
          const required = (grant.required_effect_tags || []).map((item) => String(item).trim().toLowerCase());
          if (required.length && !required.some((item) => tags.has(item))) continue;
          if (grant.action_cost && !A().available(source.state, grant.action_cost)) continue;

          const resourceId = grant.resource_id || null;
          const cost = grant.resource_cost || 1;
          if (resourceId != null) {
            const available = source.state.resources?.[resourceId];
            if (available == null) {
              throw new Error(`Failed-save reroll ${grant.source_id} references missing resource ${resourceId}.`);
            }
            if (available < cost) continue;
          }

          const count = d20Count(original.mode);
          const retained = (original.rolls || []).slice(count);
          const replacementBase = R().d20(original.modifier || 0, replacementMode(grant, original));
          const replacementRolls = [...replacementBase.rolls, ...retained];
          const replacementTotal = replacementBase.total + retained.reduce((sum, value) => sum + value, 0);
          const revision = {
            source_effect_id: grant.source_id,
            kind: "full_reroll",
            original_rolls: [...(original.rolls || [])],
            replacement_rolls: replacementRolls,
            original_modifier: original.modifier || 0,
            replacement_modifier: original.modifier || 0,
            original_selected: original.selected_roll,
            replacement_selected: replacementBase.selected_roll,
            original_total: original.total,
            replacement_total: replacementTotal,
            accepted: "replacement",
            replaced_die_index: null,
          };
          if (grant.action_cost) A().spend(source.state, grant.action_cost);
          if (resourceId != null) source.state.resources[resourceId] -= cost;
          return {
            roll: {
              ...original,
              notation: `${original.notation} [${grant.source_name}]`,
              rolls: replacementRolls,
              selected_roll: replacementBase.selected_roll,
              total: replacementTotal,
              revisions: [...(original.revisions || []), revision],
            },
            featureId: grant.source_id,
            sourceName: grant.source_name,
          };
        }
      }
      return { roll: original, featureId: null, sourceName: null };
    } catch (error) {
      console.error("Failed browser failed-save reroll", { error, combatant: state?.template?.name });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_FAILED_SAVE_REROLL = { apply };
})();
