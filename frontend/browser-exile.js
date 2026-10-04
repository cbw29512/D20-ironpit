(() => {
  "use strict";

  const EFFECT = "banished";

  function removed(state) {
    return (state.timed_effects || []).some((effect) => effect.removed_from_battlefield === true);
  }

  function applyOnHit(ctx) {
    const member = ctx.member, target = ctx.target, rule = member.state.template.resource_backed_on_hit_exile;
    if (!rule || !target?.state?.is_alive || target.state.is_dead || target.state.current_hp <= 0) {
      return window.IRON_PIT_BROWSER_ATTACK_OUTCOME.noEventResult(ctx.sequence);
    }
    if (rule.once_per_turn) {
      if (!ctx.turnKey) throw new Error(rule.source_name + " requires a turn key for its once-per-turn limit.");
      if (member.state.feature_last_turn_keys?.[rule.source_id] === ctx.turnKey) {
        return window.IRON_PIT_BROWSER_ATTACK_OUTCOME.noEventResult(ctx.sequence);
      }
    }
    const available = member.state.resources?.[rule.resource_id] || 0;
    const cost = rule.resource_cost || 1;
    if (available < cost || removed(target.state)) {
      return window.IRON_PIT_BROWSER_ATTACK_OUTCOME.noEventResult(ctx.sequence);
    }
    member.state.resources[rule.resource_id] -= cost;
    if (rule.once_per_turn) {
      member.state.feature_last_turn_keys ||= {};
      member.state.feature_last_turn_keys[rule.source_id] = ctx.turnKey;
    }
    if (rule.save_ability) {
      const saves = window.IRON_PIT_BROWSER_SAVING_THROWS;
      if (!saves?.resolveSavingThrow || rule.save_dc == null) {
        throw new Error(rule.source_name + " requires a save DC and the saving-throw runtime.");
      }
      const save = saves.resolveSavingThrow(target.state, rule.save_ability, rule.save_dc, {
        condition_id: EFFECT,
      });
      if (save.succeeded) return window.IRON_PIT_BROWSER_ATTACK_OUTCOME.noEventResult(ctx.sequence);
    }
    const creatureType = String(target.state.template.creature_type || "").toLowerCase();
    const hitExcluded = (rule.hit_damage_excluded_creature_types || [])
      .map((item) => String(item).toLowerCase())
      .includes(creatureType);
    if (rule.hit_damage_type && rule.hit_damage_dice_count && !hitExcluded) {
      const rolls = window.IRON_PIT_DICE.rollMany(rule.hit_damage_dice_count, rule.hit_damage_dice_size);
      const raw = rolls.reduce((sum, roll) => sum + roll, 0);
      const applied = window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES
        ? window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES.adjustedDamage(target.state, raw, rule.hit_damage_type)
        : raw;
      if (applied) {
        const affected = [...(ctx.setup?.heroes || []), ...(ctx.setup?.monsters || [])]
          .map((item) => item.state);
        window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(
          target.state, applied, false, [rule.hit_damage_type], affected, ctx.setup,
        );
      }
    }
    for (const conditionId of rule.apply_condition_ids || []) {
      window.IRON_PIT_BROWSER_TIMED.apply(target.state, conditionId, member.combatant_id, {
        sourceEffectId: rule.source_id,
        sourceTemplate: member.state.template,
        sourceIsMagical: true,
        appliedRound: ctx.round,
        expiresRound: ctx.round + (rule.duration_rounds || 1),
        expiryTiming: rule.expiry_timing || "source_turn_end",
        useDefaultPoisonRecovery: false,
      });
    }
    window.IRON_PIT_BROWSER_TIMED.apply(target.state, EFFECT, member.combatant_id, {
      sourceEffectId: rule.source_id,
      sourceTemplate: member.state.template,
      sourceIsMagical: true,
      appliedRound: ctx.round,
      expiresRound: ctx.round + (rule.duration_rounds || 1),
      expiryTiming: rule.expiry_timing || "source_turn_end",
      suppressAction: true,
      suppressBonusAction: true,
      suppressReactions: true,
      suppressMovement: true,
      useDefaultPoisonRecovery: false,
      removedFromBattlefield: true,
      returnDamageDiceCount: rule.return_damage_dice_count || 0,
      returnDamageDiceSize: rule.return_damage_dice_size || 0,
      returnDamageBonus: rule.return_damage_bonus || 0,
      returnDamageType: rule.return_damage_type || null,
      returnDamageExcludedCreatureTypes: rule.return_damage_excluded_creature_types || [],
    });
    ctx.attackOutcome.exileApplied = {
      sourceId: rule.source_id,
      sourceName: rule.source_name,
      resourceRemaining: member.state.resources[rule.resource_id],
    };
    return window.IRON_PIT_BROWSER_ATTACK_OUTCOME.noEventResult(ctx.sequence);
  }

  function returnAtSourceEnd(ctx) {
    const events = [];
    const states = [...ctx.setup.heroes, ...ctx.setup.monsters].map((member) => member.state);
    for (const target of [...ctx.setup.heroes, ...ctx.setup.monsters]) {
      const effects = [...(target.state.timed_effects || [])].filter((effect) =>
        effect.source_id === ctx.member.combatant_id
        && effect.removed_from_battlefield
        && effect.expiry_timing === "source_turn_end"
        && (effect.expires_round == null || ctx.round >= effect.expires_round)
      );
      for (const effect of effects) {
        if (!target.state.timed_effects.includes(effect)) continue;
        const hpBefore = target.state.current_hp, tempBefore = target.state.temporary_hp || 0;
        const removedIds = window.IRON_PIT_BROWSER_TIMED.removeGroup(target.state, effect);
        if (!removedIds.length) continue;
        let damageRoll = null, damageComponents = [];
        const excluded = (effect.return_damage_excluded_creature_types || [])
          .map((item) => String(item).toLowerCase())
          .includes(String(target.state.template.creature_type || "").toLowerCase());
        if (effect.return_damage_type && effect.return_damage_dice_count && !excluded) {
          const rolls = window.IRON_PIT_DICE.rollMany(effect.return_damage_dice_count, effect.return_damage_dice_size);
          const raw = rolls.reduce((a, b) => a + b, 0) + (effect.return_damage_bonus || 0);
          const applied = window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES
            ? window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES.adjustedDamage(target.state, raw, effect.return_damage_type)
            : raw;
          damageComponents = [{
            source: effect.source_effect_id || effect.effect_id,
            notation: `${effect.return_damage_dice_count}d${effect.return_damage_dice_size}+${effect.return_damage_bonus || 0}`,
            rolls, modifier: effect.return_damage_bonus || 0,
            damage_type: effect.return_damage_type, total: raw, applied_total: applied,
          }];
          damageRoll = {
            notation: damageComponents[0].notation,
            rolls, modifier: effect.return_damage_bonus || 0, total: applied,
          };
          if (applied) window.IRON_PIT_BROWSER_ZERO_HP.applyDamage(
            target.state, applied, false, [effect.return_damage_type], states,
          );
        }
        events.push({
          sequence: ctx.sequence + events.length, round_number: ctx.round, event_type: "feature",
          actor_id: ctx.member.combatant_id, actor_name: ctx.member.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          removed_condition_ids: removedIds,
          feature_id: effect.source_effect_id || "exile-return",
          animation: "condition-ended",
          damage_roll: damageRoll, damage_components: damageComponents,
          hp_before: hpBefore, hp_after: target.state.current_hp,
          temporary_hp_before: tempBefore, temporary_hp_after: target.state.temporary_hp || 0,
          description: `${target.state.template.name} returns from ${effect.source_effect_id || effect.effect_id}.`
            + (excluded ? " The return damage is suppressed by creature type." : ""),
        });
      }
    }
    return { events, sequence: ctx.sequence + events.length, claimed: false };
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Exile hook installation requires browser-ability-hooks.js.");
    if (!hooks.abilitiesFor(hooks.PHASES.ON_HIT).some((item) => item.id === "resource-backed-on-hit-exile")) {
      hooks.registerAbility(hooks.PHASES.ON_HIT, {
        id: "resource-backed-on-hit-exile", priority: 80, rulesets: ["2014", "2024"],
        appliesTo: (member) => Boolean(member.state.template.resource_backed_on_hit_exile),
        resolve: applyOnHit,
      });
    }
    if (!hooks.abilitiesFor(hooks.PHASES.TURN_END_LIFECYCLE).some((item) => item.id === "exile-return")) {
      hooks.registerAbility(hooks.PHASES.TURN_END_LIFECYCLE, {
        id: "exile-return", priority: 80, rulesets: ["2014", "2024"],
        appliesTo: (_member, ctx) => [...ctx.setup.heroes, ...ctx.setup.monsters]
          .some((target) => (target.state.timed_effects || []).some((effect) =>
            effect.source_id === ctx.member.combatant_id && effect.removed_from_battlefield)),
        resolve: returnAtSourceEnd,
      });
    }
  }

  window.IRON_PIT_BROWSER_EXILE = { EFFECT, installAbilityHooks, removed };
})();