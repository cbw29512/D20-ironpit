(() => {
  "use strict"; const S = () => window.IRON_PIT_BROWSER_STATE, R = () => window.IRON_PIT_BROWSER_ROLLS, A = () => window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE || { sources: () => 0 };
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE, T = () => window.IRON_PIT_BROWSER_TIMED, Z = () => window.IRON_PIT_BROWSER_ZERO_HP, BS = () => window.IRON_PIT_BROWSER_BRUTAL_STRIKE; const SAP = () => window.IRON_PIT_BROWSER_SAP || { applyWeapon: () => false, consume: () => 0, disadvantage: () => 0 };
  const H = () => { const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS; if (!hooks) throw new Error("Browser attack resolution requires browser-ability-hooks.js."); return hooks; };
  const O = () => { const outcome = window.IRON_PIT_BROWSER_ATTACK_OUTCOME; if (!outcome) throw new Error("Browser attack resolution requires browser-attack-outcome.js."); return outcome; }; const HI = () => window.IRON_PIT_BROWSER_HEROIC_INSPIRATION || { rerollFailedAttack: (_state, roll) => ({ roll, used: false }) }, B2 = () => window.IRON_PIT_BROWSER_BARBARIAN2 || { activate: () => false, attackAdvantage: () => 0, attacksAgainstAdvantage: () => 0 };
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS || { attacksAgainstAdvantage: () => 0, consumeAttacksAgainstAdvantage: () => 0, nextAttackAgainstAdvantage: () => 0, consumeNextAttackAgainstAdvantage: () => 0,
    effectiveArmorClass: (state) => state.template.armor_class, effectiveSpeed: (state) => state.template.speed_ft, attackRollFlat: () => 0, applyD20Bonus: (_state, _kind, roll) => roll };
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION, I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false }, X = () => window.IRON_PIT_BROWSER_EXHAUSTION || { attackDisadvantage: () => 0 }, DB = () => window.IRON_PIT_BROWSER_D20_BONUS_DICE;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { attackAdvantage: (state) => state.is_unconscious, autoCritical: (state) => state.is_unconscious, has: (state, id) => state.active_effect_ids.includes(id), incapacitated: (state) => state.is_unconscious, suppressAttackAdvantage: () => false, canSee: (observer, target) => !observer.active_effect_ids.includes("blinded") && !target.active_effect_ids.includes("invisible") };
  const E = () => window.IRON_PIT_ACTION_ECONOMY || { available: (state, cost) => cost === "action" && state.action_available, spend: (state) => { state.action_available = false; } };
  const states = (setup) => setup ? [...setup.heroes, ...setup.monsters].map((member) => member.state) : [];
  function conditionSources(attacker, defender, distance, targetId) {
    let advantage = M().attacksAgainstAdvantage(defender) + B2().attacksAgainstAdvantage(defender) + (M().d20TestAdvantage?.(attacker) || 0), disadvantage = X().attackDisadvantage(attacker) + (window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS?.attacksAgainstDisadvantage(defender, attacker, distance) || 0); const ignoresUnseen = Boolean(attacker.template.ignore_unseen_target_attack_disadvantage);
    if (Q().has(attacker, "blinded") && !ignoresUnseen) disadvantage += 1; if (Q().has(attacker, "invisible") && !Q().canSee(defender, attacker, distance)) advantage += 1;
    if (attacker.active_effect_ids.includes("prone")) disadvantage += 1; if (attacker.active_effect_ids.includes("restrained")) disadvantage += 1; if (attacker.active_effect_ids.includes("poisoned")) disadvantage += 1; disadvantage += G()?.attackDisadvantage(attacker, targetId) || 0;
    if (defender.active_effect_ids.includes("dodge") && !Q().incapacitated(defender) && M().effectiveSpeed(defender) > 0 && !G()?.speedIsZero(defender)) disadvantage += 1; if (Q().attackAdvantage(defender)) advantage += 1;
    if (Q().has(defender, "invisible") && !ignoresUnseen && !Q().canSee(attacker, defender, distance)) disadvantage += 1; if (defender.active_effect_ids.includes("restrained")) advantage += 1; if (defender.active_effect_ids.includes("prone")) distance <= 5 ? advantage += 1 : disadvantage += 1;
    return { advantage, disadvantage };
  }
  function rangedCloseThreat(attacker, target, distance, setup) {
    if (!setup) return distance <= 5 && !Q().incapacitated(target.state); const enemies = attacker.side === "heroes" ? setup.monsters : setup.heroes; return enemies.some((enemy) => enemy.state.is_alive && !enemy.state.is_dead && enemy.state.current_hp > 0 && !Q().incapacitated(enemy.state) && S().distance(attacker, enemy) <= 5);
  }
  const bloodiedFury = (state, attack) => state.template.traits?.includes("bloodied-fury") && attack.kind === "melee" && state.current_hp * 2 <= state.template.max_hp ? 1 : 0;
  function adjustedDamage(target, amount, type, allowVulnerability = true, sourceQualifiers = [], ignoreResistance = false) {
    const rules = window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES; if (rules) return rules.adjustedDamage(target, amount, type, allowVulnerability, sourceQualifiers, ignoreResistance); if (target.template.damage_immunities?.includes(type)) return 0; let value = amount; if (!ignoreResistance && (target.template.damage_resistances?.includes(type) || target.temporary_damage_resistances?.includes(type) || T()?.ownsDamageResistance?.(target, type) || Q().has(target, "petrified"))) value = Math.floor(value / 2); if (allowVulnerability && target.template.damage_vulnerabilities?.includes(type)) value *= 2; return value;
  }
  function applyDamage(state, amount, critical = false, damageTypes = [], affectedStates = [], setup = null, damageComponents = []) { const lifecycle = Z(); if (!lifecycle) throw new Error("Browser zero-HP runtime is not loaded."); return lifecycle.applyDamage(state, amount, critical, damageTypes, affectedStates, setup, damageComponents); }
  function legacyHitDamage(attacker, defender, attack, critical, mode, turnKey, options = {}) {
    if (attack.onHitSaveDamage) throw new Error("Save-dependent hit damage requires the browser hit-damage runtime."); const base = R().weaponDamage(attacker, attack, critical, mode, turnKey, options.bonusDamage || null, defender, Boolean(options.sneakAttackAllyAvailable)), damageComponents = base.components.map((part) => ({ ...part, applied_total: adjustedDamage(defender, part.total, part.damage_type, true, part.source_qualifiers || []) })); const appliedTotal = damageComponents.reduce((sum, part) => sum + part.applied_total, 0), damageRoll = { ...base.roll, total: appliedTotal }, appliedTypes = [...new Set(damageComponents.filter((part) => part.applied_total > 0).map((part) => part.damage_type))]; return { damageRoll, damageComponents, damageOutcome: applyDamage(defender, appliedTotal, critical, appliedTypes, options.affectedStates || [], options.setup || null, damageComponents), appliedTotal, saveDamage: null };
  }
  const HD = () => window.IRON_PIT_BROWSER_HIT_DAMAGE || { resolve: legacyHitDamage };
  function resolveAttack(sequence, round, attacker, target, attack, distance, extra = {}) {
    if (extra.brutalStrikeEffectIds != null) BS()?.selectEffects?.(attacker.state, extra.brutalStrikeEffectIds); const spendAction = extra.spendAction !== false; window.IRON_PIT_BROWSER_TIMED_CONTROL?.registerTurnAttack(attacker.state, extra.offTurn === true);
    if (spendAction && !E().available(attacker.state, "action")) throw new Error("Action is unavailable for attack.");
    const formation = window.IRON_PIT_BROWSER_FORMATION;
    if (formation?.targetAllowed && !formation.targetAllowed(attacker, target, attack, extra.setup || null)) throw new Error(`${attack.id} cannot target ${target.combatant_id} under its current target policy.`);
    if (!formation?.targetAllowed && (attack.grappleTargetPolicy || "normal") !== "normal") throw new Error("Nonstandard attack target policy requires browser-formation.js.");
    const automaticHit = Boolean(formation?.automaticHit?.(attacker, target, attack));
    const ward = window.IRON_PIT_BROWSER_TARGETING_WARDS?.check(attacker, target) || null;
    if (ward && !ward.succeeded) { if (spendAction) E().spend(attacker.state, "action"); return window.IRON_PIT_BROWSER_TARGETING_WARDS.blocked(sequence, round, attacker, target, attack.name, ward); }
    const recklessStarted = !automaticHit && extra.allowReckless === true && B2().activate(attacker, attack, round);
    if (recklessStarted) window.IRON_PIT_BROWSER_BARBARIAN3?.markRecklessUse(attacker.state, extra.turnKey);

    let mode = "normal";
    let heroic = { used: false, roll: null };
    let attackRoll = null;
    let d20Bonus = null;
    let rollPenalty = null;
    if (!automaticHit) {
      const conditions = conditionSources(attacker.state, target.state, distance, target.combatant_id);
      const disadvantage = conditions.disadvantage + SAP().disadvantage(attacker.state)
        + (T()?.nextAttackDisadvantage(attacker.state) || 0) + (extra.otherDisadvantageSources || 0) + (window.IRON_PIT_BROWSER_ENVIRONMENT_CONTEXTS?.disadvantageSources(attacker, extra.setup, "attack_rolls") || 0) + (window.IRON_PIT_BROWSER_TIMED_CONTROL?.abilityD20Disadvantage(attacker.state, attack.attackAbility || attack.attack_ability) || 0);
      const closeThreat = attack.kind === "ranged" && rangedCloseThreat(attacker, target, distance, extra.setup);
      const rangedDisadvantage = attack.kind === "ranged" && ((attack.normal && distance > attack.normal) || closeThreat);
      const recklessAdvantage = B2().attackAdvantage(attacker.state, attack);
      const brutalSuppression = BS()?.advantageSuppression(
        attacker.state, attack, extra.turnKey, disadvantage > 0 || rangedDisadvantage,
      ) || 0;
      const firstTurnUnacted = attacker.state.template.first_turn_attack_advantage_against_unacted_target
        && round === 1 && target?.state?.current_round == null ? 1 : 0;
      const unsuppressedAdvantage = (extra.advantage || 0) + firstTurnUnacted + conditions.advantage + bloodiedFury(attacker.state, attack)
        + Math.max(0, recklessAdvantage - brutalSuppression) + A().sources(attack, target.state, attacker.combatant_id)
        + M().nextAttackAgainstAdvantage(attacker.state, target.combatant_id) + (attacker.state.template.advantage_against_marked_effect_id && attacker.state.active_modifiers?.some((item) => item.source_effect_id === attacker.state.template.advantage_against_marked_effect_id && item.target_id === target.combatant_id) ? 1 : 0);
      const advantage = Q().suppressAttackAdvantage?.(target.state) ? 0 : unsuppressedAdvantage;
      mode = R().attackMode(attack, distance, advantage, disadvantage, closeThreat);
      heroic = HI().rerollFailedAttack(attacker.state, R().d20(attack.bonus + M().attackRollFlat(attacker.state, attack.weaponId || attack.id) + (M().nextIncomingAttackRollFlat?.(target.state, attacker.combatant_id) || 0), mode), M().effectiveArmorClass(target.state));
      attackRoll = M().applyD20Bonus(attacker.state, "attack-roll-bonus-die", heroic.roll);
      d20Bonus = [1, 20].includes(heroic.roll.selected_roll) ? null : DB()?.applyIfUseful(attacker.state, "attack", attackRoll, M().effectiveArmorClass(target.state), round);
      if (d20Bonus) attackRoll = d20Bonus.roll;
      rollPenalty = window.IRON_PIT_BROWSER_REACTION_ROLL_PENALTIES?.applyIfUseful(attacker, extra.setup, "attack", attackRoll, M().effectiveArmorClass(target.state)) || null;
      if (rollPenalty) attackRoll = rollPenalty.roll;
      M().consumeNextAttackAgainstAdvantage(attacker.state, target.combatant_id);
      M().consumeNextIncomingAttackRollFlat?.(target.state, attacker.combatant_id);
      T()?.consumeNextAttackDisadvantage(attacker.state);
      SAP().consume(attacker.state);
      M().consumeAttacksAgainstAdvantage(target.state);
      window.IRON_PIT_BROWSER_RAGE?.extendFromAttack(attacker.state, round);
    }

    if (spendAction) E().spend(attacker.state, "action");
    const redirected = automaticHit ? null : (window.IRON_PIT_BROWSER_REACTIONS?.redirectAttack?.(target, extra.setup) || null);
    const actualTarget = redirected || target;
    let resolvedAttackRoll = null;
    let natural = 0;
    let targetAc = M().effectiveArmorClass(actualTarget.state);
    let parry = { used: false };
    let outcomeAdjustment = null;
    let d20Override = { featureId: null, sourceName: null };
    let override = { featureId: null, sourceName: null };
    let hit = automaticHit;
    if (!automaticHit) {
      const resolved = O().resolveD20(attacker.state, actualTarget.state, attack, attackRoll,
        targetAc, attacker, extra.setup);
      resolvedAttackRoll = resolved.roll;
      natural = resolved.natural;
      targetAc = resolved.targetAc;
      parry = resolved.parry;
      outcomeAdjustment = resolved.adjustment;
      d20Override = resolved.d20;
      override = resolved.miss;
      hit = resolved.hit;
    }
    if (!hit) BS()?.clearPending?.(attacker.state, extra.turnKey);
    const naturalOne = natural === 1;
    const naturalOneEndsTurn = naturalOne && extra.offTurn !== true && !d20Override.featureId && !override.featureId;
    if (naturalOneEndsTurn) S().terminateTurn(attacker.state, "iron-pit-natural-1-attack");
    const expandedCritical = natural >= (attacker.state.template.critical_hit_minimum || 20);
    const critical = Boolean(hit && !override.featureId && (expandedCritical || (Q().autoCritical(actualTarget.state) && distance <= 5)));
    if (attacker.state.template.deferred_save_effect && !window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT) {
      throw new Error("Declared deferred-save effect requires browser-deferred-save-effect.js.");
    }
    const hpBefore = actualTarget.state.current_hp, temporaryHpBefore = actualTarget.state.temporary_hp;
    const deathSuccessBefore = actualTarget.state.death_save_successes, deathFailureBefore = actualTarget.state.death_save_failures;
    const concentrationBefore = actualTarget.state.concentration?.effect_id || null;
    const outcome = O().create();
    let { damageRoll, damageComponents, damageOutcome, hitSave, saveDamage, topple, sapApplied, vexApplied, studiedApplied, deferredEffectArmed, exileApplied } = outcome;
    let maximumHpSave = null;
    let contestedMovement = null;
    let cunningStrikeTrip = null, cunningStrikeObscure = null;
    const applied = outcome.appliedConditions;
    if (hit) {
      const affectedStates = states(extra.setup), damage = HD().resolve(attacker.state, actualTarget.state, attack, critical, mode,
        extra.turnKey || `${round}:${attacker.combatant_id}`, { bonusDamage: extra.bonusDamage || null,
          targetId: actualTarget.combatant_id, sneakAttackAllyAvailable: window.IRON_PIT_BROWSER_SNEAK_ATTACK?.allyAvailable(attacker, extra.setup, actualTarget) || false, affectedStates, setup: extra.setup || null, naturalRoll: natural });
      damageComponents = damage.damageComponents; damageRoll = damage.damageRoll; damageOutcome = damage.damageOutcome; saveDamage = damage.saveDamage; outcome.damageReductionReaction = damage.damageReductionReactionUsed ? damage : null;
      cunningStrikeTrip = damage.cunningStrikeTrip || null;
      cunningStrikeObscure = damage.cunningStrikeObscure || null;
      if (cunningStrikeTrip?.applied && !applied.includes("prone")) applied.push("prone");
      if (cunningStrikeObscure?.applied && !applied.includes("blinded")) applied.push("blinded");
      const living = actualTarget.state.is_alive && !actualTarget.state.is_dead, proneMax = extra.proneMaxSize || attack.proneMaxSize;
      if (living && S().canProne(actualTarget, proneMax) && !I().immune(actualTarget.state, "prone")) { if (!actualTarget.state.active_effect_ids.includes("prone")) actualTarget.state.active_effect_ids.push("prone"); applied.push("prone"); }
      const control = attack.controlEffect;
      if (living && control?.grappleEscapeDc && (!control.maxTargetSize || S().sizeAtMost(actualTarget, control.maxTargetSize))) applied.push(...G().apply(actualTarget.state, attacker.combatant_id, control.grappleEscapeDc, attack.reach || 5, Boolean(control.restrainsWhileGrappled)));
      if (living && control?.conditionId) {
        const timed = T().apply(actualTarget.state, control.conditionId, attacker.combatant_id, { sourceEffectId: attack.id, appliedRound: round,
          expiresAtStartOfSourceTurn: Boolean(control.expiresAtStartOfSourceTurn), expiryTiming: control.expiryTiming || null,
          repeatSaveAbility: control.repeatSaveAbility || null, repeatSaveDc: control.repeatSaveDc || null,
          repeatSaveTiming: control.repeatSaveTiming || null, allowedRemovalActionIds: control.allowedRemovalActionIds || [], sourceTemplate: attacker.state.template });
        if (timed) applied.push(timed);
      }
      if (living) M().applyHitEffects?.(actualTarget.state, attacker.combatant_id, attack);
      hitSave = living ? window.IRON_PIT_BROWSER_SAVES?.resolveOnHitConditionSave(actualTarget, attack, attacker.state.template, round, extra.setup, attacker) || null : null;
      if (hitSave?.appliedCondition && !applied.includes(hitSave.appliedCondition)) applied.push(hitSave.appliedCondition);
      const appliedDamage = (damageComponents || []).reduce((total, component) => total + (component.appliedTotal || 0), 0);
      maximumHpSave = living ? window.IRON_PIT_BROWSER_MAXIMUM_HP?.resolve(actualTarget, attack, appliedDamage) || null : null;
      contestedMovement = living ? window.IRON_PIT_BROWSER_CONTESTED_MOVEMENT?.resolve(
        attacker, actualTarget, attack, extra.setup, round,
      ) || null : null;
      Object.assign(outcome, { damageRoll, damageComponents, damageOutcome, hitSave, saveDamage, maximumHpSave, contestedMovement });
      const phase = H().runPhase(H().PHASES.ON_HIT, {
        sequence, round, member: attacker, target: actualTarget, originalTarget: target, attack,
        setup: extra.setup, turnKey: extra.turnKey, attackOutcome: outcome, events: [],
      });
      if (phase.events.length) throw new Error("Attack outcome hooks must not emit standalone battle events.");
      ({ damageRoll, damageComponents, damageOutcome, hitSave, saveDamage, topple, sapApplied, vexApplied, studiedApplied, deferredEffectArmed, exileApplied } = outcome); outcome.brutalStrikeEffects = BS()?.applyEffects?.(attacker, actualTarget, extra.setup, extra.turnKey, extra.brutalStrikeEffectIds) || []; window.IRON_PIT_BROWSER_MELEE_RETALIATION?.apply(attacker, actualTarget, { melee: (attack.kind || attack.attackKind) === "melee", setup: extra.setup }); window.IRON_PIT_BROWSER_MELEE_HIT_SAVE_RETALIATION?.apply(attacker, actualTarget, { melee: (attack.kind || attack.attackKind) === "melee", setup: extra.setup, round });
      window.IRON_PIT_BROWSER_RAGE?.endIfIncapacitated(actualTarget.state); C()?.endIfIncapacitated(actualTarget.state, affectedStates);
    } else {
      const phase = H().runPhase(H().PHASES.ON_MISS, {
        sequence, round, member: attacker, target: actualTarget, originalTarget: target, attack,
        setup: extra.setup, turnKey: extra.turnKey, attackOutcome: outcome, events: [],
      });
      if (phase.events.length) throw new Error("Attack outcome hooks must not emit standalone battle events.");
      ({ damageRoll, damageComponents, damageOutcome, hitSave, saveDamage, topple, sapApplied, vexApplied, studiedApplied } = outcome);
      if (damageRoll !== null) {
        const affectedStates = states(extra.setup);
        window.IRON_PIT_BROWSER_RAGE?.endIfIncapacitated(actualTarget.state); C()?.endIfIncapacitated(actualTarget.state, affectedStates);
      }
    }
    const event = O().buildEvent({
      sequence, round, attacker, target, actualTarget, attack, targetAc, resolvedAttackRoll,
      hit, critical, naturalOne, naturalOneEndsTurn, automaticHit, outcomeAdjustment,
      d20Override, override, heroic, d20Bonus, rollPenalty, recklessStarted, redirected, parry,
      damageRoll, damageComponents, damageOutcome, hitSave, saveDamage, topple, sapApplied,
      vexApplied, studiedApplied, deferredEffectArmed, exileApplied, maximumHpSave,
      contestedMovement, cunningStrikeTrip, cunningStrikeObscure, applied, hpBefore,
      temporaryHpBefore, deathSuccessBefore, deathFailureBefore, concentrationBefore, extra, outcome,
    });
    if (ward) window.IRON_PIT_BROWSER_TARGETING_WARDS.annotate(event, ward, attacker.state.template.name);
    return window.IRON_PIT_BROWSER_CHAMPION?.criticalMove(attacker, extra.setup, event) || event;
  }  window.IRON_PIT_BROWSER_ATTACK = { adjustedDamage, applyDamage, conditionSources, rangedCloseThreat, resolveAttack }; })();