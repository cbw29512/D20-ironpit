(() => {
  "use strict";

  function origin() {
    try {
      const raw = String(window.IRON_PIT_SITE_URL || "").trim();
      if (!raw) return "";
      const url = new URL(raw);
      if (url.protocol !== "https:") {
        throw new Error("IRON_PIT_SITE_URL must be https:// because .app is HSTS-preloaded.");
      }
      return url.origin;
    } catch (error) {
      console.error("Iron Pit site origin is invalid", { error });
      return "";
    }
  }

  function abs(path) {
    const root = origin();
    const clean = String(path || "/").startsWith("/") ? path : `/${path}`;
    return root ? `${root}${clean}` : clean;
  }

  function set(selector, attr, value) {
    const node = document.querySelector(selector);
    if (node && value) node.setAttribute(attr, value);
  }

  function apply() {
    try {
      const page = abs("/");
      const image = abs(window.IRON_PIT_SHARE_IMAGE || "/assets/portraits/heroes/hero-2014-fighter.webp");
      set('link[rel="canonical"]', "href", page);
      set('meta[property="og:url"]', "content", page);
      set('meta[property="og:image"]', "content", image);
      set('meta[name="twitter:image"]', "content", image);
      const json = document.getElementById("iron-pit-jsonld");
      if (!json) return;
      const data = JSON.parse(json.textContent);
      const nodes = Array.isArray(data["@graph"]) ? data["@graph"] : [data];
      for (const node of nodes) {
        if (node["@type"] === "WebSite" || node["@type"] === "SoftwareApplication") node.url = page;
        if (node.image) node.image = image;
      }
      json.textContent = JSON.stringify(data);
    } catch (error) {
      console.error("Iron Pit SEO tags could not be applied from IRON_PIT_SITE_URL", { error });
    }
  }

  apply();
})();
