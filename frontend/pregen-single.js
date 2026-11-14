(() => {
  "use strict";
  // One immutable source pregen + one newly compiled, temporary test bag per
  // run. No alternate game resolver; the existing seeded engine owns combat.
  const $ = id => document.getElementById(id);
  const SEED = 12345;
  let active = false;

  function allCards() {
    try {
      const source = Object.values(window.IRON_PIT_BROWSER_HEROES || {});
      const cards = source.filter(card =>
        card?.kind === "character" &&
        ["2014", "2024"].includes(card.ruleset) &&
        Number.isInteger(card.level) && card.id && card.class_id);
      if (cards.length !== 480)
        throw new Error("Expected 240 certified pregens per edition; found " + cards.length);
      return cards.sort((a, b) => a.ruleset.localeCompare(b.ruleset) ||
        a.class_id.localeCompare(b.class_id) || a.level - b.level);
    } catch (error) {
      console.error("Could not enumerate source-backed individual pregens", error);
      throw error;
    }
  }

  function option(value, label) {
    const node = document.createElement("option");
    node.value = String(value);
    node.textContent = label;
    return node;
  }

  function render(cards) {
    try {
      const edition = $("single-edition").value;
      const level = $("single-level").value;
      const classId = $("single-class").value;
      const matches = cards.filter(card =>
        card.ruleset === edition && String(card.level) === level &&
        (classId === "all" || card.class_id === classId));
      const host = $("single-pregen-cards");
      const fragment = document.createDocumentFragment();
      for (const card of matches) {
        const tile = document.createElement("article");
        tile.className = "test-recipe-card";
        const title = document.createElement("h3");
        title.textContent = card.name;
        const info = document.createElement("p");
        info.textContent = edition + " · " + card.class_id +
          " · level " + card.level + " · Punching Bag (AC 10 / HP 10,000)";
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = "Fight Punching Bag";
        button.addEventListener("click", () => { void fight(card, button); });
        tile.append(title, info, button);
        fragment.append(tile);
      }
      host.replaceChildren(fragment);
      $("single-status").textContent =
        matches.length + " certified pregens ready. Choose one to run a real seeded fight.";
    } catch (error) {
      console.error("Could not render individual pregen fight cards", error);
      $("single-status").textContent = "Unable to show pregens: " + error.message;
    }
  }

  async function fight(card, button) {
    if (active) return;
    active = true;
    button.disabled = true;
    const status = $("single-status");
    status.textContent = "Fighting: " + card.name + " vs Punching Bag…";
    try {
      const sourceBefore = JSON.stringify(
        window.IRON_PIT_BROWSER_HEROES[card.id]);
      const entry = {kind: "punching_bag", edition: card.ruleset,
        source_kind: "pregen", source_id: card.id, label: card.name + " vs Punching Bag"};
      const {replay} = window.IRON_PIT_TEST_BAG_FIGHT.run(entry, SEED);
      const battle = replay.battle;
      if (!Array.isArray(battle?.events) || !battle.events.length)
        throw new Error("Canonical engine did not return a combat transcript.");
      if (JSON.stringify(window.IRON_PIT_BROWSER_HEROES[card.id]) !== sourceBefore)
        throw new Error("Immutable pregen card changed during combat.");
      const narrative = window.IRON_PIT_BATTLE_LOG_EXPORT.textFromBattle(battle);
      $("events").textContent = [
        "IRON PIT — COMPLETE PREGEN FIGHT",
        card.name + " (" + card.ruleset + " " + card.class_id +
          " L" + card.level + ") vs Punching Bag",
        "Seed " + SEED + " · Replay " + replay.diagnostic_id,
        "Outcome " + battle.outcome + " · Rounds " + battle.rounds +
          " · Events " + battle.events.length,
        "===== EVERY COMBAT ROUND =====", narrative,
        "===== FULL RAW ENGINE EVENTS (EVERY FIELD) =====",
        JSON.stringify({edition: card.ruleset, source_id: card.id,
          seed: SEED, diagnostic_id: replay.diagnostic_id,
          events: battle.events}, null, 2),
      ].join("\n");
      status.textContent = "Completed " + card.name + ": " +
        battle.rounds + " rounds, " + battle.events.length + " events.";
      $("pregen-log-panel").scrollIntoView({behavior: "smooth", block: "start"});
    } catch (error) {
      console.error("Selected single pregen fight failed", {id: card.id, error});
      $("events").textContent = "IRON PIT — COMPLETE PREGEN FIGHT\n" +
        card.name + " · " + card.ruleset + " · Seed " + SEED +
        "\nENGINE FAILURE: " + (error?.stack || String(error)) +
        "\nNo missing combat events have been invented.";
      status.textContent = "Fight failed: " + (error?.message || String(error));
    } finally {
      button.disabled = false;
      active = false;
    }
  }

  function install() {
    try {
      const cards = allCards();
      const classes = [...new Set(cards.map(card => card.class_id))].sort();
      $("single-edition").replaceChildren(option("2014", "2014"), option("2024", "2024"));
      $("single-level").replaceChildren(...Array.from({length: 20},
        (_, i) => option(i + 1, "Level " + (i + 1))));
      $("single-class").replaceChildren(option("all", "All classes"),
        ...classes.map(id => option(id, id[0].toUpperCase() + id.slice(1))));
      for (const id of ["single-edition", "single-level", "single-class"])
        $(id).addEventListener("change", () => render(cards));
      render(cards);
    } catch (error) {
      console.error("Individual pregen page could not initialize", error);
      $("single-status").textContent = "Pregen cards unavailable: " + error.message;
    }
  }
  install();
})();