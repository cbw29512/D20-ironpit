(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const R = () => window.IRON_PIT_BROWSER_ROLLS;

  function conditionSources(attacker, defender, distance) {
    let advantage = 0;
    let disadvantage = 0;
    if (attacker.active_effect_ids.includes("prone")) disadvantage += 1;
    if (defender.active_effect_ids.includes("dodge")) disadvantage += 1;
    if (defender.active_effect_ids.includes("prone")) distance <= 5 ? advantage += 1 : disadvantage += 1;
    return { advantage, disadvantage };
  }

  function adjustedDamage(target, amount, type) {
    if (target.template.damage_immunities?.includes(type)) return 0;
    let value = amount;
    const resistant = target.template.damage_resistances?.includes(type) || target.temporary_damage_resistances?.includes(type);
    if (resistant) value = Math.floor(value / 2);
    if (target.template.damage_vulnerabilities?.includes(type)) value *= 2;
    return value;
  }

  function useRelentless(state, remaining) {
    if (!state.template.traits?.includes("relentless-endurance")) return false;
    if ((state.resources["relentless-endurance"] || 0) < 1 || remaining >= state.template.max_hp) return false;
    state.resources["relentless-endurance"] -= 1;
    state.current_hp = 1;
    state.is_alive = true;
    state.is_unconscious = false;
    return true;
  }

  function markDead(state) {
    state.current_hp = 0;
    state.is_alive = false;
    state.is_dead = true;
    state.is_unconscious = false;
    state.is_stable = false;
  }

  function applyDamage(state, amount, critical) {
    const absorbed = Math.min(state.temporary_hp, amount);
    state.temporary_hp -= absorbed;
    amount -= absorbed;
    if (!amount || state.is_dead) return "damaged";
    if (state.current_hp > 0) {
      const before = state.current_hp;
      state.current_hp = Math.max(0, before - amount);
      if (state.current_hp > 0) return "damaged";
      if (state.template.kind === "monster") { markDead(state); return "dead"; }
      const remaining = Math.max(0, amount - before);
      if (remaining >= state.template.max_hp) { markDead(state); return "dead"; }
      if (useRelentless(state, remaining)) return "relentless_endurance";
      state.is_unconscious = true;
      return "unconscious";
    }
    if (state.template.kind === "monster" || amount >= state.template.max_hp) { markDead(state); return "dead"; }
    state.death_save_failures = Math.min(3, state.death_save_failures + (critical ? 2 : 1));
    state.is_unconscious = true;
    if (state.death_save_failures >= 3) { markDead(state); return "dead"; }
    return "unconscious";
  }

  function resolveAttack(sequence, round, attacker, target, attack, distance, extra = {}) {
    const conditions = conditionSources(attacker.state, target.state, distance);
    const advantage = (extra.advantage || 0) + conditions.advantage;
    const mode = R().attackMode(attack, distance, advantage, conditions.disadvantage);
    const attackRoll = R().d20(attack.bonus, mode);
    window.IRON_PIT_BROWSER_RAGE?.extendFromAttack(attacker.state, round);
    if (extra.spendAction !== false) attacker.state.action_available = false;
    const natural = attackRoll.selected_roll;
    const critical = natural === 20;
    const hit = natural !== 1 && (critical || attackRoll.total >= target.state.template.armor_class);
    const hpBefore = target.state.current_hp;
    let damageRoll = null;
    let damageComponents = [];
    let damageOutcome = null;
    const applied = [];
    if (hit) {
      const damage = R().weaponDamage(attacker.state, attack, critical, mode, `${round}:${attacker.combatant_id}`);
      damageComponents = damage.components.map((part) => ({ ...part, applied_total: adjustedDamage(target.state, part.total, part.damage_type) }));
      damageRoll = { ...damage.roll, total: damageComponents.reduce((sum, part) => sum + part.applied_total, 0) };
      damageOutcome = applyDamage(target.state, damageRoll.total, critical);
      window.IRON_PIT_BROWSER_RAGE?.endIfIncapacitated(target.state);
      if (S().canProne(target, attack.proneMaxSize) && target.state.current_hp > 0) {
        if (!target.state.active_effect_ids.includes("prone")) target.state.active_effect_ids.push("prone");
        applied.push("prone");
      }
    }
    let description = `${attacker.state.template.name}: ${critical ? "CRITICAL HIT" : hit ? "HIT" : "MISS"} with ${attack.name}.`;
    if (damageOutcome === "relentless_endurance") description += ` ${target.state.template.name} uses Relentless Endurance and remains at 1 HP.`;
    if (applied.includes("prone")) description += ` ${target.state.template.name} is knocked Prone.`;
    return {
      sequence, round_number: round, event_type: "attack", actor_id: attacker.combatant_id,
      actor_name: attacker.state.template.name, target_id: target.combatant_id, target_name: target.state.template.name,
      attack_roll: attackRoll, damage_roll: damageRoll, damage_components: damageComponents,
      applied_condition_ids: applied, hit, critical, hp_before: hpBefore, hp_after: target.state.current_hp,
      weapon_id: attack.id, projectile: attack.projectile || null, feature_id: extra.featureId || null,
      animation: attack.animation || (attack.kind === "ranged" ? "projectile" : "slash"), description,
    };
  }

  window.IRON_PIT_BROWSER_ATTACK = { applyDamage, resolveAttack };
})();
