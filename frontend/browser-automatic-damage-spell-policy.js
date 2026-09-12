(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;

  function slots(state, minimumLevel, turnKey) {
    if (!C().slotSpellAvailable(state, turnKey)) return [];
    return Object.entries(state.resources || {})
      .filter(([id, uses]) => id.startsWith("spell-slot-") && uses > 0)
      .map(([id, uses]) => [Number(id.slice("spell-slot-".length)), id, uses])
      .filter(([level]) => Number.isInteger(level) && level >= minimumLevel && level <= 9)
      .sort((a, b) => a[0] - b[0]);
  }

  function factor(target, damageType) {
    const t = target.state.template;
    if ((t.damage_immunities || []).includes(damageType)) return 0;
    let value = 1;
    if ((t.damage_resistances || []).includes(damageType) || (target.state.temporary_damage_resistances || []).includes(damageType)) value *= 0.5;
    if ((t.damage_vulnerabilities || []).includes(damageType)) value *= 2;
    return value;
  }

  function projectileCount(action, slotLevel) {
    return action.baseProjectiles + Math.max(0, slotLevel - action.level) * (action.projectilesPerSlotAbove || 0);
  }

  function choose(caster, setup, turnKey) {
    if (!E().available(caster.state, "action")) return null;
    const enemies = caster.side === "heroes" ? setup.monsters : setup.heroes;
    const choices = [];
    for (const action of caster.state.template.automatic_damage_spell_actions || []) {
      const slot = slots(caster.state, action.level, turnKey)[0];
      if (!slot) continue;
      const slotLevel = slot[0];
      const count = projectileCount(action, slotLevel);
      const mean = count * ((action.damageDiceCountPerProjectile || 1) * (action.damageDiceSize + 1) / 2 + (action.damageBonusPerProjectile || 0));
      for (const target of enemies) {
        if (!target.state.is_alive || target.state.is_dead || target.state.current_hp <= 0) continue;
        if (S().distance(caster, target) > action.range) continue;
        choices.push({ action, target, slotLevel, expectedDamage: mean * factor(target, action.damageType) });
      }
    }
    choices.sort((a, b) => b.expectedDamage - a.expectedDamage || a.slotLevel - b.slotLevel || a.target.combatant_id.localeCompare(b.target.combatant_id));
    return choices[0] || null;
  }

  window.IRON_PIT_BROWSER_AUTOMATIC_DAMAGE_SPELL_POLICY = { choose, projectileCount, slots };
})();
