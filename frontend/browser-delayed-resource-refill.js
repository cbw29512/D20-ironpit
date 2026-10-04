(() => {
  "use strict";

  function resolve(ctx) {
    const rule = ctx.member.state.template.delayed_resource_refill;
    if (!rule) return { events: [], sequence: ctx.sequence, claimed: false };

    const timers = ctx.member.state.delayed_resource_refills || [];
    const timer = timers.find((item) => item.source_id === rule.source_id) || null;

    if (timer) {
      if (ctx.round < timer.completes_round) return { events: [], sequence: ctx.sequence, claimed: false };
      const restored = [];
      for (const resourceId of rule.resource_ids || []) {
        const maxUses = ctx.member.state.template.resources?.[resourceId];
        if (maxUses == null) throw new Error(rule.source_name + " references missing resource " + resourceId + ".");
        const current = ctx.member.state.resources?.[resourceId] || 0;
        if (current < maxUses) {
          if (rule.restore_mode === "half_max_rounded_up") {
            const regain = Math.floor((maxUses + 1) / 2);
            ctx.member.state.resources[resourceId] = Math.min(maxUses, current + regain);
          } else {
            ctx.member.state.resources[resourceId] = maxUses;
          }
          restored.push(resourceId);
        }
      }
      ctx.member.state.delayed_resource_refills = timers.filter((item) => item !== timer);
      return {
        events: [{
          sequence: ctx.sequence,
          round_number: ctx.round,
          event_type: "feature",
          actor_id: ctx.member.combatant_id,
          actor_name: ctx.member.state.template.name,
          target_id: ctx.member.combatant_id,
          target_name: ctx.member.state.template.name,
          feature_id: rule.source_id,
          animation: "resource-refill",
          description: ctx.member.state.template.name + " completes " + rule.source_name
            + " and restores " + (restored.length ? restored.join(", ") : "no depleted resources") + ".",
        }],
        sequence: ctx.sequence + 1,
        claimed: false,
      };
    }

    const useId = rule.use_resource_id;
    const cost = rule.use_resource_cost || 1;
    if ((ctx.member.state.resources?.[useId] || 0) < cost) {
      return { events: [], sequence: ctx.sequence, claimed: false };
    }

    const depleted = (rule.resource_ids || []).filter((resourceId) => {
      const maxUses = ctx.member.state.template.resources?.[resourceId];
      if (maxUses == null) throw new Error(rule.source_name + " references missing resource " + resourceId + ".");
      return (ctx.member.state.resources?.[resourceId] || 0) < maxUses;
    });
    if (!depleted.length) return { events: [], sequence: ctx.sequence, claimed: false };

    ctx.member.state.resources[useId] -= cost;
    ctx.member.state.delayed_resource_refills.push({
      source_id: rule.source_id,
      started_round: ctx.round,
      completes_round: ctx.round + rule.delay_rounds,
    });
    return {
      events: [{
        sequence: ctx.sequence,
        round_number: ctx.round,
        event_type: "feature",
        actor_id: ctx.member.combatant_id,
        actor_name: ctx.member.state.template.name,
        target_id: ctx.member.combatant_id,
        target_name: ctx.member.state.template.name,
        feature_id: rule.source_id,
        resource_remaining: ctx.member.state.resources[useId],
        animation: "resource-refill",
        description: ctx.member.state.template.name + " begins " + rule.source_name
          + "; the refill completes after " + rule.delay_rounds + " rounds.",
      }],
      sequence: ctx.sequence + 1,
      claimed: false,
    };
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Delayed resource refill requires browser-ability-hooks.js.");
    const phase = hooks.PHASES.TURN_END_LIFECYCLE;
    if (hooks.abilitiesFor(phase).some((item) => item.id === "delayed-resource-refill")) return;
    hooks.registerAbility(phase, {
      id: "delayed-resource-refill",
      priority: 90,
      rulesets: ["2014", "2024"],
      appliesTo: (member) => Boolean(member.state.template.delayed_resource_refill),
      resolve,
    });
  }

  window.IRON_PIT_BROWSER_DELAYED_RESOURCE_REFILL = { installAbilityHooks, resolve };
})();