(() => {
  "use strict";

  const meleeButton = document.querySelector("#fight-button");
  const rangedButton = document.querySelector("#ranged-button");
  const characterSelect = document.querySelector("#character-select");
  const monsterSelect = document.querySelector("#monster-select");
  const controls = [meleeButton, rangedButton, characterSelect, monsterSelect];
  const apiBase = String(window.IRON_PIT_API_BASE || "").trim().replace(/\/$/, "");
  const preview = window.IRON_PIT_PREVIEW;
  const catalogUI = window.createIronPitCatalogUI(characterSelect, monsterSelect);
  const arenaState = {
    fighter: { id: "aldric-vane-l1", maxHp: 12 },
    goblin: { id: "srd-goblin-warrior", maxHp: 10 },
  };

  function setControlsDisabled(disabled) {
    try { for (const control of controls) control.disabled = disabled; }
    catch (error) { console.error("Control state update failed", error); }
  }

  function staticCatalog() {
    try {
      if (!preview?.roster) throw new Error("Secure preview roster is unavailable.");
      return {
        characters: [{ combatant: preview.roster.fighter, battle_ready: true }],
        monsters: [{ combatant: preview.roster.monster, battle_ready: true }],
      };
    } catch (error) { console.error("Static catalog build failed", error); throw error; }
  }

  async function fetchCatalog() {
    try {
      if (!apiBase) return staticCatalog();
      const [charactersResponse, monstersResponse] = await Promise.all([
        fetch(`${apiBase}/api/catalog/characters`),
        fetch(`${apiBase}/api/catalog/monsters`),
      ]);
      if (!charactersResponse.ok || !monstersResponse.ok) throw new Error("Catalog API request failed.");
      return { characters: await charactersResponse.json(), monsters: await monstersResponse.json() };
    } catch (error) { console.error("Catalog request failed", error); throw error; }
  }

  function showSelectedMatchup(view, status = "Matchup ready — choose a starting distance.") {
    try {
      view.hydrateRoster(catalogUI.selectedRoster());
      view.resetArena(status, 5);
    } catch (error) { console.error("Selected matchup render failed", error); throw error; }
  }

  async function loadCatalog(view) {
    try {
      catalogUI.hydrate(await fetchCatalog());
      showSelectedMatchup(view, apiBase ? "Catalog ready — choose a starting distance." : "Secure random preview ready.");
    } catch (error) {
      console.error("Catalog load failed", error);
      view.resetArena("Arena catalog could not be loaded.", 5);
    }
  }

  async function requestBattle(startingDistance) {
    try {
      if (!apiBase) {
        if (!preview?.buildBattle) throw new Error("Secure preview engine is unavailable.");
        return preview.buildBattle(startingDistance);
      }
      const ids = catalogUI.selectedIds();
      const response = await fetch(`${apiBase}/api/battles`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          character_id: ids.characterId,
          monster_id: ids.monsterId,
          starting_distance_ft: startingDistance,
        }),
      });
      if (!response.ok) throw new Error(`Battle API returned ${response.status}`);
      return await response.json();
    } catch (error) { console.error("Battle request failed", error); throw error; }
  }

  async function startFight(view, startingDistance) {
    try {
      setControlsDisabled(true);
      view.resetArena(apiBase ? "Requesting battle..." : "Rolling secure random battle...", startingDistance);
      const battle = await requestBattle(startingDistance);
      view.hydrateRoster({ fighter: battle.fighter.template, monster: battle.monster.template });
      view.resetArena("Rolling initiative...", battle.battlefield.starting_distance_ft);
      await view.replay(battle.events);
      view.setStatus(battle.winner_name ? `${battle.winner_name} wins in round ${battle.rounds}!` : "The duel is a draw.");
    } catch (error) {
      console.error("Fight failed", error);
      view.setStatus(apiBase ? "Battle failed. Check the FastAPI deployment." : "Secure preview battle failed.");
    } finally { setControlsDisabled(false); }
  }

  try {
    const view = window.createIronPitArenaView(arenaState);
    meleeButton.addEventListener("click", () => startFight(view, 5));
    rangedButton.addEventListener("click", () => startFight(view, 90));
    characterSelect.addEventListener("change", () => showSelectedMatchup(view));
    monsterSelect.addEventListener("change", () => showSelectedMatchup(view));
    loadCatalog(view);
  } catch (error) {
    console.error("App initialization failed", error);
    document.querySelector("#status").textContent = "Arena initialization failed.";
  }
})();
