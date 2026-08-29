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

  function attackMode(attack, distance, advantage = 0, disadvantage = 0) {
    if (attack.kind === "melee") {
      if (distance > (attack.reach || 5)) throw new Error(`${attack.name} is out of melee reach.`);
    } else {
      if (!attack.normal || !attack.long || distance > attack.long) throw new Error(`${attack.name} is out of range.`);
      if (distance > attack.normal) disadvantage += 1;
      if (distance <= 5) disadvantage += 1;
    }
    return modeFromSources(advantage, disadvantage);
  }

  function candidate(attack, critical) {
    const count = attack.diceCount * (critical ? 2 : 1);
    const rolls = dice().rollMany(count, attack.diceSize);
    return { rolls, modifier: attack.damageBonus, total: rolls.reduce((sum, roll) => sum + roll, 0) + attack.damageBonus };
  }

  function weaponDamage(attacker, attack, critical, mode, turnKey) {
    let rolled = candidate(attack, critical);
    if (attacker.template.traits?.includes("savage-attacker") && attacker.feature_last_turn_keys["savage-attacker"] !== turnKey) {
      const second = candidate(attack, critical);
      attacker.feature_last_turn_keys["savage-attacker"] = turnKey;
      if (second.total > rolled.total) rolled = second;
    }
    const components = [{ source: attack.name, damage_type: attack.damageType, ...rolled }];
    if (mode === "advantage" && attack.conditionalAdvantage) {
      const [count, sides] = attack.conditionalAdvantage;
      const rolls = dice().rollMany(count * (critical ? 2 : 1), sides);
      components.push({ source: "Advantage bonus damage", damage_type: attack.damageType, rolls, modifier: 0, total: rolls.reduce((a, b) => a + b, 0) });
    }
    const total = components.reduce((sum, item) => sum + item.total, 0);
    return {
      roll: { notation: components.map((c) => `${c.rolls.length}d${c.rolls.length ? (c.rolls[0] ? attack.diceSize : attack.diceSize) : attack.diceSize}`).join(" + "), rolls: components.flatMap((c) => c.rolls), modifier: components.reduce((s, c) => s + c.modifier, 0), total },
      components,
    };
  }

  window.IRON_PIT_BROWSER_ROLLS = { attackMode, d20, modeFromSources, weaponDamage };
})();
