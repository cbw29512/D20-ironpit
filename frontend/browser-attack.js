(() => {
  "use strict";
  const S = () => window.IRON_PIT_BROWSER_STATE, R = () => window.IRON_PIT_BROWSER_ROLLS;
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE, T = () => window.IRON_PIT_BROWSER_TIMED, Z = () => window.IRON_PIT_BROWSER_ZERO_HP; const HC = () => window.IRON_PIT_BROWSER_HIT_CONTROL || { resolve: () => ({ applied: [], saveRoll: null, saveAbility: null, saveDc: null, saveSucceeded: null }) };
  const SAP = () => window.IRON_PIT_BROWSER_SAP || { applyWeapon: () => false, consume: () => 0, disadvantage: () => 0 };
  const TM = () => window.IRON_PIT_BROWSER_TACTICAL_MASTER || { apply: () => false };
  const GRZ = () => window.IRON_PIT_BROWSER_GRAZE || { rawDamage: () => null };
  const TOP = () => window.IRON_PIT_BROWSER_TOPPLE || { resolve: () => ({ saveRoll: null, saveDc: null, saveSucceeded: null, applied: false }) };
  const STUDY = () => window.IRON_PIT_BROWSER_STUDIED_ATTACKS || { apply: () => false };
  const HI = () => window.IRON_PIT_BROWSER_HEROIC_INSPIRATION || { rerollFailedAttack: (_state, roll) => ({ roll, used: false }) };
  const B2 = () => window.IRON_PIT_BROWSER_BARBARIAN2 || { activate: () => false, attackAdvantage: () => 0, attacksAgainstAdvantage: () => 0 };
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS || {
    attacksAgainstAdvantage: () => 0, consumeAttacksAgainstAdvantage: () => 0, nextAttackAgainstAdvantage: () => 0,
    consumeNextAttackAgainstAdvantage: () => 0, effectiveArmorClass: (state) => state.template.armor_class,
    effectiveSpeed: (state) => state.template.speed_ft, applyD20Bonus: (_state, _kind, roll) => roll,
  };
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || {
    attackAdvantage: (state) => state.is_unconscious, autoCritical: (state) => state.is_unconscious,
    has: (state, id) => state.active_effect_ids.includes(id), incapacitated: (state) => state.is_unconscious,
  };
  const E = () => window.IRON_PIT_ACTION_ECONOMY || { available: (state, cost) => cost === "action" && state.action_available, spend: (state) => { state.action_available = false; } };
  const states = (setup) => setup ? [...setup.heroes, ...setup.monsters].map((member) => member.state) : [];
  function conditionSources(attacker, defender, distance, targetId) {
    let advantage = M().attacksAgainstAdvantage(defender) + B2().attacksAgainstAdvantage(defender), disadvantage = 0;
    if (Q().has(attacker, "blinded")) disadvantage += 1;
    if (attacker.active_effect_ids.includes("prone")) disadvantage += 1;
    if (attacker.active_effect_ids.includes("restrained")) disadvantage += 1;
    if (attacker.active_effect_ids.includes("poisoned")) disadvantage += 1;
    disadvantage += G()?.attackDisadvantage(attacker, targetId) || 0;
    if (defender.active_effect_ids.includes("dodge") && !Q().incapacitated(defender) && M().effectiveSpeed(defender) > 0 && !G()?.speedIsZero(defender)) disadvantage += 1;
    if (Q().attackAdvantage(defender)) advantage += 1;
    if (defender.active_effect_ids.includes("restrained")) advantage += 1;
    if (defender.active_effect_ids.includes("prone")) distance <= 5 ? advantage += 1 : disadvantage += 1;
    return { advantage, disadvantage };
  }
  function rangedCloseThreat(attacker, target, distance, setup) {
    if (distance > 5 && !setup) return false;
    if (!setup) return distance <= 5 && !Q().incapacitated(target.state);
    const enemies = attacker.side === "heroes" ? setup.monsters : setup.heroes;
    return enemies.some((enemy) => enemy.state.is_alive && !enemy.state.is_dead && enemy.state.current_hp > 0 && !Q().incapacitated(enemy.state) && S().distance(attacker, enemy) <= 5);
  }
  const bloodiedFury = (state, attack) => state.template.traits?.includes("bloodied-fury") && attack.kind === "melee" && state.current_hp * 2 <= state.template.max_hp ? 1 : 0;
  function adjustedDamage(target, amount, type, allowVulnerability = true) {
    if (target.template.damage_immunities?.includes(type)) return 0;
    let value = amount;
    if (target.template.damage_resistances?.includes(type) || target.temporary_damage_resistances?.includes(type) || Q().has(target, "petrified")) value = Math.floor(value / 2);
    if (allowVulnerability && target.template.damage_vulnerabilities?.includes(type)) value *= 2;
    return value;
  }
  function applyDamage(state, amount, critical = false, damageTypes = [], affectedStates = []) {
    const lifecycle = Z(); if (!lifecycle) throw new Error("Browser zero-HP runtime is not loaded.");
    return lifecycle.applyDamage(state, amount, critical, damageTypes, affectedStates);
  }
  function resolveAttack(sequence, round, attacker, target, attack, distance, extra = {}) {
    const spendAction = extra.spendAction !== false;
    if (spendAction && !E().available(attacker.state, "action")) throw new Error("Action is unavailable for attack.");
    const recklessStarted = extra.allowReckless === true && B2().activate(attacker, attack, round);
    if (recklessStarted) window.IRON_PIT_BROWSER_BARBARIAN3?.markRecklessUse(attacker.state, extra.turnKey);
    const conditions = conditionSources(attacker.state, target.state, distance, target.combatant_id);
    const advantage = (extra.advantage || 0) + conditions.advantage + bloodiedFury(attacker.state, attack)
      + (attack.advantageIfTargetMissingHp && target.state.current_hp < S().effectiveMaxHp(target.state) ? 1 : 0) + B2().attackAdvantage(attacker.state, attack) + M().nextAttackAgainstAdvantage(attacker.state, target.combatant_id);
    const closeThreat = attack.kind === "ranged" && rangedCloseThreat(attacker, target, distance, extra.setup);
    const mode = R().attackMode(attack, distance, advantage, conditions.disadvantage + SAP().disadvantage(attacker.state), closeThreat);
    const heroic = HI().rerollFailedAttack(attacker.state, R().d20(attack.bonus, mode), M().effectiveArmorClass(target.state));
    const attackRoll = M().applyD20Bonus(attacker.state, "attack-roll-bonus-die", heroic.roll);
    M().consumeNextAttackAgainstAdvantage(attacker.state, target.combatant_id); SAP().consume(attacker.state);
    M().consumeAttacksAgainstAdvantage(target.state); window.IRON_PIT_BROWSER_RAGE?.extendFromAttack(attacker.state, round);
    if (spendAction) E().spend(attacker.state, "action");
    const redirected = window.IRON_PIT_BROWSER_REACTIONS?.redirectAttack?.(target, extra.setup) || null, actualTarget = redirected || target;
    const natural = attackRoll.selected_roll, naturalTwenty = natural === 20, baseTargetAc = M().effectiveArmorClass(actualTarget.state);
    const initialHit = natural !== 1 && (naturalTwenty || attackRoll.total >= baseTargetAc);
    const parry = window.IRON_PIT_BROWSER_REACTIONS?.parryHit?.(actualTarget.state, attack, attackRoll, initialHit, baseTargetAc) || { hit: initialHit, used: false };
    const turnKey = extra.turnKey || `${round}:${attacker.combatant_id}`, prowessUsed = !parry.hit && Boolean(attacker.state.template.combat_prowess) && attacker.state.feature_last_turn_keys["boon-combat-prowess"] !== turnKey; if (prowessUsed) attacker.state.feature_last_turn_keys["boon-combat-prowess"] = turnKey; const hit = parry.hit || prowessUsed, targetAc = baseTargetAc + (parry.used ? actualTarget.state.template.parry_reaction.ac_bonus : 0);
    const expandedCritical = natural >= (attacker.state.template.critical_hit_minimum || 20);
    const critical = Boolean(hit && (expandedCritical || (Q().autoCritical(actualTarget.state) && distance <= 5)));
    const hpBefore = actualTarget.state.current_hp, temporaryHpBefore = actualTarget.state.temporary_hp;
    const deathSuccessBefore = actualTarget.state.death_save_successes, deathFailureBefore = actualTarget.state.death_save_failures;
    const concentrationBefore = actualTarget.state.concentration?.effect_id || null;
    let damageRoll = null, damageComponents = [], damageOutcome = null, sapApplied = "", vexApplied = false, studiedApplied = false;
    let topple = { saveRoll: null, saveDc: null, saveSucceeded: null, applied: false }, controlSave = { applied: [], saveRoll: null, saveAbility: null, saveDc: null, saveSucceeded: null }; const applied = [];
    if (hit) {
      const damage = R().weaponDamage(attacker.state, attack, critical, mode, turnKey,
        extra.bonusDamage || null, actualTarget.state, window.IRON_PIT_BROWSER_SNEAK_ATTACK?.allyAvailable(attacker, extra.setup) || false, attacker.combatant_id);
      damageComponents = damage.components.map((part) => ({ ...part, applied_total: adjustedDamage(actualTarget.state, part.total, part.damage_type) }));
      damageRoll = { ...damage.roll, total: damageComponents.reduce((sum, part) => sum + part.applied_total, 0) };
      const appliedTypes = [...new Set(damageComponents.filter((part) => part.applied_total > 0).map((part) => part.damage_type))], affectedStates = states(extra.setup);
      damageOutcome = applyDamage(actualTarget.state, damageRoll.total, critical, appliedTypes, affectedStates);
      if (attack.maxHpReduction) Z().applyAttackMaxHpReduction(actualTarget.state, attack, damageComponents);
      const living = actualTarget.state.is_alive && !actualTarget.state.is_dead, proneMax = extra.proneMaxSize || attack.proneMaxSize;
      if (living && S().canProne(actualTarget, proneMax) && !I().immune(actualTarget.state, "prone")) { if (!actualTarget.state.active_effect_ids.includes("prone")) actualTarget.state.active_effect_ids.push("prone"); applied.push("prone"); }
      const control = attack.controlEffect;
      if (living && control?.grappleEscapeDc && (!control.maxTargetSize || S().sizeAtMost(actualTarget, control.maxTargetSize))) applied.push(...G().apply(actualTarget.state, attacker.combatant_id, control.grappleEscapeDc, attack.reach || 5, Boolean(control.restrainsWhileGrappled), Boolean(control.grappleEscapeCheckDisadvantage)));
      if (living && control?.conditionId && !control.initialSaveAbility) {
        const timed = T().apply(actualTarget.state, control.conditionId, attacker.combatant_id, { sourceEffectId: attack.id, appliedRound: round,
          expiresAtStartOfSourceTurn: Boolean(control.expiresAtStartOfSourceTurn), expiryTiming: control.expiryTiming || null,
          repeatSaveAbility: control.repeatSaveAbility || null, repeatSaveDc: control.repeatSaveDc || null,
          repeatSaveTiming: control.repeatSaveTiming || null, allowedRemovalActionIds: control.allowedRemovalActionIds || [] });
        if (timed) applied.push(timed);
      }
      if (living && control?.initialSaveAbility) { controlSave = HC().resolve(attack, attacker, actualTarget, round); applied.push(...controlSave.applied); }
      if (living) M().applyHitEffects?.(actualTarget.state, attacker.combatant_id, attack);
      topple = TOP().resolve(attacker, actualTarget, attack); if (topple.applied && !applied.includes("prone")) applied.push("prone");
      if (living) sapApplied = SAP().applyWeapon(attacker, actualTarget, attack, round) ? "weapon" : TM().apply(attacker, actualTarget, attack, round) ? "tactical" : "";
      vexApplied = window.IRON_PIT_BROWSER_VEX?.apply(attacker.state, attacker.combatant_id, actualTarget.combatant_id, attack, round, damageRoll.total) || false;
      window.IRON_PIT_BROWSER_RAGE?.endIfIncapacitated(actualTarget.state); C()?.endIfIncapacitated(actualTarget.state, affectedStates);
    } else {
      const rawGraze = GRZ().rawDamage(attacker.state, attack);
      if (rawGraze !== null) {
        const appliedTotal = adjustedDamage(actualTarget.state, rawGraze, attack.damageType, false);
        damageComponents = [{ source: `${attack.name} (Graze)`, notation: String(rawGraze), rolls: [], modifier: 0,
          damage_type: attack.damageType, total: rawGraze, applied_total: appliedTotal }];
        damageRoll = { notation: String(rawGraze), rolls: [], modifier: 0, selected_roll: null, mode: "normal", total: appliedTotal };
        const affectedStates = states(extra.setup), appliedTypes = appliedTotal > 0 ? [attack.damageType] : [];
        damageOutcome = applyDamage(actualTarget.state, appliedTotal, false, appliedTypes, affectedStates);
        window.IRON_PIT_BROWSER_RAGE?.endIfIncapacitated(actualTarget.state); C()?.endIfIncapacitated(actualTarget.state, affectedStates);
      }
      studiedApplied = STUDY().apply(attacker.state, attacker.combatant_id, target.combatant_id, round);
    }
    let description = `${attacker.state.template.name}: ${critical ? "CRITICAL HIT" : hit ? "HIT" : "MISS"} with ${attack.name}.`;
    if (heroic.used) description += " Heroic Inspiration rerolls one d20.";
    if (!hit && damageRoll !== null) description += ` Graze deals ${damageRoll.total} ${attack.damageType} damage.`;
    if (studiedApplied) description += ` Studied Attacks primes the next attack against ${target.state.template.name}.`;
    if (recklessStarted) description += ` ${attacker.state.template.name} uses Reckless Attack.`;
    if (redirected) description += ` ${target.state.template.name} uses Redirect Attack; ${actualTarget.state.template.name} becomes the target.`;
    if (parry.used) description += ` ${actualTarget.state.template.name} uses Parry.`; if (prowessUsed) description += ` ${attacker.state.template.name} uses Boon of Combat Prowess to turn the miss into a hit.`;
    if (sapApplied === "weapon") description += ` Sap mastery affects ${actualTarget.state.template.name}.`;
    if (sapApplied === "tactical") description += ` Tactical Master applies Sap to ${actualTarget.state.template.name}.`;
    if (vexApplied) description += ` Vex primes the next attack against ${actualTarget.state.template.name}.`;
    if (controlSave.saveDc !== null) description += ` ${actualTarget.state.template.name} ${controlSave.saveSucceeded ? "succeeds" : "fails"} the ${controlSave.saveAbility} save against ${attack.name}.`;
    if (topple.saveDc !== null) description += ` Topple save DC ${topple.saveDc}: ${actualTarget.state.template.name} ${topple.saveSucceeded ? "succeeds" : "fails"}.`;
    if (damageOutcome === "relentless_endurance") description += ` ${actualTarget.state.template.name} uses Relentless Endurance and remains at 1 HP.`;
    if (damageOutcome === "undead_fortitude") description += ` ${actualTarget.state.template.name} succeeds on Undead Fortitude and remains at 1 HP.`;
    for (const condition of ["prone", "grappled", "restrained", "poisoned", "paralyzed"]) if (applied.includes(condition)) description += ` ${actualTarget.state.template.name} is ${condition === "prone" ? "knocked Prone" : condition[0].toUpperCase() + condition.slice(1)}.`;
    const saveRoll = controlSave.saveRoll || topple.saveRoll, saveDc = controlSave.saveDc || topple.saveDc;
    const saveAbility = controlSave.saveAbility || (topple.saveDc === null ? null : "constitution"), saveSucceeded = controlSave.saveDc !== null ? controlSave.saveSucceeded : topple.saveSucceeded;
    const event = { sequence, round_number: round, event_type: "attack", actor_id: attacker.combatant_id, actor_name: attacker.state.template.name,
      target_id: actualTarget.combatant_id, target_name: actualTarget.state.template.name, attack_name: attack.name, target_ac: targetAc,
      attack_roll: attackRoll, saving_throw_roll: saveRoll, save_ability: saveAbility, save_dc: saveDc, save_succeeded: saveSucceeded,
      damage_roll: damageRoll, damage_components: damageComponents, applied_condition_ids: [...new Set(applied)], hit, critical,
      hp_before: hpBefore, hp_after: actualTarget.state.current_hp, temporary_hp_before: temporaryHpBefore, temporary_hp_after: actualTarget.state.temporary_hp,
      death_save_successes_before: deathSuccessBefore, death_save_failures_before: deathFailureBefore, death_save_successes: actualTarget.state.death_save_successes,
      death_save_failures: actualTarget.state.death_save_failures, is_stable: actualTarget.state.is_stable, is_dead: actualTarget.state.is_dead, weapon_id: attack.id, projectile: attack.projectile || null,
      feature_id: extra.featureId || (prowessUsed ? "boon-combat-prowess" : recklessStarted ? "reckless-attack" : null), concentration_ended_effect_id: concentrationBefore && !actualTarget.state.concentration ? concentrationBefore : null,
      animation: attack.animation || (attack.kind === "ranged" ? "projectile" : "slash"), description };
    return window.IRON_PIT_BROWSER_CHAMPION?.criticalMove(attacker, extra.setup, event) || event;
  }
  window.IRON_PIT_BROWSER_ATTACK = { adjustedDamage, applyDamage, conditionSources, rangedCloseThreat, resolveAttack };
})();