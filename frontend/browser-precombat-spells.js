(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const SM = () => window.IRON_PIT_BROWSER_SPELL_MODIFIERS;

  function slotChoice(member, spell) {
    const resourceId = `spell-slot-${spell.level}`;
    return (member.state.resources?.[resourceId] || 0) > 0 ? spell.level : null;
  }

  function choose(member) {
    const spells = (member.state.template.defensive_spell_actions || [])
      .map((spell, index) => ({ spell, index }))
      .sort((a, b) => (b.spell.priority || 0) - (a.spell.priority || 0)
        || a.spell.level - b.spell.level || a.index - b.index);
    for (const { spell } of spells) {
      const slotLevel = slotChoice(member, spell);
      if (slotLevel != null) return { spell, slotLevel };
    }
    return null;
  }

  function selectTargets(member, setup, spell, slotLevel) {
    if (slotLevel !== spell.level) throw new Error("Spell upcasting is not certified; use the spell's printed slot level.");
    if ((spell.targetPolicy || "self") === "self") return [member];
    const side = member.side === "heroes" ? setup.heroes : setup.monsters;
    const count = spell.targetCount || 1;
    return side.filter((target) => target.state.is_alive && !target.state.is_dead
        && Math.abs(member.position_ft - target.position_ft) <= (spell.range || 0))
      .sort((a, b) => Number(a !== member) - Number(b !== member)
        || Math.abs(member.position_ft - a.position_ft) - Math.abs(member.position_ft - b.position_ft)
        || a.combatant_id.localeCompare(b.combatant_id))
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
    if (spell.concentration && ((spell.temporaryHp || 0) || spell.damageResistances?.length)) throw new Error("Concentration defenses require source-owned modifier effects.");
    if (!targets.length) throw new Error(`${spell.name} has no legal precombat targets.`);
    const resourceId = `spell-slot-${slotLevel}`;
    if (!(member.state.resources?.[resourceId] > 0)) throw new Error(`No level ${slotLevel} spell slot remains for ${spell.name}.`);
    member.state.resources[resourceId] -= 1;
    const tempHp = spell.temporaryHp || 0;
    for (const target of targets) {
      S().grantTemporaryHp(target.state, tempHp);
      for (const type of spell.damageResistances || []) if (!target.state.temporary_damage_resistances.includes(type)) target.state.temporary_damage_resistances.push(type);
    }
    if (spell.concentration || spell.modifierEffects?.length) {
      if (!SM()) throw new Error("Browser spell-modifier runtime is not loaded.");
      SM().apply(member.state, targets.map((target) => ({ targetId: target.combatant_id, state: target.state })), member.combatant_id, spell, 0, states);
    }
    const details = [];
    if (tempHp) details.push(`${tempHp} Temporary HP`);
    if (spell.damageResistances?.length) details.push(`resistance to ${spell.damageResistances.join(", ")}`);
    details.push(...(spell.modifierEffects || []).map(modifierDetail));
    if (spell.concentration) details.push("Concentration");
    const single = targets.length === 1 ? targets[0] : null;
    return { sequence, round_number: 0, event_type: "feature", actor_id: member.combatant_id, actor_name: member.state.template.name,
      target_id: single?.combatant_id || null, target_name: single?.state.template.name || null,
      feature_id: spell.id, resource_remaining: member.state.resources[resourceId], animation: spell.animation || "precombat-defense",
      description: `Precombat preparation: ${member.state.template.name} casts ${spell.name} with a level ${slotLevel} slot on ${targets.map((target) => target.state.template.name).join(", ")} (${details.join("; ")}).` };
  }

  function prepare(setup, sequence = 1) {
    const events = [], members = [...setup.heroes, ...setup.monsters], states = members.map((member) => member.state);
    for (const member of members) {
      const choice = choose(member); if (!choice) continue;
      const targets = selectTargets(member, setup, choice.spell, choice.slotLevel);
      events.push(resolve(sequence++, member, targets, choice.spell, choice.slotLevel, states));
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS = { choose, prepare, resolve, selectTargets, slotChoice };
})();
