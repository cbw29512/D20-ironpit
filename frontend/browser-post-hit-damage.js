(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const S = () => window.IRON_PIT_BROWSER_SPELLCASTING;

  function payment(state, rule, turnKey) {
    if (rule.free_resource_id && R().available(state, rule.free_resource_id, 1)) {
      return { resourceId: rule.free_resource_id, slotLevel: rule.printed_spell_level, expendsSlot: false };
    }
    if (!S().slotSpellAvailable(state, turnKey)) return null;
    for (let level = rule.max_slot_level; level >= rule.printed_spell_level; level -= 1) {
      const resourceId = "spell-slot-" + level;
      if (R().available(state, resourceId, 1)) {
        return { resourceId, slotLevel: level, expendsSlot: true };
      }
    }
    return null;
  }

  function baseCreatureType(raw) {
    return String(raw || "").split(" (", 1)[0].trim().toLowerCase();
  }

  function bonusDamage(attacker, attack, turnKey, target = null) {
    try {
      const rule = attacker?.template?.resource_backed_post_hit_damage;
      if (!rule || !(rule.trigger_attack_ids || []).includes(attack?.id)) return null;
      if (!target || target.current_hp <= 0 || target.is_dead || !target.is_alive) return null;
      if (!turnKey) throw new Error("Post-hit resource damage requires the active turn key.");
      if (!E().available(attacker, rule.action_cost)) return null;
      const paid = payment(attacker, rule, turnKey);
      if (!paid) return null;

      E().spend(attacker, rule.action_cost);
      if (paid.expendsSlot) S().markSlotSpellCast(attacker, turnKey);
      R().spend(attacker, paid.resourceId, 1);

      let count = rule.base_dice_count
        + rule.dice_per_slot_above * (paid.slotLevel - rule.printed_spell_level);
      if ((rule.bonus_target_creature_types || []).includes(baseCreatureType(target.template.creature_type))) {
        count += rule.bonus_target_dice_count || 0;
      }
      return {
        source: rule.source_name,
        diceCount: count,
        diceSize: rule.dice_size,
        damageBonus: 0,
        damageType: rule.damage_type,
      };
    } catch (error) {
      console.error("Browser post-hit resource damage failed", { combatant: attacker?.template?.name, error });
      throw error;
    }
  }

  function activateTriggeredBuff(ctx) {
    try {
      const rule = ctx.member?.state?.template?.resource_backed_post_hit_damage;
      const actionId = rule?.post_hit_self_buff_action_id;
      if (!actionId) return null;
      const outcome = window.IRON_PIT_BROWSER_ATTACK_OUTCOME.requireOutcome(ctx);
      if (!(outcome.damageComponents || []).some((component) => component.source === rule.source_name)) return null;
      const action = (ctx.member.state.template.timed_self_buff_actions || [])
        .find((item) => item.id === actionId);
      if (!action) throw new Error(`Post-hit buff action ${actionId} is not declared.`);
      const timed = window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS;
      if (!timed) throw new Error("Timed self-buff runtime is not loaded.");
      if (!timed.active(ctx.member, action)) {
        timed.resolve(ctx.sequence, ctx.round, ctx.member, action, {
          spendActionCost: false,
          affectedStates: [...ctx.setup.heroes, ...ctx.setup.monsters].map((entry) => entry.state),
        });
      }
      window.IRON_PIT_BROWSER_FRIENDLY_SAVE_AURAS?.sync(ctx.setup);
      outcome.postHitSelfBuffApplied = { sourceId: action.id, sourceName: action.name };
      return window.IRON_PIT_BROWSER_ATTACK_OUTCOME.noEventResult(ctx.sequence);
    } catch (error) {
      console.error("Browser triggered post-hit self-buff failed", {
        combatant: ctx?.member?.combatant_id, error,
      });
      throw error;
    }
  }

  function installAbilityHooks() {
    try {
      const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
      if (!hooks) throw new Error("Post-hit self-buff hook requires browser-ability-hooks.js.");
      const phase = hooks.PHASES.ON_HIT;
      const id = "resource-backed-post-hit-self-buff";
      if (hooks.abilitiesFor(phase).some((item) => item.id === id)) return;
      hooks.registerAbility(phase, {
        id, priority: 70, rulesets: ["2014", "2024"],
        appliesTo: (member) => Boolean(
          member.state.template.resource_backed_post_hit_damage?.post_hit_self_buff_action_id
        ),
        resolve: activateTriggeredBuff,
      });
    } catch (error) {
      console.error("Post-hit self-buff hook installation failed", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_POST_HIT_DAMAGE = { activateTriggeredBuff, bonusDamage, installAbilityHooks };
  if (window.IRON_PIT_BROWSER_ABILITY_HOOKS) installAbilityHooks();
  else (window.IRON_PIT_PENDING_ABILITY_HOOK_INSTALLERS ||= []).push(installAbilityHooks);
})();
