(() => {
  "use strict";

  const ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"];
  const D = () => window.IRON_PIT_PREGEN_DATA;
  const mod = (score) => Math.floor((score - 10) / 2);
  const proficiency = (level) => 2 + Math.floor((level - 1) / 4);
  const asiLevels = (classId) => classId === "fighter" ? [4, 6, 8, 12, 14, 16]
    : classId === "rogue" ? [4, 8, 10, 12, 16] : [4, 8, 12, 16];

  function increase(scores, ability, amount) {
    const index = ABILITIES.indexOf(ability);
    const room = Math.max(0, 20 - scores[index]);
    const used = Math.min(room, amount);
    scores[index] += used;
    return amount - used;
  }

  function scores(classId, level) {
    const spec = D().CLASSES[classId], values = [...spec.scores];
    for (const milestone of asiLevels(classId)) {
      if (level < milestone) break;
      let remaining = increase(values, spec.primary, 2);
      if (remaining) remaining = increase(values, spec.secondary, remaining);
      if (remaining) increase(values, "constitution", remaining);
    }
    return Object.fromEntries(ABILITIES.map((ability, index) => [ability, values[index]]));
  }

  function magic(level) {
    return {
      weapon: level >= 17 ? 3 : level >= 11 ? 2 : level >= 5 ? 1 : 0,
      armor: level >= 17 ? 1 : 0,
      shield: level >= 11 ? 1 : 0,
      utility: level >= 17 ? 2 : level >= 5 ? 1 : 0,
    };
  }

  function shieldUser(classId, buildId) {
    return ["barbarian:axe-shield", "fighter:guardian", "paladin:guardian", "cleric:guardian",
      "cleric:healer", "cleric:war-priest", "druid:wild-shaper", "druid:warden", "ranger:warden"].includes(`${classId}:${buildId}`);
  }

  function armorClass(classId, buildId, level, s) {
    const dex = mod(s.dexterity), wis = mod(s.wisdom), cha = mod(s.charisma), con = mod(s.constitution);
    const gear = magic(level), shield = shieldUser(classId, buildId) ? 2 + gear.shield : 0;
    if (classId === "barbarian") return 10 + dex + con + shield;
    if (classId === "monk") return 10 + dex + wis;
    if (classId === "sorcerer") return level >= 3 ? 10 + dex + cha : 10 + dex;
    if (classId === "wizard") return 10 + dex;
    if (classId === "warlock") return 11 + dex + (level >= 17 ? gear.armor : 0);
    if (["bard", "rogue", "ranger"].includes(classId)) return (level >= 5 ? 12 : 11) + dex + gear.armor + shield;
    if (classId === "druid") return 11 + dex + gear.armor + shield;
    if (classId === "cleric" && buildId === "healer") return 14 + Math.min(2, dex) + gear.armor + shield;
    if (["cleric", "fighter", "paladin"].includes(classId)) return (level >= 5 ? 18 : 16) + gear.armor + shield;
    return 10 + dex;
  }

  function maxHp(classId, level, s) {
    const hitDie = D().CLASSES[classId].hitDie, con = mod(s.constitution), fixed = Math.floor(hitDie / 2) + 1;
    let hp = hitDie + con + (level - 1) * (fixed + con);
    if (classId === "sorcerer" && level >= 3) hp += level;
    return Math.max(level, hp);
  }

  function saveBonuses(classId, level, s) {
    const trained = new Set(D().CLASSES[classId].saves), pb = proficiency(level);
    return Object.fromEntries(ABILITIES.map((ability) => [ability, mod(s[ability]) + (trained.has(ability) ? pb : 0)]));
  }

  function skillBonuses(classId, level, s) {
    const pb = proficiency(level), athletic = ["barbarian", "fighter", "paladin", "ranger"].includes(classId);
    const acrobatic = ["bard", "monk", "ranger", "rogue"].includes(classId);
    return { athletics: mod(s.strength) + (athletic ? pb : 0), acrobatics: mod(s.dexterity) + (acrobatic ? pb : 0) };
  }

  window.IRON_PIT_PREGEN_MATH = {
    ABILITIES, armorClass, magic, maxHp, mod, proficiency, saveBonuses, scores, shieldUser, skillBonuses,
  };
})();
