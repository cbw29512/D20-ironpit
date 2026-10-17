(() => {
  "use strict";

  function passiveStates(member, setup) {
    try {
      const result = [];
      // The source owns printed passive labels, while the combat modifier stack owns activation.
      // Applies to both editions without dispatching by class or monster name.
      const passives = new Map();
      for (const grant of member.state.template.passive_modifier_grants || []) {
        if (!grant.source_name) continue;
        const available = grant.required_visible_active_ally_within_ft == null
          || Boolean(window.IRON_PIT_BROWSER_STATE?.hasVisibleActiveAllyWithin?.(
            member, setup, grant.required_visible_active_ally_within_ft));
        const enabled = available && (member.state.active_modifiers || []).some((modifier) =>
          modifier.source_effect_id === grant.source_id && modifier.kind === grant.kind
          && (modifier.required_active_effect_ids || []).every((id) => (member.state.active_effect_ids || []).includes(id)));
        passives.set(grant.source_name, enabled || Boolean(passives.get(grant.source_name)));
      }
      for (const [id, enabled] of passives) {
        if (!result.some((item) => item.id === id)) {
          result.push({ id, active: enabled, explanation: "Source-owned permanent combat modifier." });
        }
      }
      // Environmental weaknesses are permanent card traits, not transient
      // timed conditions. Their activation is a live context predicate.
      for (const reaction of member.state.template.environment_context_reactions || []) {
        // Display every declared permanent context reaction, including future
        // rules that apply damage or other effects without a d20 roll.
        const lane = reaction.status_lane || reaction.statusLane || "debuff";
        if (lane !== "buff" && lane !== "debuff") throw new Error("Unknown permanent passive status lane.");
        const contextId = reaction.context_id || reaction.contextId;
        if (!contextId) throw new Error("Permanent passive requires a typed environment context.");
        const runtime = window.IRON_PIT_BROWSER_ENVIRONMENT_CONTEXTS;
        if (!runtime?.inside) throw new Error("Permanent environment debuff requires context runtime.");
        result.push({
          id: reaction.source_id,
          label: reaction.source_name,
          lane,
          active: runtime.inside(member, setup, contextId),
          explanation: "Source-owned permanent environmental weakness.",
        });
      }
      // Every printed source trait appears as a permanent buff for completeness,
      // even when arena-neutral. Active only if already projected above.
      const seen = new Set(result.map((item) => item.label || item.id));
      for (const name of member.state.template.source_trait_names || []) {
        if (!name || seen.has(name)) continue;
        result.push({
          id: name,
          label: name,
          lane: "buff",
          active: false,
          explanation: "Source-owned permanent trait (arena-neutral or inactive).",
        });
        seen.add(name);
      }
      return result;
    } catch (error) {
      console.error("Failed to project permanent passive card states", { combatantId: member?.combatant_id, error });
      throw error;
    }
  }


  window.IRON_PIT_BATTLEFIELD_PASSIVE_STATES = { permanent passiveStates };
})();
