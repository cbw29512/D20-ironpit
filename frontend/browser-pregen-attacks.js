(() => {
  "use strict";

  const M = () => window.IRON_PIT_PREGEN_MATH;
  const D = () => window.IRON_PIT_PREGEN_DATA;
  const attack = (id, name, kind, bonus, diceCount, diceSize, damageBonus, damageType, extra = {}) => ({
    id, name, kind, bonus, diceCount, diceSize, damageBonus, damageType, reach: kind === "melee" ? 5 : 0, ...extra,
  });
  const scale = (level) => level >= 17 ? 4 : level >= 11 ? 3 : level >= 5 ? 2 : 1;

  function weaponBonus(level) { return M().magic(level).weapon; }
  function weapon(id, name, kind, level, abilityMod, diceCount, diceSize, damageType, extra = {}) {
    const magic = weaponBonus(level), bonus = M().proficiency(level) + abilityMod + magic;
    return attack(id, magic ? `+${magic} ${name}` : name, kind, bonus, diceCount, diceSize, abilityMod + magic, damageType, extra);
  }
  function spellAttack(id, name, level, casterMod, diceCount, diceSize, damageType, extra = {}) {
    return attack(id, name, "ranged", M().proficiency(level) + casterMod, diceCount, diceSize, extra.damageBonus || 0,
      damageType, { normal: extra.range || 120, long: extra.range || 120, projectile: extra.projectile || "spell", animation: "projectile" });
  }

  function extraAttackCount(classId, buildId, level) {
    if (classId === "fighter") return level >= 20 ? 4 : level >= 11 ? 3 : level >= 5 ? 2 : 1;
    if (["barbarian", "monk", "paladin", "ranger"].includes(classId)) return level >= 5 ? 2 : 1;
    if (classId === "warlock" && buildId === "blade") return level >= 12 ? 3 : level >= 5 ? 2 : 1;
    if (classId === "warlock" && buildId !== "blade") return scale(level);
    return 1;
  }

  function martialProfile(classId, buildId, level, s) {
    const str = M().mod(s.strength), dex = M().mod(s.dexterity), cha = M().mod(s.charisma);
    const key = `${classId}:${buildId}`;
    if (key === "barbarian:great-weapon") return weapon("greataxe", "Greataxe", "melee", level, str, 1, 12, "slashing", { animation: "heavy-slash", rageEligible: true });
    if (key === "barbarian:axe-shield") return weapon("battleaxe", "Battleaxe", "melee", level, str, 1, 8, "slashing", { rageEligible: true });
    if (key === "barbarian:dual-wielder") return weapon("handaxe", "Handaxe", "melee", level, str, 1, 6, "slashing", { rageEligible: true });
    if (key === "fighter:guardian") return weapon("longsword", "Longsword", "melee", level, str, 1, 8, "slashing");
    if (key === "fighter:great-weapon") return weapon("greatsword", "Greatsword", "melee", level, str, 2, 6, "slashing", { animation: "heavy-slash" });
    if (key === "fighter:archer") return weapon("longbow", "Longbow", "ranged", level, dex, 1, 8, "piercing", { normal: 150, long: 600, projectile: "arrow", animation: "projectile" });
    if (classId === "monk") return weapon("unarmed", "Unarmed Strike", "melee", level, dex, 1, level >= 17 ? 12 : level >= 11 ? 10 : level >= 5 ? 8 : 6, "bludgeoning", { animation: "quick-strike" });
    if (key === "paladin:great-weapon") return weapon("greatsword", "Greatsword", "melee", level, str, 2, 6, "slashing", { animation: "heavy-slash" });
    if (classId === "paladin") return weapon("longsword", "Longsword", "melee", level, str, 1, 8, "slashing");
    if (key === "ranger:archer") return weapon("longbow", "Longbow", "ranged", level, dex, 1, 8, "piercing", { normal: 150, long: 600, projectile: "arrow", animation: "projectile" });
    if (classId === "ranger") return weapon("scimitar", "Scimitar", "melee", level, dex, 1, 6, "slashing", { animation: "quick-strike" });
    if (key === "rogue:archer") return weapon("shortbow", "Shortbow", "ranged", level, dex, 1, 6, "piercing", { normal: 80, long: 320, projectile: "arrow", animation: "projectile" });
    if (classId === "rogue") return weapon(buildId === "duelist" ? "rapier" : "shortsword", buildId === "duelist" ? "Rapier" : "Shortsword", "melee", level, dex, 1, buildId === "duelist" ? 8 : 6, "piercing", { animation: "quick-strike" });
    if (key === "warlock:blade") return weapon("pact-quarterstaff", "Pact Quarterstaff", "melee", level, cha, 1, 8, "bludgeoning", { animation: "quick-strike" });
    if (classId === "bard") return weapon("light-crossbow", "Light Crossbow", "ranged", level, dex, 1, 8, "piercing", { normal: 80, long: 320, projectile: "bolt", animation: "projectile" });
    return null;
  }

  function spellProfile(classId, level, s) {
    const caster = D().CLASSES[classId].caster, casterMod = caster ? M().mod(s[caster]) : 0, dice = scale(level);
    if (classId === "wizard") return spellAttack("fire-bolt", "Fire Bolt", level, casterMod, dice, 10, "fire", { damageBonus: level >= 10 ? casterMod : 0 });
    if (classId === "sorcerer") return spellAttack("fire-bolt", "Fire Bolt", level, casterMod, dice, 10, "fire", { damageBonus: level >= 6 ? casterMod : 0 });
    if (classId === "warlock") return spellAttack("eldritch-blast", "Eldritch Blast", level, casterMod, 1, 10, "force");
    if (classId === "druid") return spellAttack("produce-flame", "Produce Flame", level, casterMod, dice, 8, "fire", { range: 60 });
    return null;
  }

  function build(classId, buildId, level, s) {
    const spell = spellProfile(classId, level, s), martial = martialProfile(classId, buildId, level, s);
    const primary = (classId === "warlock" && buildId !== "blade") || ["wizard", "sorcerer", "druid"].includes(classId) ? spell : martial;
    const attacks = [primary, primary === martial ? spell : martial].filter(Boolean);
    const count = extraAttackCount(classId, buildId, level);
    const attackAction = primary && count > 1 ? { id: classId === "warlock" && buildId !== "blade" ? "eldritch-blast-beams" : "extra-attack", slots: Array.from({ length: count }, () => [primary.id]) } : null;
    return { attacks, primaryAttackId: primary?.id || null, attackAction };
  }

  window.IRON_PIT_PREGEN_ATTACKS = { build, extraAttackCount, scale };
})();
