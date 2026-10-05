(() => {
  "use strict";

  // ONE public-origin switch for canonical, Open Graph, Twitter, JSON-LD,
  // robots.txt, and sitemap.xml. Planned domain only — not purchased or live.
  // When Chris buys the domain and publishes, keep this exact HTTPS value.
  // .app is HSTS-preloaded; never use an unencrypted origin.
  window.IRON_PIT_SITE_URL = "https://ironpit.app";
  window.IRON_PIT_SHARE_IMAGE = "/assets/portraits/heroes/hero-2014-fighter.webp";
})();
