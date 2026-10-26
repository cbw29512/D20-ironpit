(() => {
  "use strict";
  const SIZES = ["tiny", "small", "medium", "large", "huge", "gargantuan"];
  const GRAPPLE = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || {immune:()=>false};
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
          && victim.state.is_alive && !victim.state.is_dead && victim.state.current_hp > 0) continue;
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
  window.IRON_PIT_BROWSER_SWALLOW = {swallowAfterBite, release, cleanup};
})();
