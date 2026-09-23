(() => {
  "use strict";

  function resolve(sequence, setup) {
    try {
      const events = [];
      for (const member of [...setup.heroes, ...setup.monsters]) {
        for (const grant of member.state.template.initiative_resource_refill_grants || []) {
          const resources = member.state.resources || {};
          const maxima = member.state.template.resources || {};
          if (!Object.prototype.hasOwnProperty.call(resources, grant.resource_id)
              || !Number.isFinite(resources[grant.resource_id])
              || !Number.isFinite(maxima[grant.resource_id])) {
            throw new Error(`${grant.source_name} references missing resource ${grant.resource_id}.`);
          }
          if (resources[grant.resource_id] > grant.when_at_or_below) continue;
          const before = resources[grant.resource_id];
          const after = Math.min(maxima[grant.resource_id], before + grant.restore_amount);
          if (after <= before) continue;
          resources[grant.resource_id] = after;
          events.push({
            sequence: sequence++, round_number: 0, event_type: "feature",
            actor_id: member.combatant_id, actor_name: member.state.template.name,
            feature_id: grant.source_id, resource_remaining: after, animation: "initiative",
            description: `${member.state.template.name} regains ${after - before} ${grant.resource_id} from ${grant.source_name}.`,
          });
        }
      }
      return { events, sequence };
    } catch (error) {
      console.error("Browser initiative resource refill failed.", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_INITIATIVE_RESOURCE_REFILL = { resolve };
})();
