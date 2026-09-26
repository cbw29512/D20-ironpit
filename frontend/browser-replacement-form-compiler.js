(() => {
  "use strict";

  const clone = (value) => structuredClone(value);
  const maxMap = (left = {}, right = {}) => {
    const keys = new Set([...Object.keys(left), ...Object.keys(right)]);
    return Object.fromEntries([...keys].map((key) => [key, Math.max(left[key] ?? -99, right[key] ?? -99)]));
  };

  function compile(original, form, retainSpellcasting = false) {
    try {
      if (original.kind !== "character") throw new Error("Replacement-form owner must be a character.");
      if (form.kind !== "monster") throw new Error("Replacement-form source must be monster-form data.");
      if (!original.ability_scores || !form.ability_scores) throw new Error("Replacement-form compilation requires ability scores.");
      const active = clone(original);
      const formOwned = [
        "creature_type", "size", "armor_class", "max_hp", "speed_ft", "attacks", "primary_attack_id",
        "attack_action", "saving_throw_actions", "traits", "damage_resistances", "damage_vulnerabilities",
        "damage_immunities", "condition_immunities", "visual", "source_trait_names", "source_reaction_names",
        "source_bonus_action_names", "source_limited_use_names", "source_legendary_action_names",
        "source_spellcasting_fingerprint", "recharge_rules",
      ];
      for (const key of formOwned) {
        if (Object.prototype.hasOwnProperty.call(form, key)) active[key] = clone(form[key]);
        else delete active[key];
      }
      active.id = `${original.id}--form-${form.id}`;
      active.name = original.name;
      active.archetype = original.archetype;
      active.level = original.level;
      active.kind = "character";
      active.ruleset = original.ruleset;
      active.ability_scores = {
        strength: form.ability_scores.strength, dexterity: form.ability_scores.dexterity, constitution: form.ability_scores.constitution,
        intelligence: original.ability_scores.intelligence, wisdom: original.ability_scores.wisdom, charisma: original.ability_scores.charisma,
      };
      active.saving_throw_bonuses = maxMap(original.saving_throw_bonuses, form.saving_throw_bonuses);
      active.skill_bonuses = maxMap(original.skill_bonuses, form.skill_bonuses);
      active.resources = clone(original.resources || {});
      active.unlimited_resources = clone(original.unlimited_resources || []);
      active.source = `${original.source}; replacement form: ${form.source}`;
      if (!retainSpellcasting) {
        active.spell_save_actions = []; active.spell_attack_actions = []; active.persistent_spell_attack_actions = [];
        active.defensive_spell_actions = []; active.healingActions = []; active.condition_removal_actions = []; active.effect_removal_actions = [];
      }
      return active;
    } catch (error) {
      console.error("Browser replacement-form compilation failed", { original: original?.id, form: form?.id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_REPLACEMENT_FORM_COMPILER = { compile };
})();