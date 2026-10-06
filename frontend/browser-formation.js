(() => {
  "use strict";
  const HERO_BACK = 0, HERO_FRONT = 5, MONSTER_FRONT = 10, MONSTER_BACK = 15;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const attacks = (template) => template?.attacks || [];
  const alive = (member) => member.state.is_alive && !member.state.is_dead && member.state.current_hp > 0
    && !window.IRON_PIT_BROWSER_EXILE?.removed(member.state);
  function hasRangedWeaponOffense(template) {
    return attacks(template).some((attack) => attack.kind === "ranged" && Number.isFinite(attack.long) && attack.long > 5);
  }
  function primaryWeaponIsRanged(template) {
    const primary = attacks(template).find((attack) => attack.id === template?.primary_attack_id) || attacks(template)[0];
    return primary?.kind === "ranged" && Number.isFinite(primary.long) && primary.long > 5;
  }
  function hasRangedSpellOffense(template) {
    if ((template?.spell_attack_actions || []).some((action) => action.attackKind === "ranged" && (action.range || 0) > 5)) return true;
    if ((template?.auto_hit_spell_actions || []).some((action) => (action.range || 0) > 5)) return true;
    return (template?.spell_save_actions || []).some((action) => (action.range || 0) > 5);
  }
  function hasTrueRangeOffense(template) { return hasRangedWeaponOffense(template) || hasRangedSpellOffense(template); }
  function usesBackline(template) { return primaryWeaponIsRanged(template) || hasRangedSpellOffense(template); }
  function isBackline(member) {
    const row = member.state.formation_row;
    if (row === "front") return false;
    if (row === "back") return true;
    return usesBackline(member.state.template);
  }
  function startingPosition(template, side) {
    const back = usesBackline(template);
    if (side === "heroes") return back ? HERO_BACK : HERO_FRONT;
    if (side === "monsters") return back ? MONSTER_BACK : MONSTER_FRONT;
    throw new Error(`Unknown encounter side: ${side}`);
  }
  function enemies(member, setup) { return member.side === "heroes" ? setup.monsters : setup.heroes; }
  function livingTargets(member, setup) {
    const pool = enemies(member, setup), active = pool.filter(alive);
    if (active.length) return active;
    return pool.filter((target) => target.state.template.kind === "character"
      && target.state.is_alive && !target.state.is_dead && target.state.current_hp === 0);
  }
  function targetOrder(member, setup, preferBackline = false) {
    const targets = livingTargets(member, setup);
    const front = targets.filter((target) => !isBackline(target));
    const back = targets.filter(isBackline);
    return preferBackline ? [...back, ...front] : [...front, ...back];
  }
  function alliedFrontlineActive(member, setup) {
    const allies = member.side === "heroes" ? setup.heroes : setup.monsters;
    return allies.some((ally) => ally !== member && alive(ally) && !isBackline(ally));
  }
  function targetAllowed(member, target, attack, setup = null) {
    try {
      const ownsTarget = (target.state.grapple_sources || []).some(
        (source) => source.source_id === member.combatant_id,
      );
      if (attack.forbidSelfGrappledTarget && ownsTarget) return false;
      const policy = attack.grappleTargetPolicy || "normal";
      if (policy === "normal") return true;
      if (!["own_grapple_only", "auto_hit_own_grapple"].includes(policy)) {
        throw new Error(`Unsupported grapple target policy: ${policy}`);
      }
      if (ownsTarget) return true;
      if (!setup) return true;
      return ![...setup.heroes, ...setup.monsters].some((candidate) =>
        (candidate.state.grapple_sources || []).some((source) => source.source_id === member.combatant_id),
      );
    } catch (error) {
      console.error("Failed browser attack target policy", { member: member?.combatant_id, target: target?.combatant_id, error });
      throw error;
    }
  }
  function automaticHit(member, target, attack) {
    return (attack.grappleTargetPolicy || "normal") === "auto_hit_own_grapple"
      && (target.state.grapple_sources || []).some(
        (source) => source.source_id === member.combatant_id,
      );
  }
  function attackDistance(member, target) {
    try {
      return S().distance(member, target);
    } catch (error) {
      console.error("Failed browser attack distance", { member: member.combatant_id, target: target.combatant_id, error });
      throw error;
    }
  }
  function saveDistance(member, target, range) {
    try {
      if (range < 0) throw new Error("Save-action range cannot be negative.");
      return S().distance(member, target);
    } catch (error) {
      console.error("Failed browser save-action distance", { member: member.combatant_id, target: target.combatant_id, error });
      throw error;
    }
  }
  function attackInRange(attack, distance) {
    try {
      if (attack.kind === "melee") return distance <= (attack.reach || 5);
      return Number.isFinite(attack.long) && distance <= attack.long;
    } catch (error) {
      console.error("Failed browser attack-range legality", { attack: attack.id, error });
      throw error;
    }
  }
  function weaponMeanDamage(attack) {
    return (attack.diceCount || 0) * ((attack.diceSize || 0) + 1) / 2 + (attack.damageBonus || 0);
  }
  function chooseAttack(member, setup, ids, kind = null, preferBackline = false) {
    const allowed = new Set(ids);
    const profiles = attacks(member.state.template).filter((attack) => allowed.has(attack.id) && (!kind || attack.kind === kind));
    for (const target of targetOrder(member, setup, preferBackline)) {
      const distance = attackDistance(member, target);
      const legal = profiles.filter((profile) => (!window.IRON_PIT_BROWSER_GRID_BARRIERS || window.IRON_PIT_BROWSER_GRID_BARRIERS.clearBetweenMembers(member, target, setup)) && targetAllowed(member, target, profile, setup) && attackInRange(profile, distance));
      if (legal.length) {
        legal.sort((a, b) => weaponMeanDamage(b) - weaponMeanDamage(a));
        return { target, attack: legal[0], distance };
      }
    }
    return null;
  }
  function meleeCanLandNow(member, setup) {
    return chooseStandardAttack(member, setup)?.attack.kind === "melee";
  }
  function chooseStandardAttack(member, setup) {
    const ids = attacks(member.state.template).map((attack) => attack.id);
    if (isBackline(member) && alliedFrontlineActive(member, setup)) {
      const ranged = chooseAttack(member, setup, ids, "ranged");
      if (ranged) return ranged;
    }
    return chooseAttack(member, setup, ids, "melee") || chooseAttack(member, setup, ids, "ranged");
  }
  function flexibleSlotHasBoth(member, ids) {
    const allowed = new Set(ids), kinds = new Set(attacks(member.state.template).filter((a) => allowed.has(a.id)).map((a) => a.kind));
    return kinds.has("melee") && kinds.has("ranged");
  }
  const flexibleAttackMode = (member, setup) => isBackline(member) && alliedFrontlineActive(member, setup) ? "ranged" : "melee";
  function chooseSlotAttack(member, setup, ids, mode = null) {
    try {
      // Select the permitted mode before damage scoring or actual resolution.
      if (flexibleSlotHasBoth(member, ids)) {
        const kind = mode || flexibleAttackMode(member, setup);
        return chooseAttack(member, setup, ids, kind);
      }
      return chooseAttack(member, setup, ids, "melee") || chooseAttack(member, setup, ids, "ranged");
    } catch (error) {
      console.error("Failed browser row-based attack choice", { id: member?.combatant_id, error });
      throw error;
    }
  }
  function backlineHoldsPosition(member, setup) {
    return isBackline(member) && alliedFrontlineActive(member, setup) && hasRangedWeaponOffense(member.state.template);
  }
  window.IRON_PIT_BROWSER_FORMATION = {
    hasRangedWeaponOffense, hasTrueRangeOffense, usesBackline, isBackline, startingPosition,
    targetOrder, alliedFrontlineActive, targetAllowed, automaticHit,
    attackDistance, saveDistance, weaponMeanDamage, chooseAttack, chooseStandardAttack, meleeCanLandNow,
    flexibleSlotHasBoth, flexibleAttackMode, chooseSlotAttack, backlineHoldsPosition,
  };
})();
