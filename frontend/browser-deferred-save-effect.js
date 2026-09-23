(() => {
  "use strict";

  const H = () => window.IRON_PIT_BROWSER_ABILITY_HOOKS;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;
  const D = () => window.IRON_PIT_DICE;

  const ruleFor = (member) => member?.state?.template?.deferred_save_effect || null;
  const memberById = (setup, id) => [...setup.heroes, ...setup.monsters]
    .find((member) => member.combatant_id === id) || null;

  function clearMark(state, sourceId) {
    state.deferred_effects = (state.deferred_effects || []).filter((item) => item.source_id !== sourceId);
  }

  function armOnHit({ sequence, member, target, attack, attackOutcome }) {
    const rule = ruleFor(member);
    if (!rule || !target || target.state.is_dead || target.state.current_hp <= 0) {
      return { events: [], sequence, claimed: false };
    }
    const triggerId = attack.weaponId || attack.weapon?.id || attack.id;
    if (!(rule.trigger_attack_ids || []).includes(triggerId)) {
      return { events: [], sequence, claimed: false };
    }
    const state = member.state;
    state.deferred_effects ||= [];
    if (state.deferred_effects.some((item) => item.source_id === rule.source_id)) {
      return { events: [], sequence, claimed: false };
    }
    const cost = rule.resource_cost || 1;
    if ((state.resources?.[rule.resource_id] || 0) < cost) {
      return { events: [], sequence, claimed: false };
    }
    state.resources[rule.resource_id] -= cost;
    state.deferred_effects.push({ source_id: rule.source_id, target_id: target.combatant_id });
    attackOutcome.deferredEffectArmed = {
      sourceId: rule.source_id,
      sourceName: rule.source_name,
      targetId: target.combatant_id,
    };
    return { events: [], sequence, claimed: false };
  }

  function candidate(member, setup) {
    const rule = ruleFor(member);
    if (!rule || !E().available(member.state, "action")) return null;
    const mark = (member.state.deferred_effects || []).find((item) => item.source_id === rule.source_id);
    if (!mark) return null;
    const target = memberById(setup, mark.target_id);
    if (!target || target.state.is_dead || !target.state.is_alive || target.state.current_hp <= 0) {
      clearMark(member.state, rule.source_id);
      return null;
    }
    return target;
  }

  function resolve(sequence, round, member, setup, expectedTargetId = null) {
    const target = candidate(member, setup);
    if (!target) return null;
    if (expectedTargetId && target.combatant_id !== expectedTargetId) {
      throw new Error("Deferred effect candidate target changed before resolution.");
    }
    const rule = ruleFor(member);
    const hpBefore = target.state.current_hp;
    const temporaryHpBefore = target.state.temporary_hp;
    const deathSuccessBefore = target.state.death_save_successes;
    const deathFailureBefore = target.state.death_save_failures;
    const save = V().resolveSavingThrow(target.state, rule.save_ability, rule.save_dc);
    let damageRoll = null, damageComponents = [];
    const affectedStates = [...setup.heroes, ...setup.monsters].map((item) => item.state);
    if (save.succeeded && (rule.success_damage_dice_count || 0) > 0) {
      if (!rule.success_damage_type) throw new Error(`${rule.source_name} has damage dice but no damage type.`);
      const rolls = D().rollMany(rule.success_damage_dice_count, rule.success_damage_dice_size);
      const raw = rolls.reduce((sum, value) => sum + value, 0);
      const applied = A().adjustedDamage(target.state, raw, rule.success_damage_type);
      damageComponents = [{
        source: rule.source_name,
        notation: `${rule.success_damage_dice_count}d${rule.success_damage_dice_size}`,
        rolls, modifier: 0, damage_type: rule.success_damage_type,
        total: raw, applied_total: applied,
      }];
      damageRoll = { notation: damageComponents[0].notation, rolls, modifier: 0, total: applied };
      if (applied > 0) A().applyDamage(target.state, applied, false, [rule.success_damage_type], affectedStates);
    } else if (!save.succeeded && rule.failure_sets_zero_hp) {
      Z().reduceToZero(target.state, affectedStates);
    }
    E().spend(member.state, "action");
    clearMark(member.state, rule.source_id);
    const description = `${member.state.template.name} activates ${rule.source_name} on ${target.state.template.name}; the ${rule.save_ability} save ${save.succeeded ? "succeeds" : "fails"}.`;
    return {
      sequence, round_number: round, event_type: "feature",
      actor_id: member.combatant_id, actor_name: member.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name,
      saving_throw_roll: save.roll, save_ability: rule.save_ability, save_dc: rule.save_dc,
      save_succeeded: save.succeeded, damage_roll: damageRoll, damage_components: damageComponents,
      hp_before: hpBefore, hp_after: target.state.current_hp,
      temporary_hp_before: temporaryHpBefore, temporary_hp_after: target.state.temporary_hp,
      death_save_successes_before: deathSuccessBefore, death_save_failures_before: deathFailureBefore,
      death_save_successes: target.state.death_save_successes, death_save_failures: target.state.death_save_failures,
      is_stable: target.state.is_stable, is_dead: target.state.is_dead,
      feature_id: rule.source_id, animation: "save-effect", description,
    };
  }

  function installAbilityHook() {
    const hooks = H();
    if (!hooks) throw new Error("Deferred save effect requires browser-ability-hooks.js.");
    const phase = hooks.PHASES.ON_HIT;
    if (hooks.abilitiesFor(phase).some((item) => item.id === "deferred-save-effect-arm")) return;
    hooks.registerAbility(phase, {
      id: "deferred-save-effect-arm",
      priority: 40,
      rulesets: ["2014", "2024"],
      appliesTo: (member) => Boolean(ruleFor(member)),
      resolve: armOnHit,
    });
  }

  installAbilityHook();
  window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT = { candidate, resolve, armOnHit };
})();
