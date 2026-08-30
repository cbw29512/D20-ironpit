(() => {
  "use strict";

  const D = () => window.IRON_PIT_PREGEN_DATA;
  const M = () => window.IRON_PIT_PREGEN_MATH;
  const A = () => window.IRON_PIT_PREGEN_ATTACKS;
  const S = () => window.IRON_PIT_PREGEN_SPELLS;

  function runtimeId(classId, level, buildId) { return `pregen-2024-${classId}-l${level}-${buildId}`; }
  function rageUses(level) { return level >= 17 ? 6 : level >= 12 ? 5 : level >= 6 ? 4 : level >= 3 ? 3 : 2; }
  function rageBonus(level) { return level >= 16 ? 4 : level >= 9 ? 3 : 2; }
  function speed(classId, level) {
    if (classId === "barbarian" && level >= 5) return 40;
    if (classId === "monk") return level >= 18 ? 60 : level >= 14 ? 55 : level >= 10 ? 50 : level >= 6 ? 45 : level >= 2 ? 40 : 30;
    if (classId === "ranger" && level >= 6) return 40;
    return 30;
  }

  function equipment(classId, buildId, level, attacks) {
    const gear = M().magic(level), primary = attacks[0]?.name || "class equipment";
    const rows = [primary];
    if (gear.armor) rows.push(`+${gear.armor} magic armor`);
    if (M().shieldUser(classId, buildId)) rows.push(gear.shield ? `+${gear.shield} magic shield` : "shield");
    for (let i = 0; i < gear.utility; i += 1) rows.push("level-appropriate utility magic item");
    return rows;
  }

  function classResources(classId, level) {
    if (classId === "barbarian") return { rage: rageUses(level) };
    if (classId === "fighter") return { "second-wind": 2 };
    return {};
  }

  function visual(classId, buildId, attacks, level) {
    let armor = "unarmored";
    if (["bard", "rogue", "ranger", "warlock", "druid"].includes(classId)) armor = level >= 5 ? "studded-leather" : "leather";
    if (["fighter", "paladin"].includes(classId) || (classId === "cleric" && buildId !== "healer")) armor = level >= 5 ? "plate" : "chain-mail";
    if (classId === "cleric" && buildId === "healer") armor = "scale-mail";
    return { armor, main_hand: attacks[0]?.id || "spell-focus", body_style: "humanoid" };
  }

  function buildTemplate(classRow, level, build) {
    const [classId, className, subclassId, subclassName] = classRow, [buildId, buildName] = build;
    const scores = M().scores(classId, level), attackSet = A().build(classId, buildId, level, scores);
    const spellSet = S().healing(classId, level, scores), classResource = classResources(classId, level);
    const template = {
      id: runtimeId(classId, level, buildId), class_id: classId, build_id: buildId,
      name: `${className} ${level} — ${buildName}`, archetype: className, level, kind: "character", size: "medium",
      subclass_id: level >= 3 ? subclassId : null, subclass_name: level >= 3 ? subclassName : null,
      ability_scores: scores, proficiency_bonus: M().proficiency(level),
      armor_class: M().armorClass(classId, buildId, level, scores), max_hp: M().maxHp(classId, level, scores),
      speed_ft: speed(classId, level), initiative_bonus: M().mod(scores.dexterity),
      saving_throw_bonuses: M().saveBonuses(classId, level, scores), skill_bonuses: M().skillBonuses(classId, level, scores),
      attacks: attackSet.attacks, primary_attack_id: attackSet.primaryAttackId,
      saving_throw_actions: S().savingThrowActions(classId, level, scores),
      healingActions: spellSet.healingActions, resources: { ...classResource, ...spellSet.resources },
      traits: [], equipment: equipment(classId, buildId, level, attackSet.attacks),
      attack_action: attackSet.attackAction, wearing_heavy_armor: ["fighter", "paladin"].includes(classId) || (classId === "cleric" && buildId !== "healer"),
      visual: visual(classId, buildId, attackSet.attacks, level),
      automation_coverage: "core-raw", full_feature_coverage: false,
      source: "D&D 2024 Free Rules / SRD 5.2.1; deterministic Iron Pit pregen chassis",
    };
    if (classId === "barbarian") template.rage_damage_bonus = rageBonus(level);
    if (classId === "sorcerer" && level >= 6) template.damage_resistances = ["fire"];
    return template;
  }

  function buildAll(skipKeys = new Set()) {
    const templates = [];
    for (const classRow of D().CLASS_ROWS) {
      const classId = classRow[0];
      for (let level = 1; level <= 20; level += 1) for (const build of D().BUILD_ROWS[classId]) {
        const key = `${classId}:${level}:${build[0]}`;
        if (!skipKeys.has(key)) templates.push(buildTemplate(classRow, level, build));
      }
    }
    return templates;
  }

  window.IRON_PIT_PREGEN_FACTORY = { buildAll, buildTemplate, runtimeId };
})();
