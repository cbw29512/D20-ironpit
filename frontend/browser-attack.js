(() => {
  "use strict";
  const S = () => window.IRON_PIT_BROWSER_STATE, R = () => window.IRON_PIT_BROWSER_ROLLS;
  const H = () => window.IRON_PIT_BROWSER_ATTACK_HELPERS, CTRL = () => window.IRON_PIT_BROWSER_CONTROL;
  const SAP = () => window.IRON_PIT_BROWSER_SAP || { applyWeapon: () => false, consume: () => 0, disadvantage: () => 0 };
  const TM = () => window.IRON_PIT_BROWSER_TACTICAL_MASTER || { apply: () => false };
  const GRZ = () => window.IRON_PIT_BROWSER_GRAZE || { rawDamage: () => null };
  const TOP = () => window.IRON_PIT_BROWSER_TOPPLE || { resolve: () => ({ saveRoll: null, saveDc: null, saveSucceeded: null, applied: false }) };
  const STUDY = () => window.IRON_PIT_BROWSER_STUDIED_ATTACKS || { apply: () => false };
  const HI = () => window.IRON_PIT_BROWSER_HEROIC_INSPIRATION || { rerollFailedAttack: (_state, roll) => ({ roll, used: false }) };
  const B2 = () => window.IRON_PIT_BROWSER_BARBARIAN2 || { activate: () => false, attackAdvantage: () => 0 };
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS || {
    consumeAttacksAgainstAdvantage: () => 0, nextAttackAgainstAdvantage: () => 0, consumeNextAttackAgainstAdvantage: () => 0,
    nextAttackMadeDisadvantage: () => 0, consumeNextAttackMadeDisadvantage: () => 0,
    effectiveArmorClass: (state) => state.template.armor_class, applyD20Bonus: (_state, _kind, roll) => roll,
  };
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || {
    autoCritical: (state) => state.is_unconscious, incapacitated: (state) => state.is_unconscious,
  };
  const E = () => window.IRON_PIT_ACTION_ECONOMY || { available: (state) => state.action_available, spend: (state) => { state.action_available = false; } };

  function resolveAttack(sequence, round, attacker, target, attack, distance, extra = {}) {
    const spendAction = extra.spendAction !== false;
    if (spendAction && !E().available(attacker.state, "action")) throw new Error("Action is unavailable for attack.");
    const recklessStarted = extra.allowReckless === true && B2().activate(attacker, attack, round);
    if (recklessStarted) window.IRON_PIT_BROWSER_BARBARIAN3?.markRecklessUse(attacker.state, extra.turnKey);
    const conditions = H().conditionSources(attacker.state, target.state, distance, target.combatant_id);
    const conditional = H().CAM();
    const advantage = (extra.advantage || 0) + conditions.advantage + H().bloodiedFury(attacker.state, attack)
      + conditional.advantage(attacker.state, target.state, attack) + B2().attackAdvantage(attacker.state, attack)
      + M().nextAttackAgainstAdvantage(attacker.state, target.combatant_id);
    const closeThreat = attack.kind === "ranged" && H().rangedCloseThreat(attacker, target, distance, extra.setup);
    const mode = R().attackMode(attack, distance, advantage, conditions.disadvantage + SAP().disadvantage(attacker.state)
      + conditional.disadvantage(attacker.state, target.state, attack) + M().nextAttackMadeDisadvantage(attacker.state), closeThreat);
    const heroic = HI().rerollFailedAttack(attacker.state, R().d20(attack.bonus, mode), M().effectiveArmorClass(target.state));
    const attackRoll = M().applyD20Bonus(attacker.state, "attack-roll-bonus-die", heroic.roll);
    M().consumeNextAttackAgainstAdvantage(attacker.state, target.combatant_id); M().consumeNextAttackMadeDisadvantage(attacker.state); SAP().consume(attacker.state);
    M().consumeAttacksAgainstAdvantage(target.state); window.IRON_PIT_BROWSER_RAGE?.extendFromAttack(attacker.state, round);
    if (spendAction) E().spend(attacker.state, "action");
    const redirected = window.IRON_PIT_BROWSER_REACTIONS?.redirectAttack?.(target, extra.setup) || null, actualTarget = redirected || target;
    const natural = attackRoll.selected_roll, naturalTwenty = natural === 20, baseTargetAc = M().effectiveArmorClass(actualTarget.state);
    const naturalOne = natural === 1, naturalOneEndsTurn = naturalOne && extra.offTurn !== true;
    if (naturalOneEndsTurn) S().terminateTurn(attacker.state, "iron-pit-natural-1-attack");
    const initialHit = !naturalOne && (naturalTwenty || attackRoll.total >= baseTargetAc);
    const parry = window.IRON_PIT_BROWSER_REACTIONS?.parryHit?.(actualTarget.state, attack, attackRoll, initialHit, baseTargetAc) || { hit: initialHit, used: false };
    const hit = parry.hit, targetAc = baseTargetAc + (parry.used ? actualTarget.state.template.parry_reaction.ac_bonus : 0);
    const critical = Boolean(hit && (natural >= (attacker.state.template.critical_hit_minimum || 20)
      || (Q().autoCritical(actualTarget.state) && distance <= 5)));
    const hpBefore = actualTarget.state.current_hp, temporaryHpBefore = actualTarget.state.temporary_hp;
    const deathSuccessBefore = actualTarget.state.death_save_successes, deathFailureBefore = actualTarget.state.death_save_failures;
    const concentrationBefore = actualTarget.state.concentration?.effect_id || null;
    let damageRoll = null, damageComponents = [], damageOutcome = null, sapApplied = "", vexApplied = false, studiedApplied = false;
    let topple = { saveRoll: null, saveDc: null, saveSucceeded: null, applied: false }; const applied = [];
    if (hit) {
      const damage = R().weaponDamage(attacker.state, attack, critical, mode, extra.turnKey || `${round}:${attacker.combatant_id}`,
        extra.bonusDamage || null, actualTarget.state, window.IRON_PIT_BROWSER_SNEAK_ATTACK?.allyAvailable(attacker, extra.setup) || false);
      damageComponents = damage.components.map((part) => ({ ...part, applied_total: H().adjustedDamage(actualTarget.state, part.total, part.damage_type) }));
      damageRoll = { ...damage.roll, total: damageComponents.reduce((sum, part) => sum + part.applied_total, 0) };
      const appliedTypes = [...new Set(damageComponents.filter((part) => part.applied_total > 0).map((part) => part.damage_type))], affectedStates = H().states(extra.setup);
      damageOutcome = H().applyDamage(actualTarget.state, damageRoll.total, critical, appliedTypes, affectedStates);
      const living = actualTarget.state.is_alive && !actualTarget.state.is_dead, proneMax = extra.proneMaxSize || attack.proneMaxSize;
      if (living && S().canProne(actualTarget, proneMax) && !I().immune(actualTarget.state, "prone")) { if (!actualTarget.state.active_effect_ids.includes("prone")) actualTarget.state.active_effect_ids.push("prone"); applied.push("prone"); }
      if (living) applied.push(...CTRL().applyPersistent(actualTarget, attacker.combatant_id, attack.id, attack.controlEffect, attack.reach || 5, round, affectedStates));
      if (living) M().applyHitEffects?.(actualTarget.state, attacker.combatant_id, attack);
      topple = TOP().resolve(attacker, actualTarget, attack); if (topple.applied && !applied.includes("prone")) applied.push("prone");
      if (living) sapApplied = SAP().applyWeapon(attacker, actualTarget, attack, round) ? "weapon" : TM().apply(attacker, actualTarget, attack, round) ? "tactical" : "";
      vexApplied = window.IRON_PIT_BROWSER_VEX?.apply(attacker.state, attacker.combatant_id, actualTarget.combatant_id, attack, round, damageRoll.total) || false;
      window.IRON_PIT_BROWSER_RAGE?.endIfIncapacitated(actualTarget.state); C()?.endIfIncapacitated(actualTarget.state, affectedStates);
    } else {
      const rawGraze = GRZ().rawDamage(attacker.state, attack);
      if (rawGraze !== null) {
        const appliedTotal = H().adjustedDamage(actualTarget.state, rawGraze, attack.damageType, false);
        damageComponents = [{ source: `${attack.name} (Graze)`, notation: String(rawGraze), rolls: [], modifier: 0, damage_type: attack.damageType, total: rawGraze, applied_total: appliedTotal }];
        damageRoll = { notation: String(rawGraze), rolls: [], modifier: 0, selected_roll: null, mode: "normal", total: appliedTotal };
        const affectedStates = H().states(extra.setup), appliedTypes = appliedTotal > 0 ? [attack.damageType] : [];
        damageOutcome = H().applyDamage(actualTarget.state, appliedTotal, false, appliedTypes, affectedStates);
        window.IRON_PIT_BROWSER_RAGE?.endIfIncapacitated(actualTarget.state); C()?.endIfIncapacitated(actualTarget.state, affectedStates);
      }
      studiedApplied = STUDY().apply(attacker.state, attacker.combatant_id, target.combatant_id, round);
    }
    let description = `${attacker.state.template.name}: ${critical ? "CRITICAL HIT" : hit ? "HIT" : "MISS"} with ${attack.name}.`;
    if (naturalOneEndsTurn) description += " Natural 1: Iron Pit immediately ends the attacker's turn.";
    else if (naturalOne) description += " Natural 1: automatic miss; this off-turn attack does not terminate a future turn.";
    if (heroic.used) description += " Heroic Inspiration rerolls one d20.";
    if (!hit && damageRoll !== null) description += ` Graze deals ${damageRoll.total} ${attack.damageType} damage.`;
    if (studiedApplied) description += ` Studied Attacks primes the next attack against ${target.state.template.name}.`;
    if (recklessStarted) description += ` ${attacker.state.template.name} uses Reckless Attack.`;
    if (redirected) description += ` ${target.state.template.name} uses Redirect Attack; ${actualTarget.state.template.name} becomes the target.`;
    if (parry.used) description += ` ${actualTarget.state.template.name} uses Parry.`;
    if (sapApplied === "weapon") description += ` Sap mastery affects ${actualTarget.state.template.name}.`;
    if (sapApplied === "tactical") description += ` Tactical Master applies Sap to ${actualTarget.state.template.name}.`;
    if (vexApplied) description += ` Vex primes the next attack against ${actualTarget.state.template.name}.`;
    if (topple.saveDc !== null) description += ` Topple save DC ${topple.saveDc}: ${actualTarget.state.template.name} ${topple.saveSucceeded ? "succeeds" : "fails"}.`;
    if (damageOutcome === "relentless_endurance") description += ` ${actualTarget.state.template.name} uses Relentless Endurance and remains at 1 HP.`;
    if (damageOutcome === "undead_fortitude") description += ` ${actualTarget.state.template.name} succeeds on Undead Fortitude and remains at 1 HP.`;
    for (const condition of ["prone", "grappled", "restrained", "poisoned"]) if (applied.includes(condition)) description += ` ${actualTarget.state.template.name} is ${condition === "prone" ? "knocked Prone" : condition[0].toUpperCase() + condition.slice(1)}.`;
    const event = { sequence, round_number: round, event_type: "attack", actor_id: attacker.combatant_id, actor_name: attacker.state.template.name,
      target_id: actualTarget.combatant_id, target_name: actualTarget.state.template.name, attack_name: attack.name, target_ac: targetAc,
      attack_roll: attackRoll, saving_throw_roll: topple.saveRoll, save_ability: topple.saveDc === null ? null : "constitution", save_dc: topple.saveDc, save_succeeded: topple.saveSucceeded,
      damage_roll: damageRoll, damage_components: damageComponents, applied_condition_ids: [...new Set(applied)], hit, critical,
      turn_terminated: naturalOneEndsTurn, turn_termination_reason: naturalOneEndsTurn ? "iron-pit-natural-1-attack" : null,
      hp_before: hpBefore, hp_after: actualTarget.state.current_hp, temporary_hp_before: temporaryHpBefore, temporary_hp_after: actualTarget.state.temporary_hp,
      death_save_successes_before: deathSuccessBefore, death_save_failures_before: deathFailureBefore,
      death_save_successes: actualTarget.state.death_save_successes, death_save_failures: actualTarget.state.death_save_failures,
      is_stable: actualTarget.state.is_stable, is_dead: actualTarget.state.is_dead, weapon_id: attack.id, projectile: attack.projectile || null,
      feature_id: extra.featureId || (recklessStarted ? "reckless-attack" : null), concentration_ended_effect_id: concentrationBefore && !actualTarget.state.concentration ? concentrationBefore : null,
      animation: attack.animation || (attack.kind === "ranged" ? "projectile" : "slash"), description };
    if (hit) CTRL().applyMovement(attacker, actualTarget, attack.controlEffect, event);
    return window.IRON_PIT_BROWSER_CHAMPION?.criticalMove(attacker, extra.setup, event) || event;
  }
  window.IRON_PIT_BROWSER_ATTACK = {
    adjustedDamage: (...args) => H().adjustedDamage(...args), applyDamage: (...args) => H().applyDamage(...args),
    conditionSources: (...args) => H().conditionSources(...args), rangedCloseThreat: (...args) => H().rangedCloseThreat(...args), resolveAttack,
  };
})();
