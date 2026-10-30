(() => {
  "use strict";
  const SIZES = ["tiny", "small", "medium", "large", "huge", "gargantuan"];
  const GRAPPLE = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || {immune:()=>false};
  const D = () => window.IRON_PIT_DICE;
  const DD = () => window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  function swallowAfterBite(ownerId, owner, targetId, target, action, hit) {
    if (!hit || !owner.is_alive || owner.is_dead || owner.current_hp <= 0
      || !target.is_alive || target.is_dead || target.current_hp <= 0
      || target.swallowed || (owner.swallowed_target_ids || []).length >= action.maxSwallowed)
      return false;
    if (SIZES.indexOf(target.template.size) < 0 || SIZES.indexOf(action.maxTargetSize) < 0)
      throw new Error("Swallow target or limit must have a certified size.");
    if (SIZES.indexOf(target.template.size) > SIZES.indexOf(action.maxTargetSize)) return false;
    if (action.requiresExistingGrapple && !(target.grapple_sources || []).some(g => g.source_id === ownerId))
      return false;
    if (!(owner.template.attacks || []).some(a => a.id === action.attackId))
      throw new Error("Swallow must reference its printed Bite attack.");
    if (!GRAPPLE()) throw new Error("Swallow requires shared grapple lifecycle.");
    GRAPPLE().release(target, ownerId);
    target.swallowed = {
      source_id: ownerId, source_name: action.sourceName,
      damage_dice_count: action.damageDiceCount,
      damage_dice_size: action.damageDiceSize, damage_type: action.damageType,
      exit_movement_ft: action.exitMovementFt,
    };
    (owner.swallowed_target_ids ||= []).push(targetId);
    target.active_effect_ids = (target.active_effect_ids || []).filter(c => c !== "dodge");
    for (const condition of ["blinded", "restrained"]) {
      if (!I().immune(target, condition) && !target.active_effect_ids.includes(condition))
        target.active_effect_ids.push(condition);
    }
    return true;
  }
  function release(ownerId, owner, targetId, target, exitingProne = true) {
    if (!target.swallowed || target.swallowed.source_id !== ownerId) return false;
    owner.swallowed_target_ids = (owner.swallowed_target_ids || []).filter(id => id !== targetId);
    target.swallowed = null;
    for (const condition of ["blinded", "restrained"]) {
      const ownedElsewhere = (target.timed_effects || []).some(effect => effect.effect_id === condition)
        || (condition === "restrained" && (target.grapple_sources || []).some(g => g.restrains));
      if (!ownedElsewhere) target.active_effect_ids = target.active_effect_ids.filter(c => c !== condition);
    }
    if (exitingProne && !I().immune(target, "prone")
      && !target.active_effect_ids.includes("prone")) target.active_effect_ids.push("prone");
    return true;
  }
  function cleanup(setup) {
    try {
      const members = new Map([...setup.heroes, ...setup.monsters].map(member => [member.combatant_id, member]));
      const released = [];
      for (const victim of members.values()) {
        const record = victim.state.swallowed;
        if (!record) continue;
        const owner = members.get(record.source_id);
        if (owner && owner.state.is_alive && !owner.state.is_dead && owner.state.current_hp > 0
          && victim.state.is_alive && !victim.state.is_dead) continue;
        if (!owner) throw new Error("Swallowed victim references an unknown encounter owner.");
        if (release(owner.combatant_id, owner.state, victim.combatant_id, victim.state,
          victim.state.is_alive && !victim.state.is_dead && victim.state.current_hp > 0)) {
          released.push(victim.combatant_id);
        }
      }
      return released;
    } catch (error) {
      console.error("Browser Swallow lifecycle cleanup failed.", {error});
      throw error;
    }
  }
  function sourceTurnDamage(sequence, round, owner, setup) {
    try {
      cleanup(setup);
      const events = [], ownerState = owner.state;
      if (!ownerState.is_alive || ownerState.is_dead || ownerState.current_hp <= 0) {
        return {events, sequence};
      }
      if (!D()?.rollMany || !DD()?.resolveDamage || !A()?.applyDamage) {
        throw new Error("Swallow source-turn damage requires dice and universal typed-damage runtimes.");
      }
      const members = [...setup.heroes, ...setup.monsters];
      const affected = members.map(item => item.state);
      for (const target of members) {
        const record = target.state.swallowed;
        if (!record || record.source_id !== owner.combatant_id
          || !target.state.is_alive || target.state.is_dead) continue;
        const rolls = D().rollMany(record.damage_dice_count, record.damage_dice_size);
        const total = rolls.reduce((sum, roll) => sum + roll, 0);
        const hpBefore = target.state.current_hp;
        const resolved = DD().resolveDamage(target.state, total, record.damage_type);
        A().applyDamage(target.state, resolved.applied, false, [record.damage_type], affected, setup, [{
          source: record.source_name, damage_type: record.damage_type,
          notation: `${record.damage_dice_count}d${record.damage_dice_size}`,
          rolls, modifier: 0, total, applied_total: resolved.applied,
        }], owner.combatant_id);
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: owner.combatant_id, actor_name: ownerState.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          feature_id: record.source_name, hp_before: hpBefore, hp_after: target.state.current_hp,
          damage_components: [{
            source: record.source_name, damage_type: record.damage_type,
            notation: `${record.damage_dice_count}d${record.damage_dice_size}`,
            rolls, modifier: 0, total, applied_total: resolved.applied,
          }],
          animation: "feature",
          description: `${ownerState.template.name}: ${record.source_name} deals ${resolved.applied} ${record.damage_type} damage to swallowed ${target.state.template.name} at the source's turn start.`,
        });
      }
      cleanup(setup);
      return {events, sequence};
    } catch (error) {
      console.error("Browser Swallow source-turn damage failed.", {owner: owner?.combatant_id, error});
      throw error;
    }
  }
  function choose(member, setup) {
    try {
      if (!window.IRON_PIT_ACTION_ECONOMY?.available(member.state, "action")) return null;
      for (const action of member.state.template.swallowActions || []) {
        if ((member.state.swallowed_target_ids || []).length >= action.maxSwallowed) continue;
        const attack = (member.state.template.attacks || []).find(a => a.id === action.attackId);
        if (!attack || attack.kind !== "melee") throw new Error("Swallow must reference a certified melee Bite.");
        const maxSize = SIZES.indexOf(action.maxTargetSize);
        if (maxSize < 0) throw new Error("Swallow has an uncertified target size.");
        const opponents = member.side === "heroes" ? setup.monsters : setup.heroes;
        for (const target of opponents) {
          const state = target.state;
          if (!state.is_alive || state.is_dead || state.current_hp <= 0 || state.swallowed) continue;
          if (SIZES.indexOf(state.template.size) < 0) throw new Error("Swallow target size is uncertified.");
          if (SIZES.indexOf(state.template.size) > maxSize) continue;
          if (action.requiresExistingGrapple && !(state.grapple_sources || []).some(g => g.source_id === member.combatant_id)) continue;
          const distance = window.IRON_PIT_BROWSER_STATE.distance(member, target);
          if (distance > (attack.reach || 5)) continue;
          return { action, attack, target, distance };
        }
      }
      return null;
    } catch (error) {
      console.error("Browser Swallow action discovery failed.", {combatant: member?.combatant_id, error});
      throw error;
    }
  }
  function resolve(sequence, round, member, setup, turnKey, targetId, attackId) {
    try {
      const chosen = choose(member, setup);
      if (!chosen || chosen.target.combatant_id !== targetId || chosen.action.attackId !== attackId)
        throw new Error("Swallow candidate is no longer legal.");
      const bite = {...chosen.attack, controlEffect: null, grappleTargetPolicy: "normal"};
      const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(
        sequence, round, member, chosen.target, bite, chosen.distance,
        {spendAction: true, setup, turnKey, featureId: "swallow"},
      );
      if (event.hit && swallowAfterBite(member.combatant_id, member.state, targetId,
        chosen.target.state, chosen.action, true)) {
        event.description += ` ${chosen.target.state.template.name} is swallowed: Blinded, Restrained, and protected by total external cover.`;
        event.applied_condition_ids = [...new Set([...(event.applied_condition_ids || []), "blinded", "restrained"])];
      }
      return {events: [event], sequence: sequence + 1};
    } catch (error) {
      console.error("Browser Swallow action resolution failed.", {combatant: member?.combatant_id, error});
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_SWALLOW = {
    swallowAfterBite, release, cleanup, sourceTurnDamage, choose, resolve,
  };
})();
