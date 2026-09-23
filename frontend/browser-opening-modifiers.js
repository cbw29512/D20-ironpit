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
            required_effect_tags: [...(grant.required_effect_tags || [])],
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
