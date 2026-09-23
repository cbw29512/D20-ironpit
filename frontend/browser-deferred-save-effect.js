(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const S = () => window.IRON_PIT_BROWSER_SAVES;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;
  const O = () => window.IRON_PIT_BROWSER_ATTACK_OUTCOME;
  const D = () => window.IRON_PIT_DICE;
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const BOTH = Object.freeze(["2014", "2024"]);

  const members = (setup) => [...setup.heroes, ...setup.monsters];
  const memberById = (setup, id) => members(setup).find((item) => item.combatant_id === id) || null;
  const ruleFor = (member) => member?.state?.template?.deferred_save_effect || null;
  const markFor = (member, rule) =>
    (member.state.deferred_effects || []).find((item) => item.source_id === rule.source_id) || null;

  function live(member) {
    return !!member && member.state.current_hp > 0 && member.state.is_alive && !member.state.is_dead;
  }

  function candidate(member, setup) {
    const rule = ruleFor(member);
    if (!rule || !E().available(member.state, "action")) return null;
    const mark = markFor(member, rule);
    if (!mark) return null;
    const target = memberById(setup, mark.target_id);
    return live(target) ? target : null;
  }

  function armOnHit(ctx) {
    const member = ctx.member, target = ctx.target, rule = ruleFor(member);
    if (!rule || !(rule.trigger_attack_ids || []).includes(ctx.attack.id) || !live(target)) return null;
    const current = markFor(member, rule);
    if (current) {
      const currentTarget = ctx.setup ? memberById(ctx.setup, current.target_id) : null;
      if (live(currentTarget)) return null;
      member.state.deferred_effects = member.state.deferred_effects.filter(
        (item) => item.source_id !== rule.source_id,
      );
    }
    if (!R().available(member.state, rule.resource_id, rule.resource_cost || 1)) return null;
    R().spend(member.state, rule.resource_id, rule.resource_cost || 1);
    member.state.deferred_effects.push({ source_id: rule.source_id, target_id: target.combatant_id });
    ctx.attackOutcome.deferredEffectArmed = rule.source_name;
    return O().noEventResult(ctx.sequence);
  }

  function resolve(sequence, round, member, setup, expectedTargetId = null) {
    const rule = ruleFor(member);
    if (!rule || !E().available(member.state, "action")) return null;
    const target = candidate(member, setup);
    if (!target || (expectedTargetId && target.combatant_id !== expectedTargetId)) return null;

    const hpBefore = target.state.current_hp, tempBefore = target.state.temporary_hp;
    const deathSuccessBefore = target.state.death_save_successes, deathFailureBefore = target.state.death_save_failures;
    const save = S().resolveSavingThrow(target.state, rule.save_ability, rule.save_dc);
    const affectedStates = members(setup).map((item) => item.state);
    let damageRoll = null, damageComponents = [];

    if (save.succeeded && (rule.success_damage_dice_count || 0) > 0) {
      if (!rule.success_damage_type) throw new Error(`Deferred effect ${rule.source_id} lacks a success damage type.`);
      const rolls = Array.from({ length: rule.success_damage_dice_count }, () => D().roll(rule.success_damage_dice_size));
      const raw = rolls.reduce((sum, value) => sum + value, 0);
      const applied = A().adjustedDamage(target.state, raw, rule.success_damage_type);
      if (applied) A().applyDamage(target.state, applied, false, [rule.success_damage_type], affectedStates);
      damageRoll = {
        notation: `${rule.success_damage_dice_count}d${rule.success_damage_dice_size}`,
        rolls: [...rolls], modifier: 0, total: applied,
      };
      damageComponents = [{
        source: rule.source_name,
        notation: damageRoll.notation,
        rolls: [...rolls],
        modifier: 0,
        damage_type: rule.success_damage_type,
        total: raw,
        applied_total: applied,
      }];
    } else if (!save.succeeded && rule.failure_sets_zero_hp) {
      Z().reduceToZeroHitPoints(target.state, affectedStates);
    }

    E().spend(member.state, "action");
    member.state.deferred_effects = member.state.deferred_effects.filter(
      (item) => item.source_id !== rule.source_id,
    );
    window.IRON_PIT_BROWSER_RAGE?.endIfIncapacitated(target.state);
    C()?.endIfIncapacitated(target.state, affectedStates);

    return {
      sequence, round_number: round, event_type: "feature",
      actor_id: member.combatant_id, actor_name: member.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name,
      saving_throw_roll: save.roll, save_ability: rule.save_ability, save_dc: rule.save_dc,
      save_succeeded: save.succeeded, damage_roll: damageRoll, damage_components: damageComponents,
      hp_before: hpBefore, hp_after: target.state.current_hp,
      temporary_hp_before: tempBefore, temporary_hp_after: target.state.temporary_hp,
      death_save_successes_before: deathSuccessBefore, death_save_failures_before: deathFailureBefore,
      death_save_successes: target.state.death_save_successes, death_save_failures: target.state.death_save_failures,
      is_stable: target.state.is_stable, is_dead: target.state.is_dead,
      feature_id: rule.source_id, animation: "save-effect",
      description: `${member.state.template.name} activates ${rule.source_name} on ${target.state.template.name}; the ${rule.save_ability} save ${save.succeeded ? "succeeds" : "fails"}.`,
    };
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Deferred save effect hook installation requires browser-ability-hooks.js.");
    const phase = hooks.PHASES.ON_HIT;
    if (hooks.abilitiesFor(phase).some((item) => item.id === "deferred-save-effect-arm")) return;
    hooks.registerAbility(phase, {
      id: "deferred-save-effect-arm", priority: 40, rulesets: BOTH,
      appliesTo: (member, ctx) => {
        const rule = ruleFor(member);
        return !!rule && (rule.trigger_attack_ids || []).includes(ctx.attack.id);
      },
      resolve: armOnHit,
    });
  }

  window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT = { armOnHit, candidate, installAbilityHooks, resolve };
  if (window.IRON_PIT_BROWSER_ABILITY_HOOKS) installAbilityHooks();
  else (window.IRON_PIT_PENDING_ABILITY_HOOK_INSTALLERS ||= []).push(installAbilityHooks);
})();
