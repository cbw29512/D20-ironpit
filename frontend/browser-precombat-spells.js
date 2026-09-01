(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const SM = () => window.IRON_PIT_BROWSER_SPELL_MODIFIERS;

  function slotChoice(member, spell) {
    const resourceId = `spell-slot-${spell.level}`;
    return (member.state.resources?.[resourceId] || 0) > 0 ? spell.level : null;
  }

  function active(member, setup, spell) {
    if (member.state.concentration?.effect_id === spell.id) return true;
    const side = member.side === "heroes" ? setup.heroes : setup.monsters;
    return side.some((target) => target.state.active_buff_effect_ids?.includes(spell.id)
      || target.state.active_modifiers?.some((modifier) => modifier.source_effect_id === spell.id));
  }

  function choose(member, setup = null) {
    if (member.state.opening_buff_spell_id) return null;
    const spells = (member.state.template.defensive_spell_actions || [])
      .map((spell, index) => ({ spell, index }))
      .sort((a, b) => b.spell.level - a.spell.level
        || (b.spell.priority || 0) - (a.spell.priority || 0) || a.index - b.index);
    for (const { spell } of spells) {
      if (spell.concentration && member.state.concentration) continue;
      if (setup && active(member, setup, spell)) continue;
      const slotLevel = slotChoice(member, spell);
      if (slotLevel != null) return { spell, slotLevel };
    }
    return null;
  }

  function primaryAttackKind(member) {
    const attacks = member.state.template.attacks || [];
    const primaryId = member.state.template.primary_attack_id;
    return (attacks.find((attack) => attack.id === primaryId) || attacks[0] || {}).kind || null;
  }

  function nearestEnemyDistance(target, setup) {
    const enemies = target.side === "heroes" ? setup.monsters : setup.heroes;
    const living = enemies.filter((enemy) => enemy.state.is_alive && !enemy.state.is_dead);
    if (!living.length) return Number.MAX_SAFE_INTEGER;
    return Math.min(...living.map((enemy) => Math.abs(target.position_ft - enemy.position_ft)));
  }

  function friendlyBuffPriority(caster, target, setup) {
    const isMelee = primaryAttackKind(target) === "melee";
    const group = isMelee ? 0 : target === caster ? 1 : 2;
    return [group, nearestEnemyDistance(target, setup), Math.abs(caster.position_ft - target.position_ft), target.combatant_id];
  }

  function comparePriority(a, b) {
    for (let index = 0; index < 3; index += 1) {
      if (a[index] !== b[index]) return a[index] - b[index];
    }
    return a[3].localeCompare(b[3]);
  }

  function selectTargets(member, setup, spell, slotLevel) {
    if (slotLevel !== spell.level) throw new Error("Spell upcasting is not certified; use the spell's printed slot level.");
    if ((spell.targetPolicy || "self") === "self") return [member];
    const side = member.side === "heroes" ? setup.heroes : setup.monsters;
    const count = spell.targetCount || 1;
    return side.filter((target) => target.state.is_alive && !target.state.is_dead
        && Math.abs(member.position_ft - target.position_ft) <= (spell.range || 0))
      .sort((a, b) => comparePriority(friendlyBuffPriority(member, a, setup), friendlyBuffPriority(member, b, setup)))
      .slice(0, count);
  }

  function modifierDetail(effect) {
    if (effect.kind === "armor-class") return `${effect.flatBonus >= 0 ? "+" : ""}${effect.flatBonus || 0} AC`;
    if (effect.kind === "speed") return `${effect.flatBonus >= 0 ? "+" : ""}${effect.flatBonus || 0} Speed`;
    if (effect.diceCount) return `${effect.diceCount}d${effect.diceSize} ${effect.kind}`;
    return effect.kind;
  }

  function resolve(sequence, member, targets, spell, slotLevel, states = [member.state]) {
    if (slotLevel !== spell.level) throw new Error("Spell upcasting is not certified; use the spell's printed slot level.");
    const directHp = (spell.temporaryHp || 0) || (spell.maxHpIncrease || 0) || (spell.currentHpIncrease || 0);
    if (spell.concentration && (directHp || spell.damageResistances?.length)) throw new Error("Concentration defenses require source-owned modifier effects.");
    if (!targets.length) throw new Error(`${spell.name} has no legal precombat targets.`);
    if (member.state.opening_buff_spell_id) throw new Error(`${member.state.template.name} already committed its one opening buff this battle.`);
    if (spell.concentration && member.state.concentration) throw new Error(`${member.state.template.name} is already concentrating and will not replace the active buff automatically.`);
    if (targets.some((target) => target.state.active_buff_effect_ids?.includes(spell.id)
      || target.state.active_modifiers?.some((modifier) => modifier.source_effect_id === spell.id))) {
      throw new Error(`${spell.name} is already active on a selected target.`);
    }
    const resourceId = `spell-slot-${slotLevel}`;
    if (!(member.state.resources?.[resourceId] > 0)) throw new Error(`No level ${slotLevel} spell slot remains for ${spell.name}.`);
    member.state.opening_buff_spell_id = spell.id;
    member.state.resources[resourceId] -= 1;
    const tempHpDetails = [];
    for (const target of targets) {
      const before = target.state.temporary_hp;
      const after = S().grantTemporaryHp(target.state, spell.temporaryHp || 0);
      if (after > before) tempHpDetails.push(`${target.state.template.name} ${after} Temporary HP`);
      target.state.max_hp_bonus += spell.maxHpIncrease || 0;
      target.state.current_hp += spell.currentHpIncrease || 0;
      for (const type of spell.damageResistances || []) if (!target.state.temporary_damage_resistances.includes(type)) target.state.temporary_damage_resistances.push(type);
      if (!spell.concentration && !target.state.active_buff_effect_ids.includes(spell.id)) target.state.active_buff_effect_ids.push(spell.id);
    }
    if (spell.concentration || spell.modifierEffects?.length) {
      if (!SM()) throw new Error("Browser spell-modifier runtime is not loaded.");
      SM().apply(member.state, targets.map((target) => ({ targetId: target.combatant_id, state: target.state })), member.combatant_id, spell, 0, states);
    }
    const details = [...tempHpDetails];
    if (spell.maxHpIncrease) details.push(`+${spell.maxHpIncrease} Hit Point maximum`);
    if (spell.currentHpIncrease) details.push(`+${spell.currentHpIncrease} current Hit Points`);
    if (spell.damageResistances?.length) details.push(`resistance to ${spell.damageResistances.join(", ")}`);
    details.push(...(spell.modifierEffects || []).map(modifierDetail));
    if (spell.concentration) details.push("Concentration");
    const single = targets.length === 1 ? targets[0] : null;
    return { sequence, round_number: 0, event_type: "feature", actor_id: member.combatant_id, actor_name: member.state.template.name,
      target_id: single?.combatant_id || null, target_name: single?.state.template.name || null,
      feature_id: spell.id, concentration_started_effect_id: spell.concentration ? spell.id : null,
      resource_remaining: member.state.resources[resourceId], animation: spell.animation || "precombat-defense",
      description: `Precombat preparation: ${member.state.template.name} casts ${spell.name} with a level ${slotLevel} slot on ${targets.map((target) => target.state.template.name).join(", ")} (${details.join("; ")}).` };
  }

  function prepare(setup, sequence = 1) {
    const events = [], members = [...setup.heroes, ...setup.monsters], states = members.map((member) => member.state);
    for (const member of members) {
      const choice = choose(member, setup); if (!choice) continue;
      const targets = selectTargets(member, setup, choice.spell, choice.slotLevel);
      events.push(resolve(sequence++, member, targets, choice.spell, choice.slotLevel, states));
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS = { active, choose, prepare, resolve, selectTargets, slotChoice };
})();