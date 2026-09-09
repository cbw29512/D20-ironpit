(() => {
  "use strict";

  const registry = new Map();

  function register(entries) {
    try {
      for (const entry of entries || []) {
        if (!entry?.template_id || !entry?.src || !entry?.license || !entry?.source) {
          throw new Error("Combatant art entries require template_id, src, license, and source provenance.");
        }
        if (registry.has(entry.template_id)) {
          throw new Error(`Duplicate combatant art entry: ${entry.template_id}`);
        }
        registry.set(entry.template_id, Object.freeze({ ...entry }));
      }
    } catch (error) {
      console.error("Failed to register combatant artwork", { error });
      throw error;
    }
  }

  function assetFor(template) {
    try {
      if (!template?.id) return null;
      return registry.get(template.id) || null;
    } catch (error) {
      console.error("Failed to resolve combatant artwork", { templateId: template?.id, error });
      throw error;
    }
  }

  function markup(template) {
    try {
      const asset = assetFor(template);
      if (!asset) return null;
      const image = document.createElement("img");
      image.className = "portrait-image";
      image.src = asset.src;
      image.alt = asset.alt || template?.name || "Combatant artwork";
      image.loading = "lazy";
      image.decoding = "async";
      return image.outerHTML;
    } catch (error) {
      console.error("Failed to render combatant artwork", { templateId: template?.id, error });
      throw error;
    }
  }

  function provenance(template) {
    try {
      const asset = assetFor(template);
      if (!asset) return null;
      return { license: asset.license, source: asset.source };
    } catch (error) {
      console.error("Failed to resolve combatant artwork provenance", { templateId: template?.id, error });
      throw error;
    }
  }

  window.IRON_PIT_COMBATANT_ART = { assetFor, markup, provenance, register };
})();
