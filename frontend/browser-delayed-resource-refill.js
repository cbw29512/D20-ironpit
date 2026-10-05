(() => {
  "use strict";

  function ruleOf(member) {
    return member.state.template.delayed_resource_refill || null;
  }

  function committedActive(state) {
    return Boolean((state.delayed_resource_refills || []).length);
  }

  function activeTimer(member, rule) {
    return (member.state.delayed_resource_refills || []).find((item) => item.source_id === rule.source_id) || null;
  }

  function unableToPerform(member) {
    const state = member.state;
    if (state.is_dead) return true;
    const rules = window.IRON_PIT_BROWSER_CONDITION_RULES;
    return Boolean(rules ? rules.incapacitated(state) : state.is_unconscious);
  }

  function restoreResources(member, rule) {
    const restored = [];
    for (const resourceId of rule.resource_ids || []) {
      const maxUses = member.state.template.resources?.[resourceId];
      if (maxUses == null) throw new Error(rule.source_name + " references missing resource " + resourceId + ".");
      const current = member.state.resources?.[resourceId] || 0;
      if (current >= maxUses) continue;
      if (rule.restore_mode === "half_max_rounded_up") {
        const regain = Math.floor((maxUses + 1) / 2);
        member.state.resources[resourceId] = Math.min(maxUses, current + regain);
      } else {
        member.state.resources[resourceId] = maxUses;
      }
      restored.push(resourceId);
    }
    return restored;
  }

  function canStart(member) {
    const rule = ruleOf(member);
    if (!rule || activeTimer(member, rule)) return false;
    const economy = window.IRON_PIT_ACTION_ECONOMY;
    if (!economy || !economy.available(member.state, "action")) return false;
    const cost = rule.use_resource_cost || 1;
    if ((member.state.resources?.[rule.use_resource_id] || 0) < cost) return false;
    return (rule.resource_ids || []).some((resourceId) => {
      const maxUses = member.state.template.resources?.[resourceId];
      if (maxUses == null) throw new Error(rule.source_name + " references missing resource " + resourceId + ".");
      return (member.state.resources?.[resourceId] || 0) < maxUses;
    });
  }

  function start(ctx) {
    const rule = ruleOf(ctx.member);
    if (!rule || !canStart(ctx.member)) throw new Error((rule && rule.source_name) || "Committed activity" + " cannot begin.");
    const cost = rule.use_resource_cost || 1;
    ctx.member.state.resources[rule.use_resource_id] -= cost;
    window.IRON_PIT_ACTION_ECONOMY.spend(ctx.member.state, "action");
    ctx.member.state.movement_remaining_ft = 0;
    ctx.member.state.delayed_resource_refills = ctx.member.state.delayed_resource_refills || [];
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
        resource_remaining: ctx.member.state.resources[rule.use_resource_id],
        animation: "resource-refill",
        description: ctx.member.state.template.name + " begins " + rule.source_name
          + " and spends the next " + rule.delay_rounds + " rounds performing it.",
      }],
      sequence: ctx.sequence + 1,
      claimed: true,
    };
  }

  function resolve(ctx) {
    const rule = ruleOf(ctx.member);
    if (!rule) return { events: [], sequence: ctx.sequence, claimed: false };
    const timers = ctx.member.state.delayed_resource_refills || [];
    const timer = activeTimer(ctx.member, rule);
    if (!timer) return { events: [], sequence: ctx.sequence, claimed: false };
    const name = ctx.member.state.template.name;
    if (unableToPerform(ctx.member)) {
      ctx.member.state.delayed_resource_refills = timers.filter((item) => item !== timer);
      return {
        events: [{
          sequence: ctx.sequence,
          round_number: ctx.round,
          event_type: "feature",
          actor_id: ctx.member.combatant_id,
          actor_name: name,
          target_id: ctx.member.combatant_id,
          target_name: name,
          feature_id: rule.source_id,
          animation: "resource-refill",
          description: name + " stops " + rule.source_name + " before it completes and restores no resources.",
        }],
        sequence: ctx.sequence + 1,
        claimed: false,
      };
    }
    if (ctx.round < timer.completes_round) return { events: [], sequence: ctx.sequence, claimed: false };
    const restored = restoreResources(ctx.member, rule);
    ctx.member.state.delayed_resource_refills = timers.filter((item) => item !== timer);
    return {
      events: [{
        sequence: ctx.sequence,
        round_number: ctx.round,
        event_type: "feature",
        actor_id: ctx.member.combatant_id,
        actor_name: name,
        target_id: ctx.member.combatant_id,
        target_name: name,
        feature_id: rule.source_id,
        animation: "resource-refill",
        description: name + " completes " + rule.source_name
          + " and restores " + (restored.length ? restored.join(", ") : "no depleted resources") + ".",
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

  window.IRON_PIT_BROWSER_DELAYED_RESOURCE_REFILL = {
    canStart, committedActive, installAbilityHooks, resolve, start,
  };
})();
