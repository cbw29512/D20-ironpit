(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const V = () => window.IRON_PIT_BROWSER_SAVES;

  function d20Distribution(mode) {
    const rows = [];
    for (let value = 1; value <= 20; value += 1) {
      let probability = 1 / 20;
      if (mode === "advantage") probability = (value * value - (value - 1) * (value - 1)) / 400;
      if (mode === "disadvantage") probability = ((21 - value) ** 2 - (20 - value) ** 2) / 400;
      rows.push([value, probability]);
    }
    return rows;
  }

  function bonusDistribution(state, kind) {
    let distribution = new Map([[0, 1]]);
    for (const modifier of state.active_modifiers || []) {
      if (modifier.kind !== kind) continue;
      for (let die = 0; die < (modifier.dice_count || 0); die += 1) {
        const next = new Map();
        for (const [subtotal, probability] of distribution.entries()) {
          for (let face = 1; face <= modifier.dice_size; face += 1) {
            const value = subtotal + face;
            next.set(value, (next.get(value) || 0) + probability / modifier.dice_size);
          }
        }
        distribution = next;
      }
    }
    return [...distribution.entries()];
  }

  function damageFactor(state, type) {
    if (!type) return 0;
    return A().adjustedDamage(state, 2, type) / 2;
  }

  const meanDamage = (count, size, bonus = 0) => count * (size + 1) / 2 + bonus;

  function attackProbabilities(state, bonus, armorClass, mode, criticalMinimum = 20) {
    const bonuses = bonusDistribution(state, "attack-roll-bonus-die");
    let hit = 0, critical = 0;
    for (const [natural, naturalProbability] of d20Distribution(mode)) {
      for (const [extra, extraProbability] of bonuses) {
        const probability = naturalProbability * extraProbability;
        const succeeds = natural !== 1 && (natural === 20 || natural + bonus + extra >= armorClass);
        if (succeeds) {
          hit += probability;
          if (natural >= criticalMinimum) critical += probability;
        }
      }
    }
    return { hit, critical };
  }

  function spellAttack(caster, target, spell, setup) {
    const distance = S().distance(caster, target);
    const conditions = A().conditionSources(caster.state, target.state, distance, target.combatant_id);
    const closeThreat = A().rangedCloseThreat(caster, target, distance, setup);
    const mode = R().modeFromSources(conditions.advantage + M().attacksAgainstAdvantage(target.state),
      conditions.disadvantage + (closeThreat ? 1 : 0));
    const probabilities = attackProbabilities(caster.state, spell.attackBonus, M().effectiveArmorClass(target.state), mode);
    if (Q().autoCritical(target.state) && distance <= 5) probabilities.critical = probabilities.hit;
    const factor = damageFactor(target.state, spell.damageType);
    const normal = meanDamage(spell.damageDiceCount || 0, spell.damageDiceSize || 6, spell.damageBonus || 0) * factor;
    const critical = meanDamage((spell.damageDiceCount || 0) * 2, spell.damageDiceSize || 6, spell.damageBonus || 0) * factor;
    return Math.max(0, (probabilities.hit - probabilities.critical) * normal + probabilities.critical * critical);
  }

  function saveSuccess(target, action, magical = false) {
    if ((action.saveAbility === "strength" || action.saveAbility === "dexterity") && Q().autoFailStrDex(target.state)) return 0;
    const bonus = target.state.template.saving_throw_bonuses?.[action.saveAbility];
    if (bonus == null) throw new Error(`${target.state.template.name} lacks a certified ${action.saveAbility} save.`);
    const mode = V().saveMode(target.state, action.saveAbility, magical);
    const bonuses = bonusDistribution(target.state, "saving-throw-bonus-die");
    let success = 0;
    for (const [natural, naturalProbability] of d20Distribution(mode)) {
      for (const [extra, extraProbability] of bonuses) {
        if (natural + bonus + extra >= action.dc) success += naturalProbability * extraProbability;
      }
    }
    return success;
  }

  function saveSpell(target, action) {
    if (!(action.damageDiceCount > 0) || !action.damageType) return 0;
    const success = saveSuccess(target, action, true);
    const full = meanDamage(action.damageDiceCount, action.damageDiceSize, action.damageBonus || 0) * damageFactor(target.state, action.damageType);
    const onSuccess = action.successDamage === "half" ? full * 0.5 : 0;
    return Math.max(0, (1 - success) * full + success * onSuccess);
  }

  window.IRON_PIT_BROWSER_OFFENSE_VALUE = { attackProbabilities, saveSpell, spellAttack };
})();
