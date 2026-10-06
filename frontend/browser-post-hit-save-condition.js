(() => {
  "use strict";

  const SIZE_RANK = { tiny: 0, small: 1, medium: 2, large: 3, huge: 4, gargantuan: 5 };
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const S = () => window.IRON_PIT_BROWSER_SAVES;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const SC = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const D = () => window.IRON_PIT_DICE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;

  function members(setup) {
    return [...(setup?.heroes || []), ...(setup?.monsters || [])];
  }

  function sizeAtLeast(size, minimum) {
    return (SIZE_RANK[String(size || "").toLowerCase()] ?? -1)
      >= (SIZE_RANK[String(minimum || "").toLowerCase()] ?? 99);
  }

  function slotLevel(caster, action, turnKey) {
    const levels = SC().legalSlotLevels(caster.state, turnKey, action.level, { higherSlotScaling: true });
    return levels.length ? Math.min(...levels) : null;
  }

  function resolveHit(ctx) {
    try {
      const attacker = ctx.member;
      const target = ctx.target;
      if (!E().available(attacker.state, "bonus_action")) return null;
      if (target.state.current_hp <= 0 || target.state.is_dead) return null;
      for (const action of attacker.state.template.post_hit_save_condition_spells || []) {
        if (attacker.state.concentration) continue;
        const selected = slotLevel(attacker, action, ctx.turnKey);
        if (selected == null) continue;
        E().spend(attacker.state, action.action_cost || "bonus_action");
        SC().markSlotSpellCast(attacker.state, ctx.turnKey);
        attacker.state.resources[`spell-slot-${selected}`] -= 1;
        const affected = members(ctx.setup).map((item) => item.state);
        C().start(
          attacker.state, attacker.combatant_id, action.id, ctx.round,
          affected, ctx.round + action.duration_rounds, selected,
        );
        const advantage = action.size_save_advantage_from
          && sizeAtLeast(target.state.template.size, action.size_save_advantage_from)
          ? [`${action.name} size`] : [];
        const save = S().resolveSavingThrow(target.state, action.save_ability, action.save_dc, {
          conditionId: action.failed_condition_id,
          magicalEffect: true,
          spellEffect: true,
          advantageSources: advantage,
        });
        if (save.succeeded && action.success_ends_spell) C().end(attacker.state, affected);
        else if (!save.succeeded) {
          T().apply(target.state, action.failed_condition_id, attacker.combatant_id, {
            sourceEffectId: action.id, sourceTemplate: attacker.state.template, sourceIsMagical: true,
            appliedRound: ctx.round, expiresRound: ctx.round + action.duration_rounds,
            expiryTiming: "source_turn_end", useDefaultPoisonRecovery: false,
          });
        }
        const outcome = window.IRON_PIT_BROWSER_ATTACK_OUTCOME.requireOutcome(ctx);
        outcome.postHitSaveCondition = {
          id: action.id, saveDc: action.save_dc, saveSucceeded: save.succeeded, applied: !save.succeeded,
        };
        return window.IRON_PIT_BROWSER_ATTACK_OUTCOME.noEventResult(ctx.sequence);
      }
      return null;
    } catch (error) {
      console.error("Post-hit save-condition spell failed.", error);
      throw error;
    }
  }

  function resolveStartOfTurn(sequence, round, member, setup) {
    try {
      const regen = window.IRON_PIT_BROWSER_REGENERATION?.resolve(sequence, round, member);
      const events = [];
      if (regen) { events.push(...regen.events); sequence = regen.sequence; }
      window.IRON_PIT_BROWSER_FRIENDLY_RECOVERY_AURAS?.resolveWindows(member, setup);
      for (const source of members(setup)) {
        const concentration = source.state.concentration;
        if (!concentration) continue;
        const action = (source.state.template.post_hit_save_condition_spells || [])
          .find((item) => item.id === concentration.effect_id);
        if (!action || action.start_of_turn_dice_count <= 0) continue;
        const linked = (member.state.timed_effects || []).some((effect) =>
          effect.effect_id === action.failed_condition_id
          && effect.source_id === source.combatant_id
          && effect.source_effect_id === action.id,
        );
        if (!linked || !(member.state.active_effect_ids || []).includes(action.failed_condition_id)) continue;
        const slot = concentration.slot_level || action.level;
        const count = action.start_of_turn_dice_count
          + action.start_of_turn_dice_per_slot_above * Math.max(0, slot - action.level);
        const total = D().rollMany(count, action.start_of_turn_dice_size)
          .reduce((sum, roll) => sum + roll, 0);
        const hpBefore = member.state.current_hp;
        const applied = A().resolveDamage
          ? A().resolveDamage(member.state, total, action.start_of_turn_damage_type).applied
          : A().adjustedDamage(member.state, total, action.start_of_turn_damage_type);
        A().applyDamage(
          member.state, applied, false, [action.start_of_turn_damage_type],
          members(setup).map((item) => item.state), setup,
        );
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: member.combatant_id, actor_name: member.state.template.name,
          target_id: member.combatant_id, target_name: member.state.template.name,
          feature_id: action.name, hp_before: hpBefore, hp_after: member.state.current_hp,
          description: `${action.name} deals ${applied} ${action.start_of_turn_damage_type} damage to ${member.state.template.name} at the start of the turn.`,
        });
      }
      const burns = window.IRON_PIT_BROWSER_START_OF_TURN_TIMED_BURN?.resolve(sequence, round, member, setup);
      if (burns) { events.push(...burns.events); sequence = burns.sequence; }
      return { events, sequence };
    } catch (error) {
      console.error("Start-of-turn save-condition damage failed.", error);
      throw error;
    }
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Post-hit save-condition hooks require browser-ability-hooks.js.");
    const phase = hooks.PHASES.ON_HIT;
    if (hooks.abilitiesFor(phase).some((item) => item.id === "post-hit-save-condition")) return;
    hooks.registerAbility(phase, {
      id: "post-hit-save-condition", priority: 35, rulesets: ["2024"],
      appliesTo: (member) => (member.state.template.post_hit_save_condition_spells || []).length > 0,
      resolve: resolveHit,
    });
  }

  window.IRON_PIT_BROWSER_POST_HIT_SAVE_CONDITION = {
    installAbilityHooks, resolveHit, resolveStartOfTurn,
  };
  if (window.IRON_PIT_BROWSER_ABILITY_HOOKS) installAbilityHooks();
  else (window.IRON_PIT_PENDING_ABILITY_HOOK_INSTALLERS ||= []).push(installAbilityHooks);
})();
