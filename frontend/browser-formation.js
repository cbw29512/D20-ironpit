(() => {
  "use strict";

  const HERO_BACK = 0, HERO_FRONT = 5, MONSTER_FRONT = 10, MONSTER_BACK = 15;
  const S = () => window.IRON_PIT_BROWSER_STATE, RES = () => window.IRON_PIT_BROWSER_RESOURCES;
  const SW = () => window.IRON_PIT_BROWSER_SWALLOW, AT = () => window.IRON_PIT_BROWSER_ATTACHMENTS;
  const attacks = (template) => template?.attacks || [];
  const alive = (member) => member.state.is_alive && !member.state.is_dead && member.state.current_hp > 0;

  function hasRangedWeaponOffense(template) { return attacks(template).some((attack) => ["ranged", "melee_or_ranged"].includes(attack.kind) && Number.isFinite(attack.long) && attack.long > 5); }
  function primaryWeaponIsRanged(template) { const primary = attacks(template).find((attack) => attack.id === template?.primary_attack_id) || attacks(template)[0]; return ["ranged", "melee_or_ranged"].includes(primary?.kind) && Number.isFinite(primary.long) && primary.long > 5; }
  function hasRangedSpellOffense(template) { if ((template?.spell_attack_actions || []).some((action) => action.attackKind === "ranged" && (action.range || 0) > 5)) return true; return (template?.spell_save_actions || []).some((action) => (action.range || 0) > 5); }
  function hasTrueRangeOffense(template) { return hasRangedWeaponOffense(template) || hasRangedSpellOffense(template); }
  function usesBackline(template) { return primaryWeaponIsRanged(template) || hasRangedSpellOffense(template); }
  function isBackline(member) { return usesBackline(member.state.template); }
  function startingPosition(template, side) { const back = usesBackline(template); if (side === "heroes") return back ? HERO_BACK : HERO_FRONT; if (side === "monsters") return back ? MONSTER_BACK : MONSTER_FRONT; throw new Error(`Unknown encounter side: ${side}`); }
  function enemies(member, setup) { return member.side === "heroes" ? setup.monsters : setup.heroes; }
  function livingTargets(member, setup) { const pool = enemies(member, setup), active = pool.filter(alive); if (active.length) return active; return pool.filter((target) => target.state.template.kind === "character" && target.state.is_alive && !target.state.is_dead && target.state.current_hp === 0); }
  function targetOrder(member, setup, preferBackline = false) { const targets = livingTargets(member, setup), front = targets.filter((target) => !isBackline(target)), back = targets.filter(isBackline); return preferBackline ? [...back, ...front] : [...front, ...back]; }
  function hasFrontlineTarget(member, setup) { return livingTargets(member, setup).some((target) => !isBackline(target)); }
  function hasBacklineTarget(member, setup) { return livingTargets(member, setup).some(isBackline); }
  function alliedFrontlineActive(member, setup) { const allies = member.side === "heroes" ? setup.heroes : setup.monsters; return allies.some((ally) => ally !== member && alive(ally) && !isBackline(ally)); }
  function targetAllowed(member, target, attack) { if (!attack.forbidSelfGrappledTarget) return true; return !target.state.grapple_sources.some((source) => source.source_id === member.combatant_id); }
  function attackDistance(member, target) { return S().distance(member, target); }
  function saveDistance(member, target, range) { if (range < 0) throw new Error("Save-action range cannot be negative."); return S().distance(member, target); }
  function attackInRange(attack, distance) { if (attack.kind === "melee") return distance <= (attack.reach || 5); if (attack.kind === "melee_or_ranged" && distance <= (attack.reach || 5)) return true; return Number.isFinite(attack.long) && distance <= attack.long; }
  function chooseAttack(member, setup, ids, kind = null, preferBackline = false) {
    const allowed = new Set(ids), forbidden = SW()?.forbiddenAttacks(member, setup) || new Set();
    const profiles = attacks(member.state.template).filter((attack) => allowed.has(attack.id) && !forbidden.has(attack.id)
      && (AT()?.attackAvailable(member.state, attack) ?? true)
      && (!kind || attack.kind === kind || attack.kind === "melee_or_ranged")
      && (!attack.resourceId || RES().available(member.state, attack.resourceId, attack.resourceCost || 1)));
    for (const target of targetOrder(member, setup, preferBackline)) {
      const distance = attackDistance(member, target), attack = profiles.find((profile) => targetAllowed(member, target, profile) && attackInRange(profile, distance));
      if (attack) return { target, attack, distance };
    }
    return null;
  }
  function rechargeAttackIds(member) { const definitions = member.state.template.resourceDefinitions || {}; return attacks(member.state.template).filter((attack) => attack.resourceId && definitions[attack.resourceId]?.recharge).map((attack) => attack.id); }
  function chooseRechargeAttack(member, setup) { return chooseAttack(member, setup, rechargeAttackIds(member)); }
  function chooseStandardAttack(member, setup) {
    const ids = attacks(member.state.template).map((attack) => attack.id), recharge = chooseRechargeAttack(member, setup);
    if (recharge) return recharge;
    if (isBackline(member) && alliedFrontlineActive(member, setup)) { const ranged = chooseAttack(member, setup, ids, "ranged"); if (ranged) return ranged; }
    return chooseAttack(member, setup, ids, "melee") || chooseAttack(member, setup, ids, "ranged");
  }
  function flexibleSlotHasBoth(member, ids) { const allowed = new Set(ids), kinds = new Set(attacks(member.state.template).filter((a) => allowed.has(a.id) && (AT()?.attackAvailable(member.state, a) ?? true)).map((a) => a.kind)); return kinds.has("melee_or_ranged") || (kinds.has("melee") && kinds.has("ranged")); }
  function backlineHoldsPosition(member, setup) { return isBackline(member) && alliedFrontlineActive(member, setup) && hasRangedWeaponOffense(member.state.template); }

  window.IRON_PIT_BROWSER_FORMATION = { hasRangedWeaponOffense, hasTrueRangeOffense, usesBackline, isBackline, startingPosition,
    targetOrder, hasFrontlineTarget, hasBacklineTarget, alliedFrontlineActive, targetAllowed,
    attackDistance, saveDistance, chooseAttack, chooseRechargeAttack, chooseStandardAttack,
    flexibleSlotHasBoth, backlineHoldsPosition };
})();