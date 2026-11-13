(() => {
  "use strict";

  // The generated Python classifier is the sole Wanted source of truth.
  // Cards have no runnable template, so selecting or fighting them is forbidden.
  function cards() {
    try {
      const source = window.IRON_PIT_BROWSER_WANTED_2014;
      if (!Array.isArray(source)) throw new Error("Generated 2014 Wanted registry is missing.");
      return source.map((row) => {
        if (!row.id?.startsWith("2014-") || !row.name || !Array.isArray(row.blockers) || !row.blockers.length)
          throw new Error("2014 Wanted row lacks source identity or blockers.");
        return {
          id: `catalog-${row.id}`, name: row.name,
          challenge_rating: row.challenge_rating || "?",
          monster_type: row.creature_type || null, creature_type: row.creature_type || null,
          ruleset: "2014", kind: "monster", coverage_status: "blocked",
          runnable_template_id: null, blockers: [...row.blockers],
        };
      });
    } catch (error) {
      console.error("2014 Wanted catalog construction failed.", error);
      throw error;
    }
  }

  function poster(card) {
    try {
      const article = document.createElement("article");
      article.className = "wanted-poster";
      article.setAttribute("aria-label", `${card.name}: Wanted, coming soon, not playable`);
      const kicker = document.createElement("span");
      kicker.className = "wanted-stamp";
      kicker.textContent = "WANTED";
      const artwork = document.createElement("div");
      artwork.className = "wanted-portrait";
      artwork.setAttribute("aria-hidden", "true");
      artwork.textContent = "?";
      const name = document.createElement("h3");
      name.textContent = card.name;
      const detail = document.createElement("p");
      detail.className = "wanted-details";
      detail.textContent = `CR ${card.challenge_rating} · ${card.creature_type || "Unknown type"}`;
      const status = document.createElement("p");
      status.className = "wanted-status";
      status.textContent = "COMING SOON";
      const note = document.createElement("small");
      note.textContent = "Combat certification pending · Not selectable";
      article.append(kicker, artwork, name, detail, status, note);
      return article;
    } catch (error) {
      console.error("Failed to create a source-derived Wanted poster.", error);
      throw error;
    }
  }

  function render(catalog) {
    try {
      const board = document.getElementById("wanted-board");
      const grid = document.getElementById("wanted-grid");
      const summary = document.getElementById("wanted-count");
      if (!board || !grid || !summary) throw new Error("Wanted board markup is missing.");
      board.hidden = catalog?.ruleset !== "2014";
      if (board.hidden) return;
      const blocked = catalog.monsters.filter((card) =>
        card.ruleset === "2014" && card.coverage_status === "blocked");
      summary.textContent = `${blocked.length} still wanted · ${catalog.monster_ready_count} admitted`;
      grid.replaceChildren(...blocked.map(poster));
    } catch (error) {
      console.error("Failed to render Wanted board.", error);
      throw error;
    }
  }

  window.IRON_PIT_WANTED_POSTERS = { cards, render };
})();
