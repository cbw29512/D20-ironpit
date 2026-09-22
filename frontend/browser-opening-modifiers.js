(() => {
  "use strict";

  function build(template) {
    try {
      const ward = template?.opening_targeting_ward;
      if (!ward) return [];
      return [{
        id: `${template.id}:${ward.source_id}:opening`,
        source_id: template.id,
        source_effect_id: ward.source_id,
        kind: "targeting-save-gate",
        save_ability: ward.save_ability || "wisdom",
        save_dc: ward.save_dc,
        ends_on_owner_attack: ward.ends_on_owner_attack !== false,
      }];
    } catch (error) {
      console.error("Failed to compile browser opening modifiers", { error, template: template?.id });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_OPENING_MODIFIERS = { build };
})();
