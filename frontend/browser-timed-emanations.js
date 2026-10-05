(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  const members = (setup) => [...(setup?.heroes || []), ...(setup?.monsters || [])];

  function activeEmanations(source) {
    try {
      const activeIds = new Set((source.state.timed_effects || [])
        .filter((effect) => effect.source_id === source.combatant_id && effect.source_effect_id)
        .map((effect) => effect.source_effect_id));
      return (source.state.template.timed_self_buff_actions || [])
        .filter((action) => activeIds.has(action.id)
          && (action.startTurnEmanationDamage || action.hostileStartTurnConditionAura));
    } catch (error) {
      console.error("Failed browser timed emanation discovery.", { combatant: source?.combatant_id, error });
      throw error;
    }
  }

  function resolveStartOfTurn(sequence, round, target, setup) {
    try {
      const events = [];
      const all = members(setup);
      for (const source of all) {
        if (source.side === target.side) continue;
        for (const action of activeEmanations(source)) {
          const distance = S().distance(source, target);
          const aura = action.hostileStartTurnConditionAura;
          if (aura && aura.trigger === "enemy_turn_start" && distance <= aura.radius_ft) {
            const immunityId = `${action.id}:success-immunity:${source.combatant_id}`;
            const immune = (target.state.timed_effects || []).some((effect) => effect.effect_id === immunityId);
            if (!immune) {
              const saveRuntime = window.IRON_PIT_BROWSER_SAVES;
              const timed = window.IRON_PIT_BROWSER_TIMED;
              if (!saveRuntime?.resolveSavingThrow || !timed?.apply) {
                throw new Error("Hostile condition aura requires browser saving-throw and timed-effect runtimes.");
              }
              const save = saveRuntime.resolveSavingThrow(target.state, aura.save_ability, aura.save_dc, {
                magicalEffect: Boolean(aura.source_is_magical),
                effectTags: [aura.condition_id],
              });
              const applied = [];
              if (save.succeeded) {
                if (aura.success_immunity || aura.successImmunity) {
                  const granted = window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS?.grantImmunity;
                  if (!granted) throw new Error("Hostile condition aura immunity requires failed-save timed-effect runtime.");
                  granted(target.state, action.id, source.combatant_id, round, {
                    sourceTemplate: source.state.template,
                    sourceIsMagical: Boolean(aura.source_is_magical),
                  });
                }
              } else {
                const condition = timed.apply(target.state, aura.condition_id, source.combatant_id, {
                  sourceEffectId: action.id,
                  sourceTemplate: source.state.template,
                  sourceIsMagical: Boolean(aura.source_is_magical),
                  appliedRound: round,
                  expiresRound: round + action.durationRounds,
                  expiryTiming: action.expiryTiming || "source_turn_start",
                  expiresAtStartOfSourceTurn: (action.expiryTiming || "source_turn_start") === "source_turn_start",
                  endsIfSourceIncapacitated: Boolean(action.endsIfSourceIncapacitated),
                  endsIfSourceDead: Boolean(action.endsIfSourceDead),
                  useDefaultPoisonRecovery: false,
                });
                if (condition) applied.push(condition);
              }
              events.push({
                sequence: sequence++, round_number: round, event_type: "feature",
                actor_id: source.combatant_id, actor_name: source.state.template.name,
                target_id: target.combatant_id, target_name: target.state.template.name,
                saving_throw_roll: save.roll, save_ability: aura.save_ability,
                save_dc: aura.save_dc, save_succeeded: save.succeeded,
                applied_condition_ids: applied, distance_before_ft: distance,
                feature_id: action.id, animation: action.animation || "aura",
                description: `${target.state.template.name} starts its turn within ${distance} feet of ${source.state.template.name}'s ${action.name} and ${save.succeeded ? "resists" : "fails against"} its aura.`,
              });
            }
          }

          const emanation = action.startTurnEmanationDamage;
          if (!emanation || !["enemy_turn_start", "enter_or_start"].includes(emanation.trigger || "enemy_turn_start")) continue;
          window.IRON_PIT_BROWSER_EMANATION_SPEED?.sync(setup);
          const hit = window.IRON_PIT_BROWSER_EMANATION_SAVE_DAMAGE.resolveHit(
            sequence, round, source, target, action, setup, `${round}:${target.combatant_id}`,
          );
          if (hit.event) {
            events.push(hit.event);
            sequence = hit.sequence;
          }
        }
      }
      return { events, sequence };
    } catch (error) {
      console.error("Failed browser timed emanation turn-start resolution.", { combatant: target?.combatant_id, error });
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
    if (hooks.abilitiesFor(phase).some((ability) => ability.id === "timed-emanation-damage")) return;
    hooks.registerAbility(phase, {
      id: "timed-emanation-damage",
      priority: 20,
      rulesets: ["2014", "2024"],
      appliesTo: (_member, ctx) => members(ctx.setup).some((source) =>
        activeEmanations(source).some((action) =>
          ["enemy_turn_start", "enter_or_start"].includes(action.startTurnEmanationDamage?.trigger || "")
          || action.hostileStartTurnConditionAura?.trigger === "enemy_turn_start")),
      resolve: ({ sequence, round, member, setup }) => {
        const result = resolveStartOfTurn(sequence, round, member, setup);
        return result.events.length
          ? { events: result.events, sequence: result.sequence, claimed: false }
          : null;
      },
    });
  }

  window.IRON_PIT_BROWSER_TIMED_EMANATIONS = { activeEmanations, installAbilityHook, resolveStartOfTurn };
  installAbilityHook();
})();