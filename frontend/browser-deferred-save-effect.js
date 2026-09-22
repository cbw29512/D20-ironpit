(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;
  const D = () => window.IRON_PIT_DICE;
  const O = () => window.IRON_PIT_BROWSER_ATTACK_OUTCOME;
  const members = (setup) => [...setup.heroes, ...setup.monsters];
  const ruleFor = (state) => state.template?.deferred_save_effect || null;

  function arm(state, targetState, targetId, attack, round) {
    try {
      const rule = ruleFor(state);
      if (!rule || !(rule.trigger_weapon_ids || []).includes(attack.weaponId)) return null;
      if (targetState.is_dead || !targetState.is_alive || targetState.current_hp <= 0) return null;
      const active = (state.deferred_effects || []).filter((item) => item.source_id === rule.source_id);
      if (active.length >= (rule.max_active_targets || 1)) return null;
      const cost = rule.resource_cost || 1;
      const uses = state.resources?.[rule.resource_id];
      if (uses == null) throw new Error(`Deferred effect ${rule.source_id} references missing resource ${rule.resource_id}.`);
      if (uses < cost) return null;
      state.resources[rule.resource_id] -= cost;
      state.deferred_effects.push({
        source_id: rule.source_id,
        target_id: targetId,
        armed_round: round,
      });
      return {
        sourceId: rule.source_id,
        sourceName: rule.source_name,
        targetId,
        resourceRemaining: state.resources[rule.resource_id],
        armedRound: round,
      };
    } catch (error) {
      console.error("Browser deferred effect arming failed", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  function candidate(actor, setup) {
    try {
      const rule = ruleFor(actor.state);
      if (!rule || !E().available(actor.state, "action")) return null;
      const byId = new Map(members(setup).map((item) => [item.combatant_id, item]));
      let selected = null;
      const retained = [];
      for (const mark of actor.state.deferred_effects || []) {
        if (mark.source_id !== rule.source_id) {
          retained.push(mark);
          continue;
        }
        const target = byId.get(mark.target_id) || null;
        if (!target || target.state.is_dead || !target.state.is_alive || target.state.current_hp <= 0) continue;
        retained.push(mark);
        if (!selected) selected = target;
      }
      actor.state.deferred_effects = retained;
      return selected;
    } catch (error) {
      console.error("Browser deferred effect candidate failed", { combatant: actor?.combatant_id, error });
      throw error;
    }
  }

  function resolve(sequence, round, actor, setup, expectedTargetId = null) {
    try {
      const target = candidate(actor, setup);
      if (!target) return null;
      if (expectedTargetId && target.combatant_id !== expectedTargetId) {
        throw new Error("Deferred-effect candidate target changed before resolution.");
      }
      const rule = ruleFor(actor.state);
      if (!rule) throw new Error("Deferred-effect candidate exists without immutable source data.");

      const hpBefore = target.state.current_hp;
      const tempBefore = target.state.temporary_hp;
      const deathSuccessBefore = target.state.death_save_successes;
      const deathFailureBefore = target.state.death_save_failures;
      const save = V().resolveSavingThrow(target.state, rule.save_ability, rule.save_dc);
      const affectedStates = members(setup).map((item) => item.state);
      let damageRoll = null;
      let damageComponents = [];

      if (save.succeeded && (rule.success_damage_dice_count || 0) > 0) {
        if (!rule.success_damage_type) throw new Error(`Deferred effect ${rule.source_id} has damage dice without a type.`);
        const rolls = Array.from(
          { length: rule.success_damage_dice_count },
          () => D().roll(rule.success_damage_dice_size),
        );
        const rawTotal = rolls.reduce((sum, value) => sum + value, 0);
        const applied = A().adjustedDamage(target.state, rawTotal, rule.success_damage_type);
        damageComponents = [{
          source: rule.source_name,
          notation: `${rule.success_damage_dice_count}d${rule.success_damage_dice_size}`,
          rolls,
          modifier: 0,
          damage_type: rule.success_damage_type,
          total: rawTotal,
          applied_total: applied,
        }];
        damageRoll = {
          notation: damageComponents[0].notation,
          rolls,
          modifier: 0,
          total: applied,
        };
        A().applyDamage(target.state, applied, false, [rule.success_damage_type], affectedStates);
      } else if (!save.succeeded && rule.failure_sets_zero_hp) {
        Z().reduceToZero(target.state, affectedStates);
      }

      E().spend(actor.state, "action");
      actor.state.deferred_effects = actor.state.deferred_effects.filter(
        (item) => !(item.source_id === rule.source_id && item.target_id === target.combatant_id),
      );
      return {
        sequence,
        round_number: round,
        event_type: "feature",
        actor_id: actor.combatant_id,
        actor_name: actor.state.template.name,
        target_id: target.combatant_id,
        target_name: target.state.template.name,
        saving_throw_roll: save.roll,
        save_ability: rule.save_ability,
        save_dc: rule.save_dc,
        save_succeeded: save.succeeded,
        damage_roll: damageRoll,
        damage_components: damageComponents,
        hp_before: hpBefore,
        hp_after: target.state.current_hp,
        temporary_hp_before: tempBefore,
        temporary_hp_after: target.state.temporary_hp,
        death_save_successes_before: deathSuccessBefore,
        death_save_failures_before: deathFailureBefore,
        death_save_successes: target.state.death_save_successes,
        death_save_failures: target.state.death_save_failures,
        is_stable: target.state.is_stable,
        is_dead: target.state.is_dead,
        feature_id: rule.source_id,
        animation: "save-effect",
        description: `${actor.state.template.name} activates ${rule.source_name} on ${target.state.template.name}; the ${rule.save_ability} save ${save.succeeded ? "succeeds" : "fails"}.`,
      };
    } catch (error) {
      console.error("Browser deferred effect resolution failed", { combatant: actor?.combatant_id, error });
      throw error;
    }
  }

  function installAbilityHooks() {
    try {
      const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
      if (!hooks) throw new Error("Deferred effect hook installation requires browser-ability-hooks.js.");
      const phase = hooks.PHASES.ON_HIT;
      if (hooks.abilitiesFor(phase).some((item) => item.id === "deferred-save-effect")) return;
      hooks.registerAbility(phase, {
        id: "deferred-save-effect",
        priority: 80,
        rulesets: ["2014", "2024"],
        appliesTo: (member) => Boolean(ruleFor(member.state)),
        resolve: (ctx) => {
          const outcome = O().requireOutcome(ctx);
          const armed = arm(
            ctx.member.state,
            ctx.target.state,
            ctx.target.combatant_id,
            ctx.attack,
            ctx.round,
          );
          if (!armed) return null;
          outcome.deferredEffectArmed = armed;
          return O().noEventResult(ctx.sequence);
        },
      });
    } catch (error) {
      console.error("Deferred effect hook installation failed", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT = {
    arm,
    candidate,
    resolve,
    installAbilityHooks,
  };
})();
