(() => {
  "use strict";

  const clone = (value) => structuredClone(value);
  const maxMap = (left = {}, right = {}) => {
    const keys = new Set([...Object.keys(left), ...Object.keys(right)]);
    return Object.fromEntries([...keys].map((key) => [key, Math.max(left[key] ?? -99, right[key] ?? -99)]));
  };

  function compile(
    original, form, retainSpellcasting = false, retainedSpellActionIds = [],
    retainCreatureType = false, retainHitPoints = false,
  ) {
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
      if (retainCreatureType) active.creature_type = original.creature_type;
      if (retainHitPoints) active.max_hp = original.max_hp;
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
      const allowed = new Set(retainedSpellActionIds || []);
      const keep = (actions) => clone((actions || []).filter((action) => allowed.has(action.id)));
      if (retainSpellcasting) {
        active.spell_save_actions = keep(original.spell_save_actions);
        active.spell_attack_actions = keep(original.spell_attack_actions);
        active.auto_hit_spell_actions = keep(original.auto_hit_spell_actions);
        active.persistent_spell_attack_actions = keep(original.persistent_spell_attack_actions);
        active.persistent_barrier_actions = keep(original.persistent_barrier_actions);
        active.defensive_spell_actions = keep(original.defensive_spell_actions);
        active.healingActions = keep(original.healingActions);
        active.condition_removal_actions = keep(original.condition_removal_actions);
        active.effect_removal_actions = keep(original.effect_removal_actions);
      } else {
        active.spell_save_actions = []; active.spell_attack_actions = []; active.auto_hit_spell_actions = [];
        active.persistent_spell_attack_actions = []; active.persistent_barrier_actions = [];
        active.defensive_spell_actions = []; active.healingActions = []; active.condition_removal_actions = []; active.effect_removal_actions = [];
      }
      return active;
    } catch (error) {
      console.error("Browser replacement-form compilation failed", { original: original?.id, form: form?.id, error });
      throw error;
    }
  }


  // Source-retaining monster Change Shape: the physical-stat layer only.
  // Additional form attacks/capabilities must be source-validated and bound
  // before any arena action can select this output as a complete transformation.
  function compileMonsterChangeShapePhysicalOverlay(original, form) {
    if (original?.kind !== "monster" || form?.kind !== "monster") {
      throw new Error("Monster Change Shape requires two monster templates.");
    }
    if (original.ruleset !== form.ruleset) {
      throw new Error("A Change Shape form must use the owner's ruleset.");
    }
    if (!/^(beast|humanoid)(?:$|[ (])/i.test(String(form.creature_type || ""))) {
      throw new Error("Change Shape form must be a humanoid or beast.");
    }
    const crValue = (cr) => {
      if (cr == null || String(cr).trim() === "") throw new Error("Change Shape requires challenge ratings.");
      const match = String(cr).trim().match(/^(\d+)(?:\/(\d+))?$/);
      if (!match || (match[2] && Number(match[2]) === 0)) throw new Error("Invalid form challenge rating.");
      return Number(match[1]) / Number(match[2] || 1);
    };
    if (crValue(form.challenge_rating) > crValue(original.challenge_rating)) {
      throw new Error("Change Shape form exceeds its source's challenge rating.");
    }
    if (!original.ability_scores || !form.ability_scores) {
      throw new Error("Change Shape requires source ability scores.");
    }
    const active = clone(original);
    active.id = `${original.id}--form-${form.id}`;
    active.armor_class = form.armor_class;
    active.speed_ft = form.speed_ft;
    active.movement_modes = clone(form.movement_modes);
    active.blindsight_ft = Number(form.blindsight_ft || 0);
    active.truesight_ft = Number(form.truesight_ft || 0);
    active.ability_scores.strength = form.ability_scores.strength;
    active.ability_scores.dexterity = form.ability_scores.dexterity;
    const mergeUnique = (source = [], gained = []) => {
      const result = clone(source || []);
      const seen = new Set(result.map((item) => JSON.stringify(item)));
      for (const item of gained || []) {
        const key = JSON.stringify(item);
        if (!seen.has(key)) { result.push(clone(item)); seen.add(key); }
      }
      return result;
    };
    // Add only the chosen legal form's *printed* defenses. The Deva retains
    // its original defenses, including qualified nonmagical-weapon resistance.
    active.damage_resistances = mergeUnique(original.damage_resistances, form.damage_resistances);
    active.damage_immunities = mergeUnique(original.damage_immunities, form.damage_immunities);
    active.condition_immunities = mergeUnique(original.condition_immunities, form.condition_immunities);
    active.conditional_damage_defenses = mergeUnique(
      original.conditional_damage_defenses, form.conditional_damage_defenses,
    );
    active.source = `${original.source}; physical Change Shape overlay: ${form.source}`;
    return active;
  }

  window.IRON_PIT_BROWSER_REPLACEMENT_FORM_COMPILER = { compile, compileMonsterChangeShapePhysicalOverlay };
})();