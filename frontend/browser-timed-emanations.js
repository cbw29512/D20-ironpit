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
        .filter((action) => activeIds.has(action.id) && action.startTurnEmanationDamage)
        .map((action) => [action, action.startTurnEmanationDamage]);
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
        for (const [action, emanation] of activeEmanations(source)) {
          if (emanation.trigger !== "enemy_turn_start") continue;
          const distance = S().distance(source, target);
          if (distance > emanation.radius_ft) continue;

          const hpBefore = target.state.current_hp;
          const tempBefore = target.state.temporary_hp || 0;
          const successBefore = target.state.death_save_successes || 0;
          const failureBefore = target.state.death_save_failures || 0;
          const applied = A().adjustedDamage(
            target.state,
            emanation.fixed_damage,
            emanation.damage_type,
          );
          if (applied > 0) {
            A().applyDamage(
              target.state,
              applied,
              false,
              [emanation.damage_type],
              all.map((member) => member.state),
            );
          }
          events.push({
            sequence: sequence++, round_number: round, event_type: "feature",
            actor_id: source.combatant_id, actor_name: source.state.template.name,
            target_id: target.combatant_id, target_name: target.state.template.name,
            damage_roll: {
              notation: String(emanation.fixed_damage), rolls: [], modifier: 0, total: applied,
            },
            damage_components: [{
              source: action.name, notation: String(emanation.fixed_damage), rolls: [], modifier: 0,
              damage_type: emanation.damage_type, total: emanation.fixed_damage, applied_total: applied,
            }],
            hp_before: hpBefore, hp_after: target.state.current_hp,
            temporary_hp_before: tempBefore, temporary_hp_after: target.state.temporary_hp || 0,
            death_save_successes_before: successBefore, death_save_failures_before: failureBefore,
            death_save_successes: target.state.death_save_successes || 0,
            death_save_failures: target.state.death_save_failures || 0,
            is_stable: Boolean(target.state.is_stable), is_dead: Boolean(target.state.is_dead),
            distance_before_ft: distance, feature_id: action.id, animation: action.animation || "radiant-aura",
            description: `${target.state.template.name} starts its turn within ${distance} feet of ${source.state.template.name}'s ${action.name} and takes ${applied} ${emanation.damage_type} damage.`,
          });
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
        activeEmanations(source).some(([, emanation]) => emanation.trigger === "enemy_turn_start")),
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