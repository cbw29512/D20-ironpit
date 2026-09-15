(() => {
  "use strict";
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const SR = () => window.IRON_PIT_BROWSER_SPELL_REFLECTION;

  function reroll(caster, reflector, spell, setup) {
    const target = SR()?.target(reflector, caster, setup);
    if (!target) return null;
    SR().spend(reflector);
    const distance = S().distance(caster, target);
    const conditions = A().conditionSources(caster.state, target.state, distance, target.combatant_id);
    const advantage = conditions.advantage + M().nextAttackAgainstAdvantage(caster.state, target.combatant_id);
    const closeThreat = (spell.attackKind || "ranged") === "ranged" && A().rangedCloseThreat(caster, target, distance, setup);
    const mode = R().modeFromSources(advantage, conditions.disadvantage + (closeThreat ? 1 : 0));
    const targetAc = M().effectiveArmorClass(target.state);
    const attackRoll = M().applyD20Bonus(caster.state, "attack-roll-bonus-die", R().d20(spell.attackBonus, mode));
    M().consumeNextAttackAgainstAdvantage(caster.state, target.combatant_id);
    M().consumeAttacksAgainstAdvantage(target.state);
    const natural = attackRoll.selected_roll;
    const hit = natural !== 1 && (natural === 20 || attackRoll.total >= targetAc);
    const critical = Boolean(hit && (natural === 20 || (Q().autoCritical(target.state) && distance <= 5)));
    return { target, attackRoll, targetAc, hit, critical, distance };
  }

  window.IRON_PIT_BROWSER_SPELL_ATTACK_REFLECTION = { reroll };
})();
