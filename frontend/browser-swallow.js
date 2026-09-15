(() => {
  "use strict";
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const DT = () => window.IRON_PIT_BROWSER_DEATH_TRIGGERS || { resolvePending: (sequence) => ({ events: [], sequence }) };
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const D = () => window.IRON_PIT_DICE;

  const members = (setup) => [...setup.heroes, ...setup.monsters];
  const opponents = (member, setup) => member.side === "heroes" ? setup.monsters : setup.heroes;
  const swallowedBy = (member, setup) => members(setup).filter((item) => item.state.swallowed?.source_id === member.combatant_id);
  const attackById = (member, id) => member.state.template.attacks.find((attack) => attack.id === id);
  function flush(events, sequence, round, setup) {
    const result = DT().resolvePending(sequence, round, setup); events.push(...result.events); return result.sequence;
  }
  function capacityAvailable(member, setup, action) {
    return action.maxSwallowed == null || swallowedBy(member, setup).length < action.maxSwallowed;
  }
  function applySwallowed(member, victim, action, event) {
    G().release(victim.state, member.combatant_id);
    victim.state.swallowed = {
      source_id: member.combatant_id, source_effect_id: action.id,
      damageDiceCount: action.damageDiceCount, damageDiceSize: action.damageDiceSize,
      damageBonus: action.damageBonus || 0, damageType: action.damageType,
      regurgitationDamageThreshold: action.regurgitationDamageThreshold ?? null,
      regurgitationSaveAbility: action.regurgitationSaveAbility || null,
      regurgitationSaveDc: action.regurgitationSaveDc ?? null,
      regurgitationRangeFt: action.regurgitationRangeFt ?? null,
      exitMovementFt: action.exitMovementFt || 0, exitProne: action.exitProne !== false,
      sourceDead: false,
    };
    event.applied_condition_ids = [...new Set([...(event.applied_condition_ids || []), "blinded", "restrained", "swallowed"])];
    event.feature_id = action.id;
    event.description += ` ${victim.state.template.name} is swallowed.`;
  }

  function target(member, setup) {
    const action = member.state.template.swallowAction;
    const attack = action ? attackById(member, action.attackId) : null;
    if (!action || action.requiresExistingGrapple === false || attack?.onHitSaveEffect?.swallowOnFailure) return null;
    if (!capacityAvailable(member, setup, action)) return null;
    return opponents(member, setup).find((candidate) =>
      candidate.state.current_hp > 0 && !candidate.state.is_dead
      && candidate.state.grapple_sources.some((source) => source.source_id === member.combatant_id)
      && S().sizeAtMost(candidate, action.maxTargetSize)) || null;
  }

  function resolve(sequence, round, member, setup) {
    const action = member.state.template.swallowAction, victim = target(member, setup);
    if (!action || !victim) return null;
    const attack = attackById(member, action.attackId);
    if (!attack) throw new Error(`${member.state.template.name} Swallow references missing attack ${action.attackId}.`);
    const event = A().resolveAttack(sequence++, round, member, victim, attack, 5, { setup });
    const events = [event];
    sequence = flush(events, sequence, round, setup);
    if (member.state.is_dead || member.state.turn_terminated) return { events, sequence };
    if (event.hit && victim.state.current_hp > 0 && !victim.state.is_dead) applySwallowed(member, victim, action, event);
    return { events, sequence };
  }

  function applyOnHit(member, victim, attack, event, setup) {
    const action = member.state.template.swallowAction, effect = attack.onHitSaveEffect;
    if (!setup || !action || action.attackId !== attack.id || !effect?.swallowOnFailure) return false;
    if (action.requiresExistingGrapple !== false || event.save_succeeded !== false) return false;
    if (!event.hit || victim.state.current_hp <= 0 || victim.state.is_dead || victim.state.swallowed) return false;
    if (!S().sizeAtMost(victim, action.maxTargetSize) || !capacityAvailable(member, setup, action)) return false;
    applySwallowed(member, victim, action, event);
    return true;
  }

  function cleanup(setup) {
    const byId = new Map(members(setup).map((member) => [member.combatant_id, member]));
    for (const victim of members(setup)) {
      const swallowed = victim.state.swallowed;
      if (!swallowed) continue;
      const source = byId.get(swallowed.source_id);
      if (source && source.state.is_alive && !source.state.is_dead) continue;
      victim.state.swallowed = null;
      if (swallowed.exitProne !== false && !victim.state.active_effect_ids.includes("prone")) victim.state.active_effect_ids.push("prone");
    }
  }

  function startTurn(sequence, round, member, setup) {
    const events = [];
    for (const victim of swallowedBy(member, setup)) {
      const swallowed = victim.state.swallowed;
      const rolls = D().rollMany(swallowed.damageDiceCount, swallowed.damageDiceSize);
      const raw = rolls.reduce((sum, roll) => sum + roll, 0) + (swallowed.damageBonus || 0);
      const applied = A().adjustedDamage(victim.state, raw, swallowed.damageType);
      const hpBefore = victim.state.current_hp;
      A().applyDamage(victim.state, applied, false, [swallowed.damageType], members(setup).map((item) => item.state));
      events.push({
        sequence: sequence++, round_number: round, event_type: "feature",
        actor_id: member.combatant_id, actor_name: member.state.template.name,
        target_id: victim.combatant_id, target_name: victim.state.template.name,
        feature_id: "swallow", damage_roll: {
          notation: `${swallowed.damageDiceCount}d${swallowed.damageDiceSize}+${swallowed.damageBonus || 0}`,
          rolls, modifier: swallowed.damageBonus || 0, total: applied,
        }, hp_before: hpBefore, hp_after: victim.state.current_hp, animation: "damage",
        description: `${victim.state.template.name} takes ${applied} ${swallowed.damageType} damage while swallowed.`,
      });
      sequence = flush(events, sequence, round, setup);
      if (member.state.is_dead) break;
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_SWALLOW = { applyOnHit, cleanup, resolve, startTurn, target };
})();
