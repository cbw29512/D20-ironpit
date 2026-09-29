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
          if (grant.usage_resource_id) {
            if (!Object.prototype.hasOwnProperty.call(resources, grant.usage_resource_id)
                || !Number.isFinite(resources[grant.usage_resource_id])
                || !Number.isFinite(maxima[grant.usage_resource_id])) {
              throw new Error(`${grant.source_name} references missing resource ${grant.usage_resource_id}.`);
            }
          }
          if (resources[grant.resource_id] > grant.when_at_or_below) continue;
          const usageCost = grant.usage_resource_cost || 1;
          if (grant.usage_resource_id && resources[grant.usage_resource_id] < usageCost) continue;
          const before = resources[grant.resource_id];
          const after = Number.isFinite(grant.restore_to_minimum)
            ? Math.min(maxima[grant.resource_id], Math.max(before, grant.restore_to_minimum))
            : (grant.restore_to_max
              ? maxima[grant.resource_id]
              : Math.min(maxima[grant.resource_id], before + grant.restore_amount));
          if (after <= before) continue;
          if (grant.usage_resource_id) resources[grant.usage_resource_id] -= usageCost;
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
