(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const O = () => window.IRON_PIT_BROWSER_OFFENSE_VALUE;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function scaledSpell(spell, slotLevel) {
    try {
      if (spell.level === 0) {
        if (slotLevel !== 0) throw new Error("Cantrips cannot expend spell slots.");
        return spell;
      }
      if (slotLevel < spell.level || slotLevel > 9) throw new Error(`Illegal slot level ${slotLevel} for ${spell.name}.`);
      const levelsAbove = slotLevel - spell.level;
      if (!levelsAbove) return spell;
      if (!(spell.upcastDicePerLevel > 0)) throw new Error(`${spell.name} has no certified higher-slot scaling.`);
      return {
        ...spell,
        damageDiceCount: (spell.damageDiceCount || 0) + levelsAbove * spell.upcastDicePerLevel,
      };
    } catch (error) {
      console.error("Browser spell-attack scaling failed", { spell: spell?.id, slotLevel, error });
      throw error;
    }
  }

  function slotLevels(member, spell, turnKey) {
    try {
      if (spell.level === 0) return [0];
      if (!C().slotSpellAvailable(member.state, turnKey)) return [];
      const maximum = spell.upcastDicePerLevel > 0 ? 9 : spell.level;
      const levels = [];
      for (let level = spell.level; level <= maximum; level += 1) {
        if ((member.state.resources?.[`spell-slot-${level}`] || 0) > 0) levels.push(level);
      }
      return levels;
    } catch (error) {
      console.error("Browser spell-attack slot lookup failed", { spell: spell?.id, error });
      throw error;
    }
  }

  function choose(member, setup, turnKey) {
    try {
      const enemies = member.side === "heroes" ? setup.monsters : setup.heroes;
      const candidates = [];
      for (const [index, spell] of (member.state.template.spell_attack_actions || []).entries()) {
        if (spell.actionCost === "reaction" || !E().available(member.state, spell.actionCost)) continue;
        for (const slotLevel of slotLevels(member, spell, turnKey)) {
          const scaled = scaledSpell(spell, slotLevel);
          for (const target of enemies) {
            if (!target.state.is_alive || target.state.is_dead || target.state.current_hp <= 0
                || S().distance(member, target) > spell.range) continue;
            candidates.push({
              spell, target, slotLevel, index,
              score: O().spellAttack(member, target, scaled, setup),
            });
          }
        }
      }
      candidates.sort((a, b) => b.score - a.score || a.slotLevel - b.slotLevel
        || a.spell.level - b.spell.level || a.target.state.current_hp - b.target.state.current_hp
        || a.index - b.index || a.target.combatant_id.localeCompare(b.target.combatant_id));
      return candidates.length ? {
        action: candidates[0].spell,
        target: candidates[0].target,
        slotLevel: candidates[0].slotLevel,
        expectedDamage: candidates[0].score,
      } : null;
    } catch (error) {
      console.error("Browser spell-attack selection failed", { member: member?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SPELL_ATTACK_POLICY = { choose, scaledSpell, slotLevels };
})();