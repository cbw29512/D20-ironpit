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
      || target.swallowed
      || (action.maxSwallowed != null && (owner.swallowed_target_ids || []).length >= action.maxSwallowed))
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
      damage_bonus: action.damageBonus || 0,
      start_turn_save_ability: action.startTurnSaveAbility || null,
      start_turn_save_dc: action.startTurnSaveDc || null,
      exit_prone: action.exitProne !== false,
      cannot_breathe: Boolean(action.cannotBreathe),
      moves_with_source: Boolean(action.movesWithSource),
      exit_movement_ft: action.exitMovementFt,
      regurgitation_damage_threshold: action.regurgitationDamageThreshold || null,
      regurgitation_save_ability: action.regurgitationSaveAbility || null,
      regurgitation_save_dc: action.regurgitationSaveDc || null,
      regurgitation_range_ft: action.regurgitationRangeFt ?? null,
      regurgitation_all_swallowed: Boolean(action.regurgitationAllSwallowed),
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
          victim.state.swallowed.exit_prone !== false
          && victim.state.is_alive && !victim.state.is_dead && victim.state.current_hp > 0)) {
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
        let save = null;
        if (record.start_turn_save_dc != null) {
          const runtime = window.IRON_PIT_BROWSER_SAVING_THROWS;
          if (!runtime?.resolveSavingThrow || !record.start_turn_save_ability)
            throw new Error("Conditional containment requires source-owned saving throw runtime.");
          save = runtime.resolveSavingThrow(
            target.state, record.start_turn_save_ability, record.start_turn_save_dc,
            { roundNumber: round, encounterRoller: target, setup },
          );
          if (save.succeeded) {
            events.push({
              sequence: sequence++, round_number: round, event_type: "feature",
              actor_id: owner.combatant_id, actor_name: ownerState.template.name,
              target_id: target.combatant_id, target_name: target.state.template.name,
              feature_id: record.source_name, animation: "feature",
              saving_throw_roll: save.roll, save_ability: record.start_turn_save_ability,
              save_dc: record.start_turn_save_dc, save_succeeded: true,
              description: `${target.state.template.name} succeeds on the ${record.source_name} save at ${ownerState.template.name}\'s turn start; no damage.`,
            });
            continue;
          }
        }
        const rolls = D().rollMany(record.damage_dice_count, record.damage_dice_size);
        const total = rolls.reduce((sum, roll) => sum + roll, record.damage_bonus || 0);
        const hpBefore = target.state.current_hp;
        const resolved = DD().resolveDamage(target.state, total, record.damage_type);
        A().applyDamage(target.state, resolved.applied, false, [record.damage_type], affected, setup, [{
          source: record.source_name, damage_type: record.damage_type,
          notation: `${record.damage_dice_count}d${record.damage_dice_size}${record.damage_bonus ? `+${record.damage_bonus}` : ""}`,
          rolls, modifier: record.damage_bonus || 0, total, applied_total: resolved.applied,
        }], owner.combatant_id);
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: owner.combatant_id, actor_name: ownerState.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          feature_id: record.source_name, hp_before: hpBefore, hp_after: target.state.current_hp,
          saving_throw_roll: save?.roll || null,
          save_ability: record.start_turn_save_ability || null,
          save_dc: record.start_turn_save_dc || null,
          save_succeeded: save ? false : null,
          damage_components: [{
            source: record.source_name, damage_type: record.damage_type,
            notation: `${record.damage_dice_count}d${record.damage_dice_size}${record.damage_bonus ? `+${record.damage_bonus}` : ""}`,
            rolls, modifier: record.damage_bonus || 0, total, applied_total: resolved.applied,
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
  function sequenceHit(sequence, round, member, target, attack, events) {
    // All eligibility comes from the card, never the ability/creature name.
    try {
      if (!member.state.is_alive || member.state.is_dead
        || !target.state.is_alive || target.state.is_dead
        || target.state.current_hp <= 0 || target.state.swallowed) return null;
      for (const rule of member.state.template.swallowActions || []) {
        if (rule.deliveryMode !== "attack_sequence" || rule.attackId !== attack.id) continue;
        const size = SIZES.indexOf(target.state.template.size);
        const limit = SIZES.indexOf(rule.maxTargetSize);
        if (size < 0 || limit < 0) throw new Error("Containment requires certified sizes.");
        if (size > limit) continue;
        if (!Number.isInteger(rule.requiredSequenceHits) || rule.requiredSequenceHits < 2
          || !Number.isInteger(rule.sequenceGrappleDc))
          throw new Error("Containment requires an exact hit count and Grapple DC.");
        const hits = events.filter((event) =>
          event.event_type === "attack" && event.hit === true
          && event.actor_id === member.combatant_id && event.target_id === target.combatant_id
          && event.attack_id === rule.attackId).length;
        if (hits !== rule.requiredSequenceHits) continue;
        if (rule.maxSwallowed != null
          && member.state.swallowed_target_ids.length >= rule.maxSwallowed) continue;
        const grappled = GRAPPLE().apply(
          target.state, member.combatant_id, rule.sequenceGrappleDc, attack.reach || 5,
        );
        if (!grappled.includes("grappled")) continue;
        if (!swallowAfterBite(
          member.combatant_id, member.state, target.combatant_id,
          target.state, rule, true,
        )) throw new Error("A valid two-hit containment sequence failed.");
        return {
          sequence, round_number: round, event_type: "feature",
          actor_id: member.combatant_id, actor_name: member.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          feature_id: rule.sourceName, animation: "feature",
          applied_condition_ids: ["blinded", "restrained"],
          description: `${member.state.template.name}: ${rule.requiredSequenceHits} ${attack.name} hits `
            + `grapple ${target.state.template.name} (escape DC ${rule.sequenceGrappleDc}), `
            + `then ${rule.sourceName} contains the target: Blinded and Restrained.`
            + (rule.cannotBreathe ? " Unable to breathe." : ""),
        };
      }
      return null;
    } catch (error) {
      console.error("Generic same-target multi-hit containment failed.", {error});
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_SWALLOW = {
    swallowAfterBite, release, cleanup, sourceTurnDamage, sequenceHit,
  };
})();
