(() => {
  "use strict";

  const D = () => window.IRON_PIT_DICE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const DD = () => {
    const rules = window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES;
    if (!rules?.resolveDamage) throw new Error("Start-of-turn damage requires the shared damage resolver.");
    return rules;
  };
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const members = (setup) => [...(setup?.heroes || []), ...(setup?.monsters || [])];

  function loseHitPoints(state, amount, affectedStates = []) {
    try {
      if (!Number.isInteger(amount) || amount < 0) throw new Error("HP loss must be a nonnegative integer.");
      if (!amount || state.is_dead || !state.is_alive || state.current_hp <= 0) return 0;
      const before = state.current_hp;
      if (amount >= before) {
        const zero = window.IRON_PIT_BROWSER_ZERO_HP;
        if (!zero?.reduceToZero) throw new Error("Direct HP loss requires universal zero-HP lifecycle.");
        zero.reduceToZero(state, affectedStates);
      } else state.current_hp -= amount;
      return before - state.current_hp;
    } catch (error) {
      console.error("Direct HP loss failed", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  function applyOrStackHpLoss(state, effectId, sourceId, sourceEffectId, diceCount, diceSize, endsOnMagicalHealing = false) {
    try {
      if (!effectId || !sourceId || !sourceEffectId || !Number.isInteger(diceCount)
        || diceCount < 1 || !Number.isInteger(diceSize) || diceSize < 2) {
        throw new Error("Source-owned ongoing HP loss requires valid identities and dice.");
      }
      if (state.is_dead || !state.is_alive) return 0;
      const match = (state.timed_effects || []).find((effect) =>
        effect.effect_id === effectId && effect.source_id === sourceId
        && effect.source_effect_id === sourceEffectId);
      if (match) {
        if (!(match.start_of_turn_hp_loss_dice_count > 0)
          || match.start_of_turn_hp_loss_dice_size !== diceSize) throw new Error("Incompatible wound stack.");
        if (Boolean(match.ends_on_magical_healing) !== Boolean(endsOnMagicalHealing)) {
          throw new Error("Incompatible wound healing-removal semantics.");
        }
        const count = match.start_of_turn_hp_loss_dice_count + diceCount;
        if (count > 40) throw new Error("HP-loss stack exceeds supported dice limit.");
        match.start_of_turn_hp_loss_dice_count = count;
        return count;
      }
      (state.timed_effects ||= []).push({
        effect_id: effectId, source_id: sourceId, source_effect_id: sourceEffectId,
        expires_at_start_of_source_turn: false,
        start_of_turn_hp_loss_dice_count: diceCount,
        start_of_turn_hp_loss_dice_size: diceSize,
        ends_on_magical_healing: Boolean(endsOnMagicalHealing),
      });
      state.active_effect_ids ||= [];
      if (!state.active_effect_ids.includes(effectId)) state.active_effect_ids.push(effectId);
      return diceCount;
    } catch (error) {
      console.error("Ongoing HP-loss stack failed", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  function resolve(sequence, round, member, setup) {
    try {
      const events = [];
      const states = members(setup).map((item) => item.state || item);
      for (const effect of [...(member.state.timed_effects || [])]) {
        if ((effect.start_of_turn_dice_count || 0) <= 0 || !effect.start_of_turn_damage_type) continue;
        let total = 0;
        for (let index = 0; index < effect.start_of_turn_dice_count; index += 1) {
          total += D().roll(effect.start_of_turn_dice_size || 6);
        }
        const damageType = effect.start_of_turn_damage_type;
        const hpBefore = member.state.current_hp;
        const resolvedDamage = DD().resolveDamage(member.state, total, damageType);
        const applied = resolvedDamage.applied;
        A().applyDamage(
          member.state, applied, false, [damageType], states, setup,
        );
        const name = effect.source_effect_id || effect.effect_id;
        events.push({
          sequence: sequence++,
          round_number: round,
          event_type: "feature",
          actor_id: member.combatant_id,
          actor_name: member.state.template.name,
          target_id: member.combatant_id,
          target_name: member.state.template.name,
          feature_id: name,
          hp_before: hpBefore,
          hp_after: member.state.current_hp,
          animation: "feature",
          description: `${name} deals ${applied} ${damageType} damage to ${member.state.template.name} at the start of the turn.`
            + (resolvedDamage.sourceName ? ` ${resolvedDamage.sourceName} restores ${resolvedDamage.healed} HP.` : ""),
        });
        if (!(effect.start_of_turn_save_ends && effect.start_of_turn_save_ability && effect.start_of_turn_save_dc)) {
          continue;
        }
        const save = window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow(
          member.state, effect.start_of_turn_save_ability, effect.start_of_turn_save_dc,
          { effect_tags: ["spell"], roundNumber: round },
        );
        if (!save.succeeded) continue;
        T().removeEffect(member.state, effect);
        for (const source of members(setup)) {
          const concentration = source.state.concentration;
          if (!concentration) continue;
          if (concentration.source_id === effect.source_id && concentration.effect_id === effect.source_effect_id) {
            C().end(source.state, states);
          }
        }
      }
      // Grapple-linked ticks exist only while the owner relationship exists.
      for (const grapple of [...(member.state.grapple_sources || [])]) {
        const spec = grapple.periodic_damage;
        if (!spec || member.state.is_dead || !member.state.is_alive) continue;
        const grappler = members(setup).find((item) => item.combatant_id === grapple.source_id);
        if (!grappler || grappler.state.is_dead || grappler.state.is_unconscious
          || !grappler.state.is_alive || grappler.state.current_hp <= 0) continue;
        if (Math.abs(grappler.position_ft - member.position_ft) > grapple.range_ft) continue;
        const total = D().rollMany(spec.dice_count, spec.dice_size).reduce((sum, roll) => sum + roll, 0);
        const hpBefore = member.state.current_hp;
        const resolved = DD().resolveDamage(member.state, total, spec.damage_type);
        A().applyDamage(member.state, resolved.applied, false, [spec.damage_type], states, setup);
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: member.combatant_id, actor_name: member.state.template.name,
          target_id: member.combatant_id, target_name: member.state.template.name,
          feature_id: spec.source_name, hp_before: hpBefore, hp_after: member.state.current_hp,
          animation: "feature",
          description: `${spec.source_name} deals ${resolved.applied} ${spec.damage_type} damage to ${member.state.template.name} at the start of the turn.`,
        });
      }
      for (const effect of [...(member.state.timed_effects || [])]) {
        const hpLossCount = effect.start_of_turn_hp_loss_dice_count || 0;
        if (hpLossCount > 0 && member.state.current_hp > 0 && !member.state.is_dead) {
          let totalLoss = 0;
          for (let index = 0; index < hpLossCount; index += 1) {
            totalLoss += D().roll(effect.start_of_turn_hp_loss_dice_size || 10);
          }
          const hpBefore = member.state.current_hp;
          const lost = loseHitPoints(member.state, totalLoss, states);
          const name = effect.source_effect_id || effect.effect_id;
          events.push({
            sequence: sequence++, round_number: round, event_type: "feature",
            actor_id: member.combatant_id, actor_name: member.state.template.name,
            target_id: member.combatant_id, target_name: member.state.template.name,
            feature_id: name, hp_before: hpBefore, hp_after: member.state.current_hp,
            is_dead: member.state.is_dead, animation: "feature",
            description: `${member.state.template.name} loses ${lost} Hit Points from ${name} at the start of the turn (not damage).`,
          });
        }
      }
      return { events, sequence };
    } catch (error) {
      console.error("Start-of-turn timed burn failed.", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_START_OF_TURN_TIMED_BURN = { resolve, loseHitPoints, applyOrStackHpLoss };
})();
