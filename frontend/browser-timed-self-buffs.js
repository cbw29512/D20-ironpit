(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const P = () => window.IRON_PIT_BROWSER_TIMED_SELF_BUFF_POLICY;
  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function active(member, action) {
    return P().active(member, action);
  }

  function choose(member, setup = null, activationTiming = "action", turnKey = null) {
    return P().choose(member, setup, activationTiming, turnKey);
  }

  function resolve(sequence, round, member, action, options = {}) {
    try {
      const spendActionCost = options.spendActionCost !== false;
      if (spendActionCost && !E().available(member.state, action.actionCost)) throw new Error(`${action.name} action cost is unavailable.`);
      if (action.resourceId != null && (member.state.resources[action.resourceId] || 0) < (action.resourceCost || 1)) throw new Error(`${action.name} resource is unavailable.`);
      if (active(member, action)) throw new Error(`${action.name} is already active.`);
      if (options.setup && action.resourceId && String(action.resourceId).startsWith("spell-slot-")
        && window.IRON_PIT_BROWSER_SUPPRESSION_ZONES?.verbalBlocked(member, options.setup)) {
        throw new Error(`${action.name} cannot be cast inside a Silence effect.`);
      }
      if (options.turnKey && action.resourceId && String(action.resourceId).startsWith("spell-slot-")) {
        window.IRON_PIT_BROWSER_SPELLCASTING?.markSlotSpellCast(member.state, options.turnKey);
      }

      if (spendActionCost) E().spend(member.state, action.actionCost);
      if (action.resourceId != null) member.state.resources[action.resourceId] -= action.resourceCost || 1;
      const applied = [];
      let defensesAttached = false;
      const hasDuration = Number.isInteger(action.durationRounds);
      const expiresRound = hasDuration ? round + action.durationRounds : null;
      const expiryTiming = hasDuration ? (action.expiryTiming || "source_turn_start") : null;
      const expiresAtSourceStart = expiryTiming === "source_turn_start";
      (action.conditionIds || []).forEach((conditionId) => {
        const condition = T().apply(member.state, conditionId, member.combatant_id, {
          sourceEffectId: action.id,
          sourceTemplate: member.state.template,
          appliedRound: round,
          expiresRound,
          expiryTiming,
          expiresAtStartOfSourceTurn: expiresAtSourceStart,
          ownedDamageResistances: defensesAttached ? [] : [...(action.damageResistances || [])],
          ownedDebuffCounters: defensesAttached ? [] : [...(action.debuffCounters || [])],
          ownedMovementModeGrants: defensesAttached ? [] : [...(action.movementModeGrants || [])],
          endsIfSourceIncapacitated: Boolean(action.endsIfSourceIncapacitated),
          endsIfSourceDead: Boolean(action.endsIfSourceDead),
          useDefaultPoisonRecovery: false,
        });
        if (condition) { applied.push(condition); defensesAttached = true; }
      });
      if (!defensesAttached && (
        (action.damageResistances || []).length
        || (action.debuffCounters || []).length
        || (action.savingThrowAdvantageGrants || []).length
        || (action.movementModeGrants || []).length
        || action.friendlySaveAdvantageAura
        || action.friendlyCoverAura
        || action.friendlyWeaponDamageAura
        || action.friendlyRecoveryAura
        || action.hostileStartTurnConditionAura
        || action.startTurnEmanationDamage
        || action.meleeHitRetaliation
        || action.spellSaveDcBonus || action.spellAttackAdvantage || (action.modifierEffects || []).length
      )) {
        T().apply(member.state, action.id, member.combatant_id, {
          sourceEffectId: action.id,
          sourceTemplate: member.state.template,
          appliedRound: round,
          expiresRound,
          expiryTiming,
          expiresAtStartOfSourceTurn: expiresAtSourceStart,
          ownedDamageResistances: [...(action.damageResistances || [])],
          ownedDebuffCounters: [...(action.debuffCounters || [])],
          ownedMovementModeGrants: [...(action.movementModeGrants || [])],
          endsIfSourceIncapacitated: Boolean(action.endsIfSourceIncapacitated),
          endsIfSourceDead: Boolean(action.endsIfSourceDead),
          useDefaultPoisonRecovery: false,
        });
      }

      if (action.friendlyRecoveryAura) {
        window.IRON_PIT_BROWSER_FRIENDLY_RECOVERY_AURAS?.activate(member, action, options.setup, round);
      }
      if (action.concentration) {
        const concentration = window.IRON_PIT_BROWSER_CONCENTRATION;
        if (!concentration) throw new Error("Browser Concentration runtime is not loaded.");
        const allStates = options.affectedStates || [member.state];
        const slotLevel = String(action.resourceId || "").startsWith("spell-slot-")
          ? Number.parseInt(String(action.resourceId).slice("spell-slot-".length), 10)
          : null;
        concentration.start(
          member.state,
          member.combatant_id,
          action.id,
          round,
          allStates,
          expiresRound,
          Number.isInteger(slotLevel) ? slotLevel : null,
        );
      }

      if ((action.modifierEffects || []).length) {
        const modifiers = window.IRON_PIT_BROWSER_SPELL_MODIFIERS;
        if (!modifiers) throw new Error("Timed self-buff modifier effects require browser-spell-modifiers.js.");
        for (const [index, effect] of action.modifierEffects.entries()) {
          M().add(member.state, modifiers.build(
            member.combatant_id, member.combatant_id,
            { id: action.id, name: action.name, concentration: Boolean(action.concentration) },
            effect, index, round,
          ));
        }
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
        concentration_started_effect_id: action.concentration ? action.id : null,
        resource_remaining: action.resourceId == null ? null : member.state.resources[action.resourceId],
        animation: action.animation || "buff",
        description: `${member.state.template.name} uses ${action.name}.`,
      };
    } catch (error) {
      console.error("Timed self-buff resolution failed.", { combatant: member?.combatant_id, action: action?.id, error });
      throw error;
    }
  }

  function installAbilityHooks() {
    try {
      const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
      if (!hooks) throw new Error("Timed self-buff hooks require browser-ability-hooks.js.");
      const phase = hooks.PHASES.TURN_START;
      if (hooks.abilitiesFor(phase).some((item) => item.id === "start-turn-timed-self-buff")) return;
      hooks.registerAbility(phase, {
        id: "start-turn-timed-self-buff",
        priority: 70,
        rulesets: ["2014", "2024"],
        appliesTo: (member) =>
          !E().isIncapacitated(member.state)
          && (member.state.template.timed_self_buff_actions || [])
            .some((action) => (action.activationTiming || "action") === "start_turn"),
        resolve: ({ sequence, round, member, setup }) => {
          const action = choose(member, setup, "start_turn");
          if (!action) return null;
          const event = resolve(sequence, round, member, action, {
            spendActionCost: false,
            affectedStates: [...setup.heroes, ...setup.monsters].map((entry) => entry.state),
          });
          return { events: [event], sequence: sequence + 1, claimed: false };
        },
      });
    } catch (error) {
      console.error("Timed self-buff hook installation failed.", { error });
      throw error;
    }
  }

  function spellSaveDcBonus(state) {
    const activeIds = new Set((state.timed_effects || []).map((effect) => effect.source_effect_id));
    return (state.template.timed_self_buff_actions || []).reduce((total, action) => (
      activeIds.has(action.id) ? total + (action.spellSaveDcBonus || 0) : total
    ), 0);
  }

  function spellAttackAdvantage(state) {
    const activeIds = new Set((state.timed_effects || []).map((effect) => effect.source_effect_id));
    return (state.template.timed_self_buff_actions || []).some(
      (action) => action.spellAttackAdvantage && activeIds.has(action.id),
    );
  }

  window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS = {
    active, choose, installAbilityHooks, resolve, spellSaveDcBonus, spellAttackAdvantage,
  };
})();
