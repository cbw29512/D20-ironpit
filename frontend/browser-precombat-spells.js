(() => {
  "use strict";

  function slotChoice(member, spell) {
    const levels = Object.entries(member.state.resources || {})
      .filter(([id, uses]) => id.startsWith("spell-slot-") && uses > 0)
      .map(([id]) => Number(id.replace("spell-slot-", "")))
      .filter((level) => Number.isInteger(level) && level >= spell.level)
      .sort((a, b) => a - b);
    return levels.length ? levels[0] : null;
  }

  function choose(member) {
    const spells = (member.state.template.defensive_spell_actions || [])
      .map((spell, index) => ({ spell, index }))
      .sort((a, b) => (b.spell.priority || 0) - (a.spell.priority || 0)
        || a.spell.level - b.spell.level || a.index - b.index);
    for (const { spell } of spells) {
      if (spell.concentration) continue;
      const slotLevel = slotChoice(member, spell);
      if (slotLevel != null) return { spell, slotLevel };
    }
    return null;
  }

  function resolve(sequence, member, spell, slotLevel) {
    if (spell.concentration) throw new Error("Concentration precombat spells are not certified yet.");
    const resourceId = `spell-slot-${slotLevel}`;
    if (!(member.state.resources?.[resourceId] > 0)) throw new Error(`No level ${slotLevel} spell slot remains for ${spell.name}.`);
    member.state.resources[resourceId] -= 1;
    const extra = Math.max(0, slotLevel - spell.level);
    const tempHp = (spell.temporaryHp || 0) + extra * (spell.temporaryHpPerSlotAbove || 0);
    member.state.temporary_hp = Math.max(member.state.temporary_hp, tempHp);
    for (const type of spell.damageResistances || []) {
      if (!member.state.temporary_damage_resistances.includes(type)) member.state.temporary_damage_resistances.push(type);
    }
    const details = [];
    if (tempHp) details.push(`${tempHp} Temporary HP`);
    if (spell.damageResistances?.length) details.push(`resistance to ${spell.damageResistances.join(", ")}`);
    return {
      sequence, round_number: 0, event_type: "feature", actor_id: member.combatant_id,
      actor_name: member.state.template.name, target_id: member.combatant_id, target_name: member.state.template.name,
      feature_id: spell.id, resource_remaining: member.state.resources[resourceId],
      animation: spell.animation || "precombat-defense",
      description: `Precombat preparation: ${member.state.template.name} casts ${spell.name} on itself with a level ${slotLevel} slot (${details.join("; ")}).`,
    };
  }

  function prepare(setup, sequence = 1) {
    const events = [];
    for (const member of [...setup.heroes, ...setup.monsters]) {
      const choice = choose(member);
      if (!choice) continue;
      events.push(resolve(sequence++, member, choice.spell, choice.slotLevel));
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS = { choose, prepare, resolve, slotChoice };
})();
