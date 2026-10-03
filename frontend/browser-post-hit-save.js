(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_SAVES;
  const F = () => window.IRON_PIT_BROWSER_FORCED_MOVEMENT;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const O = () => window.IRON_PIT_BROWSER_ATTACK_OUTCOME;

  function proficiencyBonus(level) {
    if (!Number.isInteger(level) || level < 1 || level > 20) {
      throw new Error(`Post-hit save DC requires a certified character level; received ${level}.`);
    }
    return 2 + Math.floor((level - 1) / 4);
  }

  function spellSaveDc(attackerState, ability) {
    const scores = attackerState?.template?.ability_scores;
    const level = attackerState?.template?.level;
    const score = scores?.[ability];
    if (!Number.isInteger(score) || !Number.isInteger(level)) {
      throw new Error(`${attackerState?.template?.name || "Combatant"} post-hit save DC requires certified level and ability scores.`);
    }
    return 8 + proficiencyBonus(level) + Math.floor((score - 10) / 2);
  }

  function resolve(attacker, target, setup) {
    try {
      const rider = attacker?.state?.pending_post_hit_failed_save || null;
      if (attacker?.state) attacker.state.pending_post_hit_failed_save = null;
      if (!rider) return null;
      const defender = target?.state;
      if (!defender || defender.current_hp <= 0 || defender.is_dead || !defender.is_alive) return null;
      const dc = spellSaveDc(attacker.state, rider.dc_ability);
      const save = S().resolveSavingThrow(defender, rider.save_ability, dc);
      let applied = null;
      let pushedFt = 0;
      if (!save.succeeded) {
        const immune = rider.condition_id
          ? I().immune(defender, rider.condition_id, attacker.state.template, { sourceIsMagical: true })
          : false;
        if (rider.condition_id && !defender.active_effect_ids.includes(rider.condition_id) && !immune) {
          defender.active_effect_ids.push(rider.condition_id);
          applied = rider.condition_id;
        }
        if (rider.push_ft) {
          if (!setup) throw new Error("Post-hit forced movement requires encounter positions.");
          pushedFt = F().pushStraightAway(target, attacker, setup, rider.push_ft);
        }
      }
      return {
        saveRoll: save.roll,
        saveAbility: rider.save_ability,
        saveDc: dc,
        saveSucceeded: save.succeeded,
        pushedFt,
        appliedCondition: applied,
      };
    } catch (error) {
      console.error("Browser post-hit failed save resolution failed.", error);
      throw error;
    }
  }

  function resolveHit(ctx) {
    const outcome = O().requireOutcome(ctx);
    const resolution = resolve(ctx.member, ctx.target, ctx.setup);
    outcome.postHitSave = resolution;
    if (resolution?.appliedCondition && !outcome.appliedConditions.includes(resolution.appliedCondition)) {
      outcome.appliedConditions.push(resolution.appliedCondition);
    }
    return resolution ? O().noEventResult(ctx.sequence) : null;
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Post-hit save hook installation requires browser-ability-hooks.js.");
    const phase = hooks.PHASES.ON_HIT;
    if (hooks.abilitiesFor(phase).some((item) => item.id === "post-hit-failed-save")) return;
    hooks.registerAbility(phase, {
      id: "post-hit-failed-save",
      priority: 20,
      rulesets: ["2014", "2024"],
      appliesTo: (member) => Boolean(member?.state?.pending_post_hit_failed_save),
      resolve: resolveHit,
    });
  }

  window.IRON_PIT_BROWSER_POST_HIT_SAVE = { installAbilityHooks, resolve, resolveHit, spellSaveDc };
  if (window.IRON_PIT_BROWSER_ABILITY_HOOKS) installAbilityHooks();
  else (window.IRON_PIT_PENDING_ABILITY_HOOK_INSTALLERS ||= []).push(installAbilityHooks);
})();
