(() => {
  "use strict";

  const dice = () => window.IRON_PIT_DICE;
  const effectiveMaxHp = (state) => window.IRON_PIT_BROWSER_MAX_HP_REDUCTION?.effectiveMaxHp(state) ?? Math.max(0, state.template.max_hp + (state.max_hp_bonus || 0) - (state.max_hp_reduction || 0));
  const bloodied = (state) => state.current_hp * 2 <= effectiveMaxHp(state);
  const bloodiedAttackAdvantage = (state, attack) => !bloodied(state) ? 0 : state.template.traits?.includes("bloodied-frenzy") ? 1 : state.template.traits?.includes("bloodied-fury") && attack.kind === "melee" ? 1 : 0;
  const bloodiedSaveAdvantage = (state) => state.template.traits?.includes("bloodied-frenzy") && bloodied(state) ? 1 : 0;

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
    const reach = attack.reach || 5;
    const usesMeleeMode = attack.kind === "melee" || (attack.kind === "melee_or_ranged" && distance <= reach);
    if (usesMeleeMode) {
      if (distance > reach) throw new Error(`${attack.name} is out of melee reach.`);
    } else {
      if (!attack.normal || !attack.long || distance > attack.long) throw new Error(`${attack.name} is out of range.`);
      if (distance > attack.normal) disadvantage += 1;
      if (closeCombatThreat) disadvantage += 1;
    }
    return modeFromSources(advantage, disadvantage);
  }

  function candidate(attack, critical) {
    const count = attack.diceCount * (critical ? 2 : 1);
    const rawRolls = dice().rollMany(count, attack.diceSize);
    const rolls = attack.damageDieMinimum ? rawRolls.map((roll) => Math.max(roll, attack.damageDieMinimum)) : rawRolls;
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
    const modifier = spec.damageBonus || 0;
    if (spec.diceCount === 0) {
      return { source: spec.source, damage_type: spec.damageType, notation: String(modifier), rolls: [], modifier: 0, total: modifier };
    }
    const count = spec.diceCount * (critical ? 2 : 1);
    const rolls = dice().rollMany(count, spec.diceSize);
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

  function conditionalActive(spec, attacker, target, mode) {
    if (!spec) return false;
    if (spec.trigger === "attack_advantage") return mode === "advantage";
    if (spec.trigger === "attacker_bloodied") return bloodied(attacker);
    if (spec.trigger === "target_bloodied") {
      if (!target) throw new Error("Target state is required for target-Bloodied conditional damage.");
      return bloodied(target);
    }
    throw new Error(`Unsupported conditional damage trigger: ${spec.trigger}`);
  }

  function savageRevision(first, second, useSecond) {
    return {
      source_effect_id: "savage-attacker", kind: "roll_twice_choose",
      original_rolls: [...first.rolls], replacement_rolls: [...second.rolls],
      original_modifier: first.modifier || 0, replacement_modifier: second.modifier || 0,
      original_selected: null, replacement_selected: null,
      original_total: first.total, replacement_total: second.total,
      accepted: useSecond ? "replacement" : "original", replaced_die_index: null,
    };
  }

  function weaponDamage(attacker, attack, critical, mode, turnKey, bonusDamage = null, target = null, sneakAllyAvailable = false) {
    const conditional = attack.conditionalDamage || null;
    const replacement = conditional?.mode === "replace_weapon" && conditionalActive(conditional, attacker, target, mode)
      ? conditional : null;
    let rolled;
    if (replacement) {
      rolled = candidate(replacement, critical);
    } else if (attack.fixedDamage != null) {
      rolled = fixedCandidate(attack);
    } else {
      const rageBonus = window.IRON_PIT_BROWSER_RAGE?.damageBonus(attacker, attack) || 0;
      const effective = { ...attack, damageBonus: attack.damageBonus + rageBonus };
      rolled = candidate(effective, critical);
      if (attacker.template.traits?.includes("savage-attacker") && attacker.feature_last_turn_keys["savage-attacker"] !== turnKey) {
        const first = rolled, second = candidate(effective, critical), useSecond = second.total > first.total;
        rolled = useSecond ? second : first;
        rolled.revisions = [...(rolled.revisions || []), savageRevision(first, second, useSecond)];
        attacker.feature_last_turn_keys["savage-attacker"] = turnKey;
      }
    }
    const components = [{ source: attack.name, damage_type: replacement?.damageType || attack.damageType, ...rolled }];
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
    if (conditional?.mode === "add" && conditionalActive(conditional, attacker, target, mode)) {
      components.push(damageComponent({ ...conditional, source: "Conditional bonus damage" }, critical));
    }
    const sneak = window.IRON_PIT_BROWSER_SNEAK_ATTACK?.bonusDamage(attacker, attack, mode, turnKey, sneakAllyAvailable);
    if (sneak) components.push(bonusComponent(sneak, critical));
    const frenzy = window.IRON_PIT_BROWSER_BARBARIAN3?.bonusDamage(attacker, attack, turnKey);
    if (frenzy) components.push(bonusComponent(frenzy, critical));
    if (bonusDamage) components.push(bonusComponent(bonusDamage, critical));
    window.IRON_PIT_BROWSER_TIMED?.applyDamageRollPenalty(attacker, components);
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

  window.IRON_PIT_BROWSER_ROLLS = { attackMode, bloodiedAttackAdvantage, bloodiedSaveAdvantage, d20, modeFromSources, weaponDamage };
})();