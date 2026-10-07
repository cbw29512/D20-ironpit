(() => {
  "use strict";

  const D = () => window.IRON_PIT_DICE;

  function activeRule(state) {
    try {
      const ids = new Set(state.active_targeting_override_ids || []);
      const rules = (state.template.turn_start_targeting_overrides || []).filter((rule) => ids.has(rule.sourceId));
      if (rules.length > 1) throw new Error("Only one persistent targeting override may control a combatant at a time.");
      return rules[0] || null;
    } catch (error) {
      console.error("Failed browser active targeting-override lookup", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  function syncAfterHpChange(state) {
    try {
      const maximum = window.IRON_PIT_BROWSER_STATE?.effectiveMaxHp(state) || Number(state.template.max_hp || 0);
      if (state.current_hp < maximum) return [];
      const removable = new Set(
        (state.template.turn_start_targeting_overrides || [])
          .filter((rule) => rule.endsOnFullHp !== false)
          .map((rule) => rule.sourceId),
      );
      const ended = (state.active_targeting_override_ids || []).filter((id) => removable.has(id));
      if (ended.length) {
        state.active_targeting_override_ids = (state.active_targeting_override_ids || []).filter((id) => !removable.has(id));
      }
      return ended;
    } catch (error) {
      console.error("Failed browser targeting-override HP synchronization", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  function resolveStartOfTurn(sequence, round, member) {
    try {
      if (!D()?.roll) throw new Error("Targeting-override resolution requires the canonical browser dice provider.");
      syncAfterHpChange(member.state);
      const events = [];
      const active = new Set(member.state.active_targeting_override_ids || []);
      for (const rule of member.state.template.turn_start_targeting_overrides || []) {
        if (active.has(rule.sourceId) || member.state.current_hp <= 0 || member.state.current_hp > rule.maxCurrentHp) continue;
        const dieSize = rule.dieSize || 6;
        const roll = D().roll(dieSize);
        const activated = roll >= rule.minimumRoll;
        if (activated) {
          member.state.active_targeting_override_ids.push(rule.sourceId);
          active.add(rule.sourceId);
        }
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: member.combatant_id, actor_name: member.state.template.name,
          feature_id: rule.sourceId, animation: "feature",
          feature_roll: { notation: `1d${dieSize}`, rolls: [roll], selected_roll: roll, modifier: 0, mode: "normal", total: roll },
          description: `${member.state.template.name} rolls ${roll} for ${rule.sourceName}: ${activated ? "the targeting override activates" : "it does not activate"}.`,
        });
      }
      return { events, sequence };
    } catch (error) {
      console.error("Failed browser turn-start targeting override", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  function installAbilityHook() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) {
      window.IRON_PIT_PENDING_ABILITY_HOOK_INSTALLERS ||= [];
      window.IRON_PIT_PENDING_ABILITY_HOOK_INSTALLERS.push(installAbilityHook);
      return;
    }
    const phase = hooks.PHASES.TURN_START;
    if (hooks.abilitiesFor(phase).some((ability) => ability.id === "turn-start-targeting-override")) return;
    hooks.registerAbility(phase, {
      id: "turn-start-targeting-override", priority: 15, rulesets: ["2014", "2024"],
      appliesTo: (member) => Boolean(member.state.template.turn_start_targeting_overrides?.length),
      resolve: ({ sequence, round, member }) => {
        const result = resolveStartOfTurn(sequence, round, member);
        return result.events.length ? { events: result.events, sequence: result.sequence, claimed: false } : null;
      },
    });
  }

  window.IRON_PIT_BROWSER_TARGETING_OVERRIDES = {
    activeRule, installAbilityHook, resolveStartOfTurn, syncAfterHpChange,
  };
  installAbilityHook();
})();
