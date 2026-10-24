(() => {
  "use strict";

  const SELF_BUFFS = new Set(["rage", "dodge"]);
  const DEBUFF_MODIFIERS = new Set(["attacks-against-advantage"]);

  function modifierIsDebuff(modifier) {
    try {
      return DEBUFF_MODIFIERS.has(modifier.kind) || Number(modifier.flat_bonus || 0) < 0;
    } catch (error) {
      console.error("Failed to classify combat modifier status lane", { modifier, error });
      throw error;
    }
  }

  function timedEffectLane(effect) {
    try {
      const lane = effect?.status_lane || effect?.statusLane || "debuff";
      if (lane !== "buff" && lane !== "debuff") throw new Error("Unknown timed-effect status lane.");
      return lane;
    } catch (error) {
      console.error("Failed to classify timed-effect status lane", { effect, error });
      throw error;
    }
  }

  function classifyStatusLanes(state) {
    try {
      const buffs = new Set(state.active_buff_effect_ids || []);
      const debuffs = new Set();
      const timed = new Map(
        (state.timed_effects || []).map((effect) => [effect.effect_id, timedEffectLane(effect)]),
      );
      for (const id of state.active_effect_ids || []) {
        const lane = timed.get(id) || (SELF_BUFFS.has(id) ? "buff" : "debuff");
        (lane === "buff" ? buffs : debuffs).add(id);
      }
      for (const effect of state.timed_effects || []) {
        (timedEffectLane(effect) === "buff" ? buffs : debuffs).add(effect.effect_id);
      }
      const permanentIds = new Set(
        (state.template?.passive_modifier_grants || []).map((grant) => grant.source_id),
      );
      for (const modifier of state.active_modifiers || []) {
        const id = modifier.source_effect_id;
        if (!id || permanentIds.has(id)) continue;
        (modifierIsDebuff(modifier) ? debuffs : buffs).add(id);
      }
      if (state.concentration?.effect_id) buffs.delete(state.concentration.effect_id);
      for (const id of debuffs) buffs.delete(id);
      return { buffs: [...buffs].sort(), debuffs: [...debuffs].sort() };
    } catch (error) {
      console.error("Failed to classify battlefield status lanes", { state, error });
      throw error;
    }
  }

  function passiveActionState(member, action) {
    try {
      let active = member.state.is_alive !== false && !member.state.is_dead;
      const aura = action.hostileStartTurnConditionAura || action.hostile_start_turn_condition_aura;
      const gated = aura?.inactive_while_source_incapacitated
        || aura?.inactiveWhileSourceIncapacitated;
      if (active && gated) {
        const rules = window.IRON_PIT_BROWSER_CONDITION_RULES;
        if (!rules?.incapacitated) throw new Error("Passive aura status requires condition-rules runtime.");
        active = !rules.incapacitated(member.state);
      }
      return {
        id: action.id,
        label: action.name,
        lane: "buff",
        active,
        explanation: "Source-owned permanent passive combat effect.",
      };
    } catch (error) {
      console.error("Failed to project passive combat action state", {
        combatantId: member?.combatant_id, actionId: action?.id, error,
      });
      throw error;
    }
  }

  function permanentPassiveStates(member, setup) {
    try {
      const result = [];
      const passives = new Map();
      for (const grant of member.state.template.passive_modifier_grants || []) {
        if (!grant.source_name) continue;
        const available = grant.required_visible_active_ally_within_ft == null
          || Boolean(window.IRON_PIT_BROWSER_STATE?.hasVisibleActiveAllyWithin?.(
            member, setup, grant.required_visible_active_ally_within_ft));
        const enabled = available && (member.state.active_modifiers || []).some((modifier) =>
          modifier.source_effect_id === grant.source_id && modifier.kind === grant.kind
          && (modifier.required_active_effect_ids || []).every(
            (id) => (member.state.active_effect_ids || []).includes(id)));
        passives.set(grant.source_name, enabled || Boolean(passives.get(grant.source_name)));
      }
      for (const [id, enabled] of passives) {
        if (!result.some((item) => item.id === id)) {
          result.push({ id, active: enabled, explanation: "Source-owned permanent combat modifier." });
        }
      }
      for (const reaction of member.state.template.environment_context_reactions || []) {
        const lane = reaction.status_lane || reaction.statusLane || "debuff";
        if (lane !== "buff" && lane !== "debuff") throw new Error("Unknown permanent passive status lane.");
        const contextId = reaction.context_id || reaction.contextId;
        if (!contextId) throw new Error("Permanent passive requires a typed environment context.");
        const runtime = window.IRON_PIT_BROWSER_ENVIRONMENT_CONTEXTS;
        if (!runtime?.inside) throw new Error("Permanent environment debuff requires context runtime.");
        result.push({
          id: reaction.source_id, label: reaction.source_name, lane,
          active: runtime.inside(member, setup, contextId),
          explanation: "Source-owned permanent environmental weakness.",
        });
      }
      for (const action of member.state.template.timed_self_buff_actions || []) {
        const timing = action.activationTiming || action.activation_timing || "action";
        if (timing !== "passive" || !action.id || !action.name) continue;
        if (!result.some((item) => (item.label || item.id) === action.name)) {
          result.push(passiveActionState(member, action));
        }
      }
      const seen = new Set(result.map((item) => item.label || item.id));
      for (const name of member.state.template.source_trait_names || []) {
        if (!name || seen.has(name)) continue;
        result.push({
          id: name, label: name, lane: "buff", active: false,
          explanation: "Source-owned permanent trait (arena-neutral or inactive).",
        });
        seen.add(name);
      }
      return result;
    } catch (error) {
      console.error("Failed to project permanent passive card states", {
        combatantId: member?.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BATTLEFIELD_PASSIVE_STATES = {
    classifyStatusLanes, permanentPassiveStates, timedEffectLane,
  };
})();
