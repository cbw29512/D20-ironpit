(() => {
  "use strict";
  const clone = (value) => structuredClone(value);
  const abilityModifier = (scores, ability) => {
    const score = scores?.[ability];
    if (!Number.isInteger(score)) throw new Error("Attack source ability score must be an integer.");
    return Math.floor((score - 10) / 2);
  };

  function composeMonsterFormWeaponProfiles(owner, form, ownerAttackAbilities) {
    if (owner?.kind !== "monster" || form?.kind !== "monster" || owner.ruleset !== form.ruleset) {
      throw new Error("Form attacks require two same-edition monster sources.");
    }
    if (!owner.ability_scores || !form.ability_scores) {
      throw new Error("Attack rebasing requires source ability scores.");
    }
    const ownerAttacks = owner.attacks || [];
    const gainedAttacks = form.attacks || [];
    if (!ownerAttacks.length || !gainedAttacks.length ||
        new Set(ownerAttacks.map((a) => a.id)).size !== ownerAttacks.length) {
      throw new Error("Both monster sources require valid unique printed weapon attacks.");
    }
    const requiredIds = ownerAttacks.map((a) => a.id);
    const provenance = ownerAttackAbilities || {};
    if (Object.keys(provenance).length !== requiredIds.length ||
        !requiredIds.every((id) => Object.prototype.hasOwnProperty.call(provenance, id))) {
      throw new Error("Source provenance required for every retained attack ID.");
    }
    const result = ownerAttacks.map((attack) => {
      const rule = provenance[attack.id];
      if (!rule || !["strength", "dexterity", "fixed"].includes(rule.ability) ||
          typeof rule.addsAbilityToDamage !== "boolean") {
        throw new Error("Retained attack provenance must be explicit.");
      }
      let delta = 0;
      if (rule.ability === "fixed") {
        if (rule.addsAbilityToDamage || ["strength", "dexterity"].includes(attack.attackAbility)) {
          throw new Error("Fixed attacks cannot claim a physical ability modifier.");
        }
      } else {
        if (attack.attackAbility != null && attack.attackAbility !== rule.ability) {
          throw new Error("Attack ability conflicts with source provenance.");
        }
        delta = abilityModifier(form.ability_scores, rule.ability) -
          abilityModifier(owner.ability_scores, rule.ability);
        if (delta !== 0 && rule.addsAbilityToDamage && attack.fixedDamage != null) {
          throw new Error("Fixed-damage attack needs source-specific damage conversion.");
        }
      }
      const copy = clone(attack);
      copy.bonus += delta;
      copy.damageBonus = (copy.damageBonus || 0) + (rule.addsAbilityToDamage ? delta : 0);
      if (rule.ability !== "fixed") copy.attackAbility = rule.ability;
      if (copy.attackAbilityModifier != null) copy.attackAbilityModifier += delta;
      return copy;
    });
    const byId = new Map(result.map((row) => [row.id, row]));
    for (const attack of gainedAttacks) {
      if (byId.has(attack.id)) {
        if (JSON.stringify(byId.get(attack.id)) !== JSON.stringify(attack)) {
          throw new Error("Form and owner use the same attack ID with different semantics.");
        }
        continue;
      }
      const copied = clone(attack);
      result.push(copied);
      byId.set(attack.id, copied);
    }
    if (result.length > 64) throw new Error("Combined source attack inventory exceeds the bounded profile limit.");
    return result;
  }
  window.IRON_PIT_BROWSER_MONSTER_FORM_WEAPON_PROFILES = { composeMonsterFormWeaponProfiles };
})();
