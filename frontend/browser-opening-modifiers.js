(() => {
  "use strict";

  function build(template) {
    try {
      const modifiers = [];
      const ward = template?.opening_targeting_ward;
      if (ward) {
        modifiers.push({
          id: `${template.id}:${ward.source_id}:opening`,
          source_id: template.id,
          source_effect_id: ward.source_id,
          kind: "targeting-save-gate",
          save_ability: ward.save_ability || "wisdom",
          save_dc: ward.save_dc,
          ends_on_owner_attack: ward.ends_on_owner_attack !== false,
        });
      }
      for (const grant of template?.saving_throw_advantage_grants || []) {
        for (const ability of grant.abilities || []) {
          modifiers.push({
            id: `${template.id}:${grant.source_id}:save-advantage:${ability}`,
            source_id: template.id,
            source_effect_id: grant.source_id,
            source_name: grant.source_name,
            kind: "saving-throw-advantage",
            save_ability: ability,
            requires_magical_effect: Boolean(grant.requires_magical_effect),
            against_effect_tags: [...(grant.against_effect_tags || [])],
          });
        }
      }
      for (const grant of template?.passive_modifier_grants || []) {
        for (const [index, effect] of (grant.modifierEffects || []).entries()) {
          modifiers.push({
            id: `${template.id}:${grant.sourceId}:${template.id}:${index}`,
            source_id: template.id,
            source_effect_id: grant.sourceId,
            source_name: grant.sourceName,
            kind: effect.kind,
            flat_bonus: effect.flatBonus || 0,
            dice_count: effect.diceCount || 0,
            dice_size: effect.diceSize || 0,
            damage_type: effect.damageType || null,
            target_id: template.id,
            condition_id: effect.conditionId || null,
            source_creature_types: [...(effect.sourceCreatureTypes || [])],
            save_ability: effect.saveAbility || null,
            save_dc: effect.saveDc ?? null,
            consume_on_attack_against: Boolean(effect.consumeOnAttackAgainst),
            ends_on_owner_attack: Boolean(effect.endsOnOwnerAttack),
          });
        }
      }
      return modifiers;
    } catch (error) {
      console.error("Failed to compile browser opening modifiers", { error, template: template?.id });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_OPENING_MODIFIERS = { build };
})();
