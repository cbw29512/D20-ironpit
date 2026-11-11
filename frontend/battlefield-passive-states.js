(() => {
  "use strict";

  function permanentPassiveStates(member, setup) {
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
      // A source-defined passive self-buff is present and enabled for the full
      // fight; unlike an activated buff, it consumes no Action or duration.
      // Names are display-only; activation is determined by the shared action
      // schema rather than a monster-specific name.
      for (const action of member.state.template.timed_self_buff_actions || []) {
        const timing = action.activation_timing || action.activationTiming;
        if (timing === "passive" && action.name) {
          passives.set(action.name, true);
        }
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
      // Card data, not trait-name guessing, determines harmful passive lane.
      // Environmental weaknesses stay grey when their context cannot occur.
      const sourceTraits = member.state.template.source_trait_names || [];
      const sourceWeaknesses = new Set(member.state.template.source_weakness_trait_names || []);
      for (const name of sourceWeaknesses) {
        if (!sourceTraits.includes(name)) throw new Error("Weakness display metadata must match printed source traits.");
      }
      const seen = new Set(result.map((item) => item.label || item.id));
      for (const name of member.state.template.source_trait_names || []) {
        if (!name || seen.has(name)) continue;
        result.push({
          id: name,
          label: name,
          lane: sourceWeaknesses.has(name) ? "debuff" : "buff",
          active: false,
          explanation: sourceWeaknesses.has(name)
            ? "Source-owned permanent weakness (arena trigger inactive)."
            : "Source-owned permanent trait (arena-neutral or inactive).",
        });
        seen.add(name);
      }
      return result;
    } catch (error) {
      console.error("Failed to project permanent passive card states", { combatantId: member?.combatant_id, error });
      throw error;
    }
  }


  window.IRON_PIT_BATTLEFIELD_PASSIVE_STATES = { permanentPassiveStates };
})();
