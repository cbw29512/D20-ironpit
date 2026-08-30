(() => {
  "use strict";

  const dice = () => window.IRON_PIT_DICE;

  function modeFromSources(advantage = 0, disadvantage = 0) {
    if ((advantage > 0) === (disadvantage > 0)) return "normal";
    return advantage > 0 ? "advantage" : "disadvantage";
  }

  function d20(modifier = 0, mode = "normal") {
    const rolls = mode === "normal" ? [dice().roll(20)] : dice().rollMany(2, 20);
    const selected = mode === "advantage" ? Math.max(...rolls) : mode === "disadvantage" ? Math.min(...rolls) : rolls[0];
    return { notation: mode === "normal" ? "1d20" : "2d20", rolls, modifier, selected_roll: selected, mode, total: selected + modifier };
  }

  function attackMode(attack, distance, advantage = 0, disadvantage = 0, closeCombatThreat = distance <= 5) {
    if (attack.kind === "melee") {
      if (distance > (attack.reach || 5)) throw new Error(`${attack.name} is out of melee reach.`);
    } else {
      if (!attack.normal || !attack.long || distance > attack.long) throw new Error(`${attack.name} is out of range.`);
      if (distance > attack.normal) disadvantage += 1;
      if (closeCombatThreat) disadvantage += 1;
    }
    return modeFromSources(advantage, disadvantage);
  }

  function candidate(attack, critical) {
    const count = attack.diceCount * (critical ? 2 : 1);
    const rolls = dice().rollMany(count, attack.diceSize);
    return {
      notation: `${count}d${attack.diceSize}+${attack.damageBonus}`,
      rolls,
      modifier: attack.damageBonus,
      total: rolls.reduce((sum, roll) => sum + roll, 0) + attack.damageBonus,
    };
  }

  function fixedCandidate(attack) {
    return { notation: String(attack.fixedDamage), rolls: [], modifier: 0, total: attack.fixedDamage };
  }

  function damageComponent(spec, critical) {
    const count = spec.diceCount * (critical ? 2 : 1);
    const rolls = dice().rollMany(count, spec.diceSize);
    const modifier = spec.damageBonus || 0;
    return {
      source: spec.source,
      damage_type: spec.damageType,
      notation: `${count}d${spec.diceSize}+${modifier}`,
      rolls,
      modifier,
      total: rolls.reduce((sum, roll) => sum + roll, 0) + modifier,
    };
  }

  function bonusComponent(spec, critical) {
    return damageComponent({ ...spec, damageBonus: 0 }, critical);
  }

  function weaponDamage(attacker, attack, critical, mode, turnKey, bonusDamage = null) {
    let rolled;
    if (attack.fixedDamage != null) {
      rolled = fixedCandidate(attack);
    } else {
      const rageBonus = window.IRON_PIT_BROWSER_RAGE?.damageBonus(attacker, attack) || 0;
      const effective = { ...attack, damageBonus: attack.damageBonus + rageBonus };
      rolled = candidate(effective, critical);
      if (attacker.template.traits?.includes("savage-attacker") && attacker.feature_last_turn_keys["savage-attacker"] !== turnKey) {
        const second = candidate(effective, critical);
        attacker.feature_last_turn_keys["savage-attacker"] = turnKey;
        if (second.total > rolled.total) rolled = second;
      }
    }
    const components = [{ source: attack.name, damage_type: attack.damageType, ...rolled }];
    for (const extra of attack.onHitDamage || []) components.push(damageComponent(extra, critical));
    if (mode === "advantage" && attack.conditionalAdvantage) {
      const [baseCount, sides] = attack.conditionalAdvantage;
      const count = baseCount * (critical ? 2 : 1);
      const rolls = dice().rollMany(count, sides);
      components.push({
        source: "Advantage bonus damage", damage_type: attack.damageType,
        notation: `${count}d${sides}+0`, rolls, modifier: 0, total: rolls.reduce((a, b) => a + b, 0),
      });
    }
    if (bonusDamage) components.push(bonusComponent(bonusDamage, critical));
    const total = components.reduce((sum, item) => sum + item.total, 0);
    return {
      roll: {
        notation: components.map((item) => item.notation).join(" + "),
        rolls: components.flatMap((item) => item.rolls),
        modifier: components.reduce((sum, item) => sum + item.modifier, 0),
        total,
      },
      components,
    };
  }

  window.IRON_PIT_BROWSER_ROLLS = { attackMode, d20, modeFromSources, weaponDamage };
})();
