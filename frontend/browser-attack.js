(() => {
  "use strict";
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const E = () => window.IRON_PIT_ACTION_ECONOMY || {
    available: (state, cost) => cost === "action" && state.action_available,
    spend: (state) => { state.action_available = false; },
  };

  function conditionSources(attacker, defender, distance, targetId) {
    let advantage = 0, disadvantage = 0;
    if (attacker.active_effect_ids.includes("prone")) disadvantage += 1;
    if (attacker.active_effect_ids.includes("restrained")) disadvantage += 1;
    if (attacker.active_effect_ids.includes("poisoned")) disadvantage += 1;
    disadvantage += G()?.attackDisadvantage(attacker, targetId) || 0;
    if (defender.active_effect_ids.includes("dodge") && !defender.is_unconscious && defender.template.speed_ft > 0 && !G()?.speedIsZero(defender)) disadvantage += 1;
    if (defender.is_unconscious) advantage += 1;
    if (defender.active_effect_ids.includes("restrained")) advantage += 1;
    if (defender.active_effect_ids.includes("prone")) distance <= 5 ? advantage += 1 : disadvantage += 1;
    return { advantage, disadvantage };
  }

  const bloodiedFury = (state, attack) => state.template.traits?.includes("bloodied-fury")
    && attack.kind === "melee" && state.current_hp * 2 <= state.template.max_hp ? 1 : 0;

  function adjustedDamage(target, amount, type) {
    if (target.template.damage_immunities?.includes(type)) return 0;
    let value = amount;
    if (target.template.damage_resistances?.includes(type) || target.temporary_damage_resistances?.includes(type)) value = Math.floor(value / 2);
    if (target.template.damage_vulnerabilities?.includes(type)) value *= 2;
    return value;
  }

  function useRelentless(state, remaining) {
    if (!state.template.traits?.includes("relentless-endurance")) return false;
    if ((state.resources["relentless-endurance"] || 0) < 1 || remaining >= state.template.max_hp) return false;
    state.resources["relentless-endurance"] -= 1; state.current_hp = 1;
    state.is_alive = true; state.is_unconscious = false; state.is_stable = false;
    return true;
  }

  const endDodge = (state) => { state.active_effect_ids = state.active_effect_ids.filter((id) => id !== "dodge"); };
  function markUnconscious(state) {
    state.is_alive = true; state.is_unconscious = true; state.is_stable = false; endDodge(state);
    if (!I().immune(state, "prone") && !state.active_effect_ids.includes("prone")) state.active_effect_ids.push("prone");
  }
  function markDead(state) {
    state.current_hp = 0; state.is_alive = false; state.is_dead = true;
    state.is_unconscious = false; state.is_stable = false; endDodge(state);
  }

  function applyDamage(state, amount, critical) {
    const absorbed = Math.min(state.temporary_hp, amount); state.temporary_hp -= absorbed; amount -= absorbed;
    if (!amount || state.is_dead) return "damaged";
    if (state.current_hp > 0) {
      const before = state.current_hp; state.current_hp = Math.max(0, before - amount);
      if (state.current_hp > 0) return "damaged";
      if (state.template.kind === "monster") { markDead(state); return "dead"; }
      const remaining = Math.max(0, amount - before);
      if (remaining >= state.template.max_hp) { markDead(state); return "dead"; }
      if (useRelentless(state, remaining)) return "relentless_endurance";
      markUnconscious(state); return "unconscious";
    }
    if (state.template.kind === "monster" || amount >= state.template.max_hp) { markDead(state); return "dead"; }
    state.is_stable = false;
    state.death_save_failures = Math.min(3, state.death_save_failures + (critical ? 2 : 1));
    if (state.death_save_failures >= 3) { markDead(state); return "dead"; }
    markUnconscious(state); return "unconscious";
  }

  function resolveAttack(sequence, round, attacker, target, attack, distance, extra = {}) {
    const spendAction = extra.spendAction !== false;
    if (spendAction && !E().available(attacker.state, "action")) throw new Error("Action is unavailable for attack.");
    const conditions = conditionSources(attacker.state, target.state, distance, target.combatant_id);
    const advantage = (extra.advantage || 0) + conditions.advantage + bloodiedFury(attacker.state, attack);
    const mode = R().attackMode(attack, distance, advantage, conditions.disadvantage);
    const attackRoll = R().d20(attack.bonus, mode);
    window.IRON_PIT_BROWSER_RAGE?.extendFromAttack(attacker.state, round);
    if (spendAction) E().spend(attacker.state, "action");
    const natural = attackRoll.selected_roll, naturalCritical = natural === 20;
    const hit = natural !== 1 && (naturalCritical || attackRoll.total >= target.state.template.armor_class);
    const critical = Boolean(hit && (naturalCritical || (target.state.is_unconscious && distance <= 5)));
    const hpBefore = target.state.current_hp;
    let damageRoll = null, damageComponents = [], damageOutcome = null;
    const applied = [];
    if (hit) {
      const damage = R().weaponDamage(attacker.state, attack, critical, mode, `${round}:${attacker.combatant_id}`, extra.bonusDamage || null);
      damageComponents = damage.components.map((part) => ({ ...part, applied_total: adjustedDamage(target.state, part.total, part.damage_type) }));
      damageRoll = { ...damage.roll, total: damageComponents.reduce((sum, part) => sum + part.applied_total, 0) };
      damageOutcome = applyDamage(target.state, damageRoll.total, critical);
      window.IRON_PIT_BROWSER_RAGE?.endIfIncapacitated(target.state);
      const living = target.state.is_alive && !target.state.is_dead;
      const proneMax = extra.proneMaxSize || attack.proneMaxSize;
      if (living && S().canProne(target, proneMax) && !I().immune(target.state, "prone")) {
        if (!target.state.active_effect_ids.includes("prone")) target.state.active_effect_ids.push("prone");
        applied.push("prone");
      }
      const control = attack.controlEffect;
      if (living && control?.grappleEscapeDc && (!control.maxTargetSize || S().sizeAtMost(target, control.maxTargetSize))) {
        applied.push(...G().apply(target.state, attacker.combatant_id, control.grappleEscapeDc, attack.reach || 5, Boolean(control.restrainsWhileGrappled)));
      }
      if (living && control?.conditionId) {
        const timed = T().apply(target.state, control.conditionId, attacker.combatant_id, Boolean(control.expiresAtStartOfSourceTurn));
        if (timed) applied.push(timed);
      }
    }
    let description = `${attacker.state.template.name}: ${critical ? "CRITICAL HIT" : hit ? "HIT" : "MISS"} with ${attack.name}.`;
    if (damageOutcome === "relentless_endurance") description += ` ${target.state.template.name} uses Relentless Endurance and remains at 1 HP.`;
    if (applied.includes("prone")) description += ` ${target.state.template.name} is knocked Prone.`;
    if (applied.includes("grappled")) description += ` ${target.state.template.name} is Grappled.`;
    if (applied.includes("restrained")) description += ` ${target.state.template.name} is Restrained while Grappled.`;
    if (applied.includes("poisoned")) description += ` ${target.state.template.name} is Poisoned.`;
    return {
      sequence, round_number: round, event_type: "attack", actor_id: attacker.combatant_id, actor_name: attacker.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name, attack_roll: attackRoll, damage_roll: damageRoll,
      damage_components: damageComponents, applied_condition_ids: [...new Set(applied)], hit, critical, hp_before: hpBefore,
      hp_after: target.state.current_hp, death_save_successes: target.state.death_save_successes,
      death_save_failures: target.state.death_save_failures, is_stable: target.state.is_stable, is_dead: target.state.is_dead,
      weapon_id: attack.id, projectile: attack.projectile || null, feature_id: extra.featureId || null,
      animation: attack.animation || (attack.kind === "ranged" ? "projectile" : "slash"), description,
    };
  }
  window.IRON_PIT_BROWSER_ATTACK = { adjustedDamage, applyDamage, resolveAttack };
})();
