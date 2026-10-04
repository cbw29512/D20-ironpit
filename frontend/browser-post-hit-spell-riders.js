(() => {
  "use strict";

  const EXILE = "banished";

  function paidOption(attacker, turnKey) {
    const optionId = attacker.feature_last_turn_keys?.["paid-post-hit-spell"];
    if (!optionId || attacker.feature_last_turn_keys?.[optionId] !== turnKey) return null;
    const options = attacker.template?.post_hit_spell_options
      || attacker.template?.progression_features?.post_hit_spell_options
      || [];
    return options.find((item) => item.id === optionId) || null;
  }

  function applyRiders(ctx) {
    try {
      const attacker = ctx.member?.state || ctx.member;
      const defender = ctx.target?.state || ctx.target;
      if (!attacker || !defender) return window.IRON_PIT_BROWSER_ATTACK_OUTCOME.noEventResult(ctx.sequence);
      const option = paidOption(attacker, ctx.turnKey);
      if (!option) return window.IRON_PIT_BROWSER_ATTACK_OUTCOME.noEventResult(ctx.sequence);
      const setup = ctx.setup;
      const states = [...(setup?.heroes || []), ...(setup?.monsters || [])].map((item) => item.state || item);
      if (option.concentration) {
        window.IRON_PIT_BROWSER_CONCENTRATION.start(
          attacker, ctx.member.combatant_id, option.id, ctx.round, states,
          ctx.round + Math.max(1, option.duration_rounds || 1),
        );
      }
      if (option.attacks_against_advantage || option.suppress_invisible) {
        const effects = [];
        if (option.attacks_against_advantage) effects.push({ kind: "attacks-against-advantage" });
        if (option.suppress_invisible) {
          effects.push({ kind: "condition-immunity", conditionId: "invisible" });
          if ((defender.active_effect_ids || []).includes("invisible")) {
            window.IRON_PIT_BROWSER_CONDITION_REMOVAL?.removeCondition(defender, "invisible");
          }
        }
        effects.forEach((effect, index) => {
          window.IRON_PIT_BROWSER_MODIFIERS.add(defender, window.IRON_PIT_BROWSER_SPELL_MODIFIERS.build(
            ctx.member.combatant_id, ctx.target.combatant_id, option, effect, index, ctx.round,
          ));
        });
      }
      if (option.save_ability && option.save_dc && option.failed_condition_id) {
        const save = window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow(
          defender, option.save_ability, option.save_dc,
          { condition_id: option.failed_condition_id, effect_tags: ["spell"], roundNumber: ctx.round },
        );
        if (!save.succeeded) {
          if (option.failed_condition_expiry_timing || option.repeat_save_ability || option.duration_rounds) {
            window.IRON_PIT_BROWSER_TIMED.apply(defender, option.failed_condition_id, ctx.member.combatant_id, {
              sourceEffectId: option.id,
              sourceTemplate: attacker.template,
              sourceIsMagical: true,
              appliedRound: ctx.round,
              expiresRound: ctx.round + Math.max(1, option.duration_rounds || 1),
              expiryTiming: option.failed_condition_expiry_timing || null,
              repeatSaveAbility: option.repeat_save_ability || null,
              repeatSaveDc: option.repeat_save_dc || null,
              repeatSaveTiming: option.repeat_save_timing || null,
              useDefaultPoisonRecovery: false,
            });
          } else if (!(defender.active_effect_ids || []).includes(option.failed_condition_id)) {
            defender.active_effect_ids.push(option.failed_condition_id);
          }
          if (option.failed_push_ft) {
            window.IRON_PIT_BROWSER_FORCED_MOVEMENT.pushStraightAway(
              ctx.target, ctx.member, setup, option.failed_push_ft,
            );
          }
        }
      }
      if (option.start_of_turn_dice_count) {
        const slot = Number(attacker.feature_last_turn_keys?.["paid-post-hit-slot"] || option.level);
        const count = option.start_of_turn_dice_count
          + (option.start_of_turn_dice_per_slot_above || 0) * Math.max(0, slot - option.level);
        window.IRON_PIT_BROWSER_TIMED.apply(defender, option.id, ctx.member.combatant_id, {
          sourceEffectId: option.id,
          sourceTemplate: attacker.template,
          sourceIsMagical: true,
          appliedRound: ctx.round,
          expiresRound: ctx.round + Math.max(1, option.duration_rounds || 10),
          expiryTiming: "source_turn_end",
          useDefaultPoisonRecovery: false,
        });
        const effect = (defender.timed_effects || []).find((item) =>
          item.effect_id === option.id && item.source_id === ctx.member.combatant_id);
        if (effect) {
          effect.start_of_turn_dice_count = count;
          effect.start_of_turn_dice_size = option.start_of_turn_dice_size || 6;
          effect.start_of_turn_damage_type = option.start_of_turn_damage_type || "fire";
          effect.start_of_turn_save_ability = option.start_of_turn_save_ability || null;
          effect.start_of_turn_save_dc = option.start_of_turn_save_dc || null;
          effect.start_of_turn_save_ends = Boolean(option.start_of_turn_save_ends);
        }
      }
      if (option.exile_if_hp_at_or_below && defender.current_hp > 0
        && defender.current_hp <= option.exile_if_hp_at_or_below) {
        window.IRON_PIT_BROWSER_TIMED.apply(defender, EXILE, ctx.member.combatant_id, {
          sourceEffectId: option.id,
          sourceTemplate: attacker.template,
          sourceIsMagical: true,
          suppressAction: true,
          suppressBonusAction: true,
          suppressReactions: true,
          suppressMovement: true,
          appliedRound: ctx.round,
          expiresRound: ctx.round + Math.max(1, option.duration_rounds || 1),
          expiryTiming: "source_turn_end",
          removedFromBattlefield: true,
          useDefaultPoisonRecovery: false,
        });
      }
      return window.IRON_PIT_BROWSER_ATTACK_OUTCOME.noEventResult(ctx.sequence);
    } catch (error) {
      console.error("Browser extra-smite riders failed", { combatant: ctx?.member?.combatant_id, error });
      throw error;
    }
  }

  function installAbilityHooks() {
    try {
      const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
      if (!hooks) throw new Error("Extra-smite riders require browser-ability-hooks.js.");
      const phase = hooks.PHASES.ON_HIT;
      const id = "post-hit-spell-riders";
      if (hooks.abilitiesFor(phase).some((item) => item.id === id)) return;
      hooks.registerAbility(phase, {
        id, priority: 75, rulesets: ["2014", "2024"],
        appliesTo: (member) => Boolean(
          (member.state.template.post_hit_spell_options || []).length
          || (member.state.template.progression_features?.post_hit_spell_options || []).length
        ),
        resolve: applyRiders,
      });
    } catch (error) {
      console.error("Extra-smite rider hook installation failed", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_POST_HIT_SPELL_RIDERS = { applyRiders, installAbilityHooks };
  if (window.IRON_PIT_BROWSER_ABILITY_HOOKS) installAbilityHooks();
  else (window.IRON_PIT_PENDING_ABILITY_HOOK_INSTALLERS ||= []).push(installAbilityHooks);
})();
