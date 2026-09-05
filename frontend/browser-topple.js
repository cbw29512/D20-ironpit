(() => {
  "use strict";

  const W = () => window.IRON_PIT_BROWSER_WEAPON_MASTERY;
  const S = () => window.IRON_PIT_BROWSER_SAVES;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const empty = () => ({ saveRoll: null, saveDc: null, saveSucceeded: null, applied: false });

  function proficiencyBonus(level) {
    if (!Number.isInteger(level) || level < 1 || level > 20) throw new Error(`Topple requires a certified character level; received ${level}.`);
    return 2 + Math.floor((level - 1) / 4);
  }

  function resolve(attacker, target, attack, advantageSources = 0) {
    try {
      if (!W().active(attacker.state, attack, "Topple")) return empty();
      if (!target.state.is_alive || target.state.is_dead) return empty();
      if (target.state.active_effect_ids.includes("prone") || I().immune(target.state, "prone")) return empty();
      const modifier = attack.attackAbilityModifier;
      if (!Number.isInteger(modifier)) throw new Error(`Topple attack ${attack.id || attack.name} requires an explicit attack ability modifier.`);
      const dc = 8 + modifier + proficiencyBonus(attacker.state.template.level);
      const save = S().resolveSavingThrow(target.state, "constitution", dc, false, advantageSources);
      if (!save.succeeded) target.state.active_effect_ids.push("prone");
      return { saveRoll: save.roll, saveDc: dc, saveSucceeded: save.succeeded, applied: !save.succeeded };
    } catch (error) {
      console.error("Topple mastery resolution failed.", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TOPPLE = { proficiencyBonus, resolve };
})();
