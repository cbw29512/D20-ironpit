(() => {
  "use strict";

  const D = () => window.IRON_PIT_DICE;

  function syncAfterHpChange(state) {
    try {
      const maximum = window.IRON_PIT_BROWSER_STATE?.effectiveMaxHp(state) || Number(state.template.max_hp || 0);
      if (state.current_hp < maximum) return [];
      const removable = new Set(
        (state.template.turn_start_persistent_effects || [])
          .filter((rule) => rule.endsOnFullHp !== false)
          .map((rule) => rule.effectId),
      );
      const ended = (state.active_effect_ids || []).filter((id) => removable.has(id));
      if (ended.length) {
        state.active_effect_ids = (state.active_effect_ids || []).filter((id) => !removable.has(id));
      }
      return ended;
    } catch (error) {
      console.error("Failed browser turn-start effect HP synchronization", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  function resolveStartOfTurn(sequence, round, member) {
    try {
      if (!D()?.roll) throw new Error("Turn-start persistent effects require the canonical browser dice provider.");
      syncAfterHpChange(member.state);
      const events = [];
      for (const rule of member.state.template.turn_start_persistent_effects || []) {
        if (
          (member.state.active_effect_ids || []).includes(rule.effectId)
          || member.state.current_hp <= 0
          || member.state.current_hp > rule.maxCurrentHp
        ) continue;
        const dieSize = rule.dieSize || 6;
        const roll = D().roll(dieSize);
        const activated = roll >= rule.minimumRoll;
        if (activated) member.state.active_effect_ids.push(rule.effectId);
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: member.combatant_id, actor_name: member.state.template.name,
          feature_id: rule.sourceId, animation: "feature",
          feature_roll: { notation: `1d${dieSize}`, rolls: [roll], selected_roll: roll, modifier: 0, mode: "normal", total: roll },
          description: `${member.state.template.name} rolls ${roll} for ${rule.sourceName}: ${rule.sourceName} ${activated ? "activates" : "does not activate"}.`,
        });
      }
      return { events, sequence };
    } catch (error) {
      console.error("Failed browser turn-start persistent effect resolution", { combatant: member?.combatant_id, error });
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
    if (hooks.abilitiesFor(phase).some((ability) => ability.id === "turn-start-persistent-effect")) return;
    hooks.registerAbility(phase, {
      id: "turn-start-persistent-effect", priority: 15, rulesets: ["2014", "2024"],
      appliesTo: (member) => Boolean(member.state.template.turn_start_persistent_effects?.length),
      resolve: ({ sequence, round, member }) => {
        const result = resolveStartOfTurn(sequence, round, member);
        return result.events.length ? { events: result.events, sequence: result.sequence, claimed: false } : null;
      },
    });
  }

  window.IRON_PIT_BROWSER_TURN_START_EFFECTS = { installAbilityHook, resolveStartOfTurn, syncAfterHpChange };
  installAbilityHook();
})();
