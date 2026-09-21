(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;
  const D = () => window.IRON_PIT_DICE;

  const members = (setup) => [...setup.heroes, ...setup.monsters];
  const ruleFor = (state) => state.template?.deferred_save_effect || null;
  const markFor = (state, sourceId) =>
    (state.deferred_effects || []).find((item) => item.source_id === sourceId) || null;

  function arm(state, targetId, attackId) {
    const rule = ruleFor(state);
    if (!rule || !(rule.trigger_attack_ids || []).includes(attackId)) return null;
    if (markFor(state, rule.source_id)) return null;
    const uses = state.resources?.[rule.resource_id] || 0;
    if (uses < (rule.resource_cost || 1)) return null;
    state.resources[rule.resource_id] -= rule.resource_cost || 1;
    state.deferred_effects.push({ source_id: rule.source_id, target_id: targetId });
    return rule.source_id;
  }

  function candidate(actor, setup) {
    const rule = ruleFor(actor.state);
    if (!rule || !E().available(actor.state, "action")) return null;
    const mark = markFor(actor.state, rule.source_id);
    if (!mark) return null;
    const target = members(setup).find((item) => item.combatant_id === mark.target_id) || null;
    if (!target || target.state.is_dead || !target.state.is_alive || target.state.current_hp <= 0) {
      actor.state.deferred_effects = actor.state.deferred_effects.filter(
        (item) => item.source_id !== rule.source_id,
      );
      return null;
    }
    return target;
  }

  function resolve(sequence, round, actor, setup, expectedTargetId = null) {
    const target = candidate(actor, setup);
    if (!target) return null;
    if (expectedTargetId && target.combatant_id !== expectedTargetId) {
      throw new Error("Deferred-effect candidate target changed before resolution.");
    }
    const rule = ruleFor(actor.state);
    const hpBefore = target.state.current_hp;
    const tempBefore = target.state.temporary_hp;
    const deathSuccessBefore = target.state.death_save_successes;
    const deathFailureBefore = target.state.death_save_failures;
    const save = V().resolveSavingThrow(target.state, rule.save_ability, rule.save_dc);
    const affectedStates = members(setup).map((item) => item.state);
    let damageRoll = null;
    let damageComponents = [];
    if (save.succeeded) {
      const rolls = Array.from(
        { length: rule.success_damage_dice_count || 0 },
        () => D().roll(rule.success_damage_dice_size),
      );
      const rawTotal = rolls.reduce((sum, value) => sum + value, 0);
      const applied = A().adjustedDamage(target.state, rawTotal, rule.success_damage_type);
      damageComponents = [{
        source: rule.source_id,
        notation: `${rule.success_damage_dice_count}d${rule.success_damage_dice_size}`,
        rolls, modifier: 0, damage_type: rule.success_damage_type,
        total: rawTotal, applied_total: applied,
      }];
      damageRoll = {
        notation: damageComponents[0].notation, rolls, modifier: 0, total: applied,
      };
      A().applyDamage(target.state, applied, false, [rule.success_damage_type], affectedStates);
    } else if (rule.failure_sets_zero_hp) {
      Z().reduceToZero(target.state, affectedStates);
    }
    E().spend(actor.state, "action");
    actor.state.deferred_effects = actor.state.deferred_effects.filter(
      (item) => item.source_id !== rule.source_id,
    );
    return {
      sequence, round_number: round, event_type: "feature",
      actor_id: actor.combatant_id, actor_name: actor.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name,
      saving_throw_roll: save.roll, save_ability: rule.save_ability,
      save_dc: rule.save_dc, save_succeeded: save.succeeded,
      damage_roll: damageRoll, damage_components: damageComponents,
      hp_before: hpBefore, hp_after: target.state.current_hp,
      temporary_hp_before: tempBefore, temporary_hp_after: target.state.temporary_hp,
      death_save_successes_before: deathSuccessBefore,
      death_save_failures_before: deathFailureBefore,
      death_save_successes: target.state.death_save_successes,
      death_save_failures: target.state.death_save_failures,
      is_stable: target.state.is_stable, is_dead: target.state.is_dead,
      feature_id: rule.source_id, animation: "save-effect",
      description: `${actor.state.template.name} activates ${rule.source_id.replaceAll("-", " ")} on ${target.state.template.name}; the ${rule.save_ability} save ${save.succeeded ? "succeeds" : "fails"}.`,
    };
  }

  window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT = { arm, candidate, resolve };
})();
