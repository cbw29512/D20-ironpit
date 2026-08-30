(() => {
  "use strict";

  const M = () => window.IRON_PIT_PREGEN_MATH;
  const A = () => window.IRON_PIT_PREGEN_ATTACKS;
  const D = () => window.IRON_PIT_PREGEN_DATA;

  function spellDc(classId, level, scores) {
    const ability = D().CLASSES[classId].caster;
    return ability ? 8 + M().proficiency(level) + M().mod(scores[ability]) : null;
  }

  function savingThrowActions(classId, level, scores) {
    if (classId !== "cleric") return [];
    return [{
      id: "sacred-flame", name: "Sacred Flame", range: 60, saveAbility: "dexterity",
      dc: spellDc(classId, level, scores), damageDiceCount: A().scale(level), damageDiceSize: 8,
      damageBonus: 0, damageType: "radiant", successDamage: "none", animation: "radiant-flame",
    }];
  }

  function firstLevelSlots(classId, level) {
    if (["bard", "cleric", "druid"].includes(classId)) return level === 1 ? 2 : level === 2 ? 3 : 4;
    if (classId === "ranger") return level <= 2 ? 2 : level <= 4 ? 3 : 4;
    return 0;
  }

  function healing(classId, level, scores) {
    const caster = D().CLASSES[classId].caster, abilityMod = caster ? M().mod(scores[caster]) : 0;
    const resources = {}, healingActions = [];
    if (["bard", "cleric", "druid"].includes(classId)) {
      resources["healing-word-slot"] = firstLevelSlots(classId, level);
      healingActions.push({
        id: "healing-word", name: "Healing Word", actionCost: "bonus_action", targetMode: "any",
        range: 60, diceCount: 2, diceSize: 4, healingBonus: abilityMod + (classId === "cleric" && level >= 3 ? 3 : 0),
        resourceId: "healing-word-slot", resourceCost: 1, animation: "healing-word",
      });
    }
    if (classId === "ranger") {
      resources["cure-wounds-slot"] = firstLevelSlots(classId, level);
      healingActions.push({
        id: "cure-wounds", name: "Cure Wounds", actionCost: "action", targetMode: "any",
        range: 5, diceCount: 2, diceSize: 8, healingBonus: abilityMod,
        resourceId: "cure-wounds-slot", resourceCost: 1, animation: "healing",
      });
    }
    if (classId === "paladin") {
      resources["lay-on-hands-points"] = level * 5;
      healingActions.push({
        id: "lay-on-hands", name: "Lay on Hands", actionCost: "bonus_action", targetMode: "any",
        range: 5, diceCount: 0, diceSize: 6, healingBonus: 5,
        resourceId: "lay-on-hands-points", resourceCost: 5, animation: "lay-on-hands",
      });
    }
    return { healingActions, resources };
  }

  window.IRON_PIT_PREGEN_SPELLS = { healing, savingThrowActions, spellDc };
})();
