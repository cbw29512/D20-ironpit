(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const SM = () => window.IRON_PIT_BROWSER_SPELL_MODIFIERS;

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
      const slotLevel = slotChoice(member, spell);
      if (slotLevel != null) return { spell, slotLevel };
    }
    return null;
  }

  function modifierDetail(effect) {
    if (effect.kind === "armor-class") return `${effect.flatBonus >= 0 ? "+" : ""}${effect.flatBonus || 0} AC`;
    if (effect.kind === "speed") return `${effect.flatBonus >= 0 ? "+" : ""}${effect.flatBonus || 0} Speed`;
    if (effect.diceCount) return `${effect.diceCount}d${effect.diceSize} ${effect.kind}`;
    return effect.kind;
  }

  function resolve(sequence, member, spell, slotLevel, states = [member.state]) {
    if (spell.concentration && ((spell.temporaryHp || 0) || spell.damageResistances?.length)) {
      throw new Error("Concentration defenses require source-owned modifier effects.");
    }
    const resourceId = `spell-slot-${slotLevel}`;
    if (!(member.state.resources?.[resourceId] > 0)) throw new Error(`No level ${slotLevel} spell slot remains for ${spell.name}.`);
    member.state.resources[resourceId] -= 1;
    const extra = Math.max(0, slotLevel - spell.level);
    const tempHp = (spell.temporaryHp || 0) + extra * (spell.temporaryHpPerSlotAbove || 0);
    const grantedTempHp = S().grantTemporaryHp(member.state, tempHp);
    for (const type of spell.damageResistances || []) {
      if (!member.state.temporary_damage_resistances.includes(type)) member.state.temporary_damage_resistances.push(type);
    }
    if (spell.concentration || spell.modifierEffects?.length) {
      if (!SM()) throw new Error("Browser spell-modifier runtime is not loaded.");
      SM().apply(member.state, member.state, member.combatant_id, member.combatant_id, spell, 0, states);
    }
    const details = [];
    if (tempHp && grantedTempHp) details.push(`${grantedTempHp} Temporary HP`);
    if (spell.damageResistances?.length) details.push(`resistance to ${spell.damageResistances.join(", ")}`);
    details.push(...(spell.modifierEffects || []).map(modifierDetail));
    if (spell.concentration) details.push("Concentration");
    return {
      sequence, round_number: 0, event_type: "feature", actor_id: member.combatant_id,
      actor_name: member.state.template.name, target_id: member.combatant_id, target_name: member.state.template.name,
      feature_id: spell.id, resource_remaining: member.state.resources[resourceId],
      animation: spell.animation || "precombat-defense",
      description: `Precombat preparation: ${member.state.template.name} casts ${spell.name} on itself with a level ${slotLevel} slot (${details.join("; ")}).`,
    };
  }

  function prepare(setup, sequence = 1) {
    const events = [], members = [...setup.heroes, ...setup.monsters], states = members.map((member) => member.state);
    for (const member of members) {
      const choice = choose(member);
      if (!choice) continue;
      events.push(resolve(sequence++, member, choice.spell, choice.slotLevel, states));
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS = { choose, prepare, resolve, slotChoice };
})();
