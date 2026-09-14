(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const D = () => window.IRON_PIT_DICE;
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;
  const members = (setup) => [...setup.heroes, ...setup.monsters];

  function matching(state, sourceId, attackId) {
    return (state.ongoing_damage_effects || []).find((item) => item.sourceId === sourceId && item.sourceEffectId === attackId) || null;
  }
  function shouldSkipSave(state, attack, sourceId) {
    const effect = attack.ongoingDamageEffect;
    return Boolean(effect && effect.applyOn === "failed_on_hit_save" && effect.stacksOnReapply && matching(state, sourceId, attack.id));
  }
  function applyOnHit(state, attack, sourceId, saveSucceeded = null) {
    const effect = attack.ongoingDamageEffect;
    if (!effect || state.is_dead || !state.is_alive) return false;
    const existing = matching(state, sourceId, attack.id);
    if (existing) {
      if (effect.stacksOnReapply) { existing.stacks += 1; return true; }
      return false;
    }
    if (effect.endsWhenGrappleSourceEnds && !(state.grapple_sources || []).some((source) => source.source_id === sourceId && source.source_effect_id === attack.id)) return false;
    if (effect.applyOn === "failed_on_hit_save" && saveSucceeded !== false) return false;
    state.ongoing_damage_effects = state.ongoing_damage_effects || [];
    state.ongoing_damage_effects.push({ sourceId, sourceEffectId: attack.id, effect: structuredClone(effect), stacks: 1 });
    return true;
  }
  function clearMagicalHealing(state) {
    const removed = (state.ongoing_damage_effects || []).filter((item) => item.effect.endsOnMagicalHealing).map((item) => item.effect.id);
    state.ongoing_damage_effects = (state.ongoing_damage_effects || []).filter((item) => !item.effect.endsOnMagicalHealing);
    return removed;
  }
  function cleanupOngoing(state) {
    state.ongoing_damage_effects = (state.ongoing_damage_effects || []).filter((item) =>
      !item.effect.endsWhenGrappleSourceEnds || (state.grapple_sources || []).some((source) => source.source_id === item.sourceId && source.source_effect_id === item.sourceEffectId));
  }
  function ongoingStartTurn(sequence, round, member, setup) {
    cleanupOngoing(member.state);
    const events = [], affected = members(setup).map((item) => item.state);
    for (const ongoing of member.state.ongoing_damage_effects || []) {
      const effect = ongoing.effect, count = effect.diceCount * ongoing.stacks;
      const rolls = D().rollMany(count, effect.diceSize), modifier = (effect.damageBonus || 0) * ongoing.stacks;
      const raw = Math.max(0, rolls.reduce((sum, roll) => sum + roll, 0) + modifier), before = member.state.current_hp;
      let applied = raw, components = [];
      if (!effect.damageType) Z().applyHitPointLoss(member.state, raw);
      else {
        applied = A().adjustedDamage(member.state, raw, effect.damageType, true, true);
        if (applied) A().applyDamage(member.state, applied, false, [effect.damageType], affected);
        components = [{ source: effect.name, notation: `${count}d${effect.diceSize}+${modifier}`, rolls, modifier,
          damage_type: effect.damageType, total: raw, applied_total: applied }];
      }
      const wording = !effect.damageType ? `loses ${applied} hit points` : `takes ${applied} ${effect.damageType} damage`;
      events.push({ sequence: sequence++, round_number: round, event_type: "feature", actor_id: ongoing.sourceId,
        actor_name: effect.name, target_id: member.combatant_id, target_name: member.state.template.name,
        feature_id: effect.id, damage_roll: { notation: `${count}d${effect.diceSize}+${modifier}`, rolls, modifier, total: applied },
        damage_components: components, hp_before: before, hp_after: member.state.current_hp, is_dead: member.state.is_dead,
        animation: "damage", description: `${member.state.template.name} ${wording} from ${effect.name}.` });
    }
    return { events, sequence };
  }

  function grapplers(source, setup) {
    const byId = Object.fromEntries(members(setup).map((member) => [member.combatant_id, member]));
    const ids = [...new Set((source.state.grapple_sources || []).map((item) => item.source_id))];
    return ids.map((id) => byId[id]).filter((member) => member && member.state.current_hp > 0 && !member.state.is_dead);
  }
  function startTurn(sequence, round, source, setup) {
    const events = [], affected = members(setup).map((member) => member.state);
    for (const profile of source.state.template.startTurnRelationshipDamage || []) {
      const targets = profile.targetRelationship === "grapplers" ? grapplers(source, setup) : [];
      for (const target of targets) {
        const rolls = D().rollMany(profile.diceCount, profile.diceSize);
        const raw = rolls.reduce((sum, roll) => sum + roll, 0) + (profile.damageBonus || 0), before = target.state.current_hp;
        const applied = A().adjustedDamage(target.state, raw, profile.damageType, true, true);
        if (applied) A().applyDamage(target.state, applied, false, [profile.damageType], affected);
        const notation = `${profile.diceCount}d${profile.diceSize}+${profile.damageBonus || 0}`;
        events.push({ sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: source.combatant_id, actor_name: source.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          feature_id: profile.id, damage_roll: { notation, rolls, modifier: profile.damageBonus || 0, total: applied },
          damage_components: [{ source: profile.name, notation, rolls, modifier: profile.damageBonus || 0,
            damage_type: profile.damageType, total: raw, applied_total: applied }], hp_before: before,
          hp_after: target.state.current_hp, animation: "damage",
          description: `${target.state.template.name} takes ${applied} ${profile.damageType} damage from ${source.state.template.name}'s ${profile.name}.` });
      }
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_START_TURN_DAMAGE = { applyOnHit, clearMagicalHealing, ongoingStartTurn, shouldSkipSave, startTurn };
})();
