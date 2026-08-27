(() => {
  "use strict";

  const meleeButton = document.querySelector("#fight-button");
  const rangedButton = document.querySelector("#ranged-button");
  const buttons = [meleeButton, rangedButton];
  const apiBase = String(window.IRON_PIT_API_BASE || "").trim().replace(/\/$/, "");
  const preview = window.IRON_PIT_PREVIEW;
  const arenaState = {
    fighter: { id: "aldric-vane-l1", maxHp: 12 },
    goblin: { id: "srd-goblin-warrior", maxHp: 10 },
  };

  function setButtonsDisabled(disabled) {
    try { for (const button of buttons) button.disabled = disabled; }
    catch (error) { console.error("Button state update failed", error); }
  }

  async function loadRoster(view) {
    try {
      if (!apiBase) {
        if (!preview?.roster) throw new Error("Secure preview roster is unavailable.");
        view.hydrateRoster(preview.roster);
        view.resetArena("Secure random preview ready — choose a starting distance.", 5);
        return;
      }
      const response = await fetch(`${apiBase}/api/roster/demo`);
      if (!response.ok) throw new Error(`Roster API returned ${response.status}`);
      view.hydrateRoster(await response.json());
      view.resetArena("Ready — choose a starting distance.", 5);
    } catch (error) {
      console.error("Roster load failed", error);
      view.resetArena("Arena data could not be loaded.", 5);
    }
  }

  async function requestBattle(endpoint) {
    try {
      if (!apiBase) {
        if (!preview?.buildBattle) throw new Error("Secure preview engine is unavailable.");
        return preview.buildBattle(endpoint.includes("ranged") ? 90 : 5);
      }
      const response = await fetch(`${apiBase}${endpoint}`, { method: "POST" });
      if (!response.ok) throw new Error(`Battle API returned ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error("Battle request failed", error);
      throw error;
    }
  }

  async function startFight(view, endpoint, fallbackDistance) {
    try {
      setButtonsDisabled(true);
      view.resetArena(apiBase ? "Requesting battle..." : "Rolling secure random battle...", fallbackDistance);
      const battle = await requestBattle(endpoint);
      view.hydrateRoster({ fighter: battle.fighter.template, monster: battle.monster.template });
      view.resetArena("Rolling initiative...", battle.battlefield.starting_distance_ft);
      await view.replay(battle.events);
      view.setStatus(battle.winner_name ? `${battle.winner_name} wins in round ${battle.rounds}!` : "The duel is a draw.");
    } catch (error) {
      console.error("Fight failed", error);
      view.setStatus(apiBase ? "Battle failed. Check the FastAPI deployment." : "Secure preview battle failed.");
    } finally {
      setButtonsDisabled(false);
    }
  }

  try {
    const view = window.createIronPitArenaView(arenaState);
    meleeButton.addEventListener("click", () => startFight(view, "/api/battles/demo", 5));
    rangedButton.addEventListener("click", () => startFight(view, "/api/battles/demo-ranged", 90));
    loadRoster(view);
  } catch (error) {
    console.error("App initialization failed", error);
    document.querySelector("#status").textContent = "Arena initialization failed.";
  }
})();
