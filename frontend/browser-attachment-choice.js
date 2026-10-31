(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const R = () => window.IRON_PIT_BROWSER_ATTACHMENT_REMOVAL;

  function choose(actor, setup) {
    try {
      if (!E()?.available(actor.state, "action")) return null;
      const members = new Map([...setup.heroes, ...setup.monsters]
        .map((member) => [member.combatant_id, member]));
      const choices = [];
      for (const link of setup.attachments || []) {
        const source = members.get(link.source_id), target = members.get(link.target_id);
        if (!link.action_removable || !source || !target) continue;
        if (source.state.is_dead || !source.state.is_alive
          || target.state.is_dead || !target.state.is_alive) continue;
        if (target.side !== actor.side || source.side === actor.side) continue;
        if (actor.combatant_id !== link.target_id
          && S().distance(actor, source) > link.action_removal_range_ft) continue;
        const threat = link.damage_dice_count * (link.damage_dice_size + 1) / 2
          + link.damage_bonus;
        choices.push({ sourceId: link.source_id, effectId: link.effect_id,
          targetId: link.target_id, sourceName: link.source_name, threat });
      }
      choices.sort((a, b) => b.threat - a.threat ||
        a.sourceId.localeCompare(b.sourceId) || a.effectId.localeCompare(b.effectId));
      return choices[0] || null;
    } catch (error) {
      console.error("Attachment removal candidate selection failed", error);
      throw error;
    }
  }

  function resolve(sequence, round, member, setup, candidate) {
    try {
      if (!candidate) throw Error("Missing source-neutral attachment removal candidate.");
      const link = (setup.attachments || []).find((row) =>
        row.source_id === candidate.sourceId
        && row.effect_id === candidate.effectId
        && row.target_id === candidate.targetId);
      if (!link) throw Error("Attachment removal candidate is stale.");
      if (!R()?.removeByAction(setup, member, link.source_id, link.effect_id)) {
        throw Error("Selected attachment removal became illegal.");
      }
      const target = [...setup.heroes, ...setup.monsters]
        .find((row) => row.combatant_id === link.target_id);
      if (!target) throw Error("Attached target is absent.");
      return { sequence: sequence + 1, events: [{
        sequence, round_number: round, event_type: "feature",
        actor_id: member.combatant_id, actor_name: member.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        feature_id: link.source_name, animation: "feature",
        attachment_changes: [{
          operation: "detach", source_id: link.source_id, target_id: link.target_id,
          effect_id: link.effect_id, source_name: link.source_name,
        }],
        description: `${member.state.template.name} spends an Action to detach ${link.source_name} from ${target.state.template.name}.`,
      }] };
    } catch (error) {
      console.error("Generic attachment removal choice failed", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ATTACHMENT_CHOICE = { choose, resolve };
})();
