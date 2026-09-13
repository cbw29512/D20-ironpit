(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const D = () => window.IRON_PIT_DICE;

  const members = (setup) => [...setup.heroes, ...setup.monsters];
  function grapplers(source, setup) {
    const byId = Object.fromEntries(members(setup).map((member) => [member.combatant_id, member]));
    const ids = [...new Set((source.state.grapple_sources || []).map((item) => item.source_id))];
    return ids.map((id) => byId[id]).filter((member) => member && member.state.current_hp > 0 && !member.state.is_dead);
  }

  function startTurn(sequence, round, source, setup) {
    const events = [], affected = members(setup).map((member) => member.state);
    for (const profile of source.state.template.startTurnRelationshipDamage || []) {
      const targets = profile.targetRelationship === "grapplers" ? grapplers(source, setup) : [];
      for (const target of targets) {
        const rolls = D().rollMany(profile.diceCount, profile.diceSize);
        const raw = rolls.reduce((sum, roll) => sum + roll, 0) + (profile.damageBonus || 0);
        const applied = A().adjustedDamage(target.state, raw, profile.damageType), before = target.state.current_hp;
        if (applied) A().applyDamage(target.state, applied, false, [profile.damageType], affected);
        const notation = `${profile.diceCount}d${profile.diceSize}+${profile.damageBonus || 0}`;
        events.push({ sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: source.combatant_id, actor_name: source.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          feature_id: profile.id, damage_roll: { notation, rolls, modifier: profile.damageBonus || 0, total: applied },
          damage_components: [{ source: profile.name, notation, rolls, modifier: profile.damageBonus || 0,
            damage_type: profile.damageType, total: raw, applied_total: applied }], hp_before: before,
          hp_after: target.state.current_hp, animation: "damage",
          description: `${target.state.template.name} takes ${applied} ${profile.damageType} damage from ${source.state.template.name}'s ${profile.name}.` });
      }
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_START_TURN_DAMAGE = { startTurn };
})();
