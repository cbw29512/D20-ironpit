(() => {
  "use strict";

  const registry = new Map();

  function entryKey(entry) {
    return entry?.portrait_id || entry?.template_id || "";
  }

  function portraitId(template) {
    try {
      if (!template) return null;
      if (template.portrait_id) return String(template.portrait_id);
      if (template.kind === "character" && template.class_id && template.ruleset) {
        return `hero-${template.ruleset}-${template.class_id}`;
      }
      const raw = String(template.id || "");
      if (!raw) return null;
      if (template.kind === "character") return raw.replace(/-l\d+$/i, "") || raw;
      return raw;
    } catch (error) {
      console.error("Failed to derive combatant portrait id", { templateId: template?.id, error });
      throw error;
    }
  }

  function candidateIds(template) {
    const ids = [];
    const push = (value) => { if (value && !ids.includes(value)) ids.push(value); };
    push(portraitId(template));
    push(template?.id);
    push(String(template?.id || "").replace(/-l\d+$/i, ""));
    return ids;
  }

  function register(entries) {
    try {
      for (const entry of entries || []) {
        const key = entryKey(entry);
        if (!key || !entry?.src || !entry?.license || !entry?.source) {
          throw new Error("Combatant art entries require portrait_id or template_id, plus src, license, and source.");
        }
        if (registry.has(key)) throw new Error(`Duplicate combatant art entry: ${key}`);
        registry.set(key, Object.freeze({ ...entry, portrait_id: key }));
      }
    } catch (error) {
      console.error("Failed to register combatant artwork", { error });
      throw error;
    }
  }

  function assetFor(template) {
    try {
      for (const key of candidateIds(template)) {
        const asset = registry.get(key);
        if (asset) return asset;
      }
      return null;
    } catch (error) {
      console.error("Failed to resolve combatant artwork", { templateId: template?.id, error });
      throw error;
    }
  }

  function attr(value) {
    return String(value || "").replace(/[&<>"']/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[char]));
  }

  function markup(template) {
    try {
      const asset = assetFor(template);
      if (!asset) return null;
      const srcset = asset.srcset ? ` srcset="${attr(asset.srcset)}"` : "";
      const position = asset.object_position ? ` style="object-position:${attr(asset.object_position)}"` : "";
      const alt = attr(asset.alt || template?.name || "Combatant artwork");
      const sizes = attr(asset.sizes || "(max-width: 620px) 42vw, 12rem");
      const kind = template?.kind === "character" ? "portrait-image-hero" : "portrait-image-monster";
      return `<img class="portrait-image ${kind}" src="${attr(asset.src)}"${srcset} sizes="${sizes}" alt="${alt}" loading="lazy" decoding="async" onerror="this.classList.add('is-broken');this.removeAttribute('src');const frame=this.closest('.fighter-portrait');if(frame)frame.classList.add('art-broken');"${position}>`;
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

  window.IRON_PIT_COMBATANT_ART = { assetFor, candidateIds, markup, portraitId, provenance, register };
})();
