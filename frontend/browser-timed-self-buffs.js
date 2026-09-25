(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function active(member, action) {
    try {
      return (member.state.timed_effects || []).some((effect) =>
        effect.source_id === member.combatant_id && effect.source_effect_id === action.id);
    } catch (error) {
      console.error("Timed self-buff activity lookup failed.", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  function choose(member) {
    try {
      const choices = (member.state.template.timed_self_buff_actions || []).filter((action) =>
        E().available(member.state, action.actionCost)
        && (member.state.resources[action.resourceId] || 0) >= (action.resourceCost || 1)
        && !active(member, action));
      choices.sort((a, b) => (b.priority || 0) - (a.priority || 0));
      return choices[0] || null;
    } catch (error) {
      console.error("Timed self-buff choice failed.", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  function resolve(sequence, round, member, action) {
    try {
      if (!E().available(member.state, action.actionCost)) throw new Error(`${action.name} action cost is unavailable.`);
      if ((member.state.resources[action.resourceId] || 0) < (action.resourceCost || 1)) throw new Error(`${action.name} resource is unavailable.`);
      if (active(member, action)) throw new Error(`${action.name} is already active.`);

      E().spend(member.state, action.actionCost);
      member.state.resources[action.resourceId] -= action.resourceCost || 1;
      const applied = [];
      let defensesAttached = false;
      (action.conditionIds || []).forEach((conditionId) => {
        const condition = T().apply(member.state, conditionId, member.combatant_id, {
          sourceEffectId: action.id,
          sourceTemplate: member.state.template,
          appliedRound: round,
          expiresRound: round + action.durationRounds,
          expiryTiming: action.expiryTiming || "source_turn_start",
          expiresAtStartOfSourceTurn: (action.expiryTiming || "source_turn_start") === "source_turn_start",
          ownedDamageResistances: defensesAttached ? [] : [...(action.damageResistances || [])],
          ownedDebuffCounters: defensesAttached ? [] : [...(action.debuffCounters || [])],
          useDefaultPoisonRecovery: false,
        });
        if (condition) { applied.push(condition); defensesAttached = true; }
      });
      if (!defensesAttached && (
        (action.damageResistances || []).length
        || (action.debuffCounters || []).length
        || (action.savingThrowAdvantageGrants || []).length
        || action.startTurnEmanationDamage
      )) {
        T().apply(member.state, action.id, member.combatant_id, {
          sourceEffectId: action.id,
          sourceTemplate: member.state.template,
          appliedRound: round,
          expiresRound: round + action.durationRounds,
          expiryTiming: action.expiryTiming || "source_turn_start",
          expiresAtStartOfSourceTurn: (action.expiryTiming || "source_turn_start") === "source_turn_start",
          ownedDamageResistances: [...(action.damageResistances || [])],
          ownedDebuffCounters: [...(action.debuffCounters || [])],
          useDefaultPoisonRecovery: false,
        });
      }

      for (const grant of action.savingThrowAdvantageGrants || []) {
        for (const ability of grant.abilities || []) {
          M().add(member.state, {
            id: `${member.combatant_id}:${action.id}:save-advantage:${ability}`,
            source_id: member.combatant_id,
            source_effect_id: action.id,
            source_name: grant.source_name,
            kind: "saving-throw-advantage",
            save_ability: ability,
            requires_magical_effect: Boolean(grant.requires_magical_effect),
            requires_spell_effect: Boolean(grant.requires_spell_effect),
            source_creature_types: [...(grant.source_creature_types || [])],
            required_effect_tags: [...(grant.required_effect_tags || [])],
          });
        }
      }

      return {
        sequence, round_number: round, event_type: "feature",
        actor_id: member.combatant_id, actor_name: member.state.template.name,
        target_id: member.combatant_id, target_name: member.state.template.name,
        applied_condition_ids: applied, feature_id: action.id,
        resource_remaining: member.state.resources[action.resourceId],
        animation: action.animation || "buff",
        description: `${member.state.template.name} uses ${action.name}.`,
      };
    } catch (error) {
      console.error("Timed self-buff resolution failed.", { combatant: member?.combatant_id, action: action?.id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS = { active, choose, resolve };
})();
