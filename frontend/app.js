(() => {
  "use strict";

  const meleeButton = document.querySelector("#fight-button");
  const rangedButton = document.querySelector("#ranged-button");
  const ambushButton = document.querySelector("#rogue-button");
  const characterSelect = document.querySelector("#character-select");
  const monsterSelect = document.querySelector("#monster-select");
  const buttons = [meleeButton, rangedButton, ambushButton];
  const apiBase = String(window.IRON_PIT_API_BASE || "").trim().replace(/\/$/, "");
  const previewRoster = window.IRON_PIT_TEST_ROSTER;
  const previewEngine = window.IRON_PIT_TEST_ENGINE;
  const previewAmbush = window.IRON_PIT_TEST_AMBUSH;
  const arenaState = {
    fighter: { id: "aldric-vane-l1", maxHp: 12 },
    goblin: { id: "srd-goblin-warrior", maxHp: 10 },
  };
  let catalog = { characters: [], monsters: [] };

  function selectedCharacter() { return catalog.characters.find((item) => item.id === characterSelect.value); }
  function selectedMonster() { return catalog.monsters.find((item) => item.id === monsterSelect.value); }

  function syncControls(disabled = false) {
    try {
      const maraSelected = characterSelect.value === "mara-vale-l1";
      meleeButton.disabled = disabled;
      rangedButton.disabled = disabled;
      ambushButton.disabled = disabled || !maraSelected;
      characterSelect.disabled = disabled;
      monsterSelect.disabled = disabled;
      ambushButton.title = maraSelected ? "Mara attempts a RAW pre-combat Hide." : "Select Mara Vale to test the Rogue ambush.";
    } catch (error) { console.error("Control state update failed", error); }
  }

  function populateSelect(select, items, labeler) {
    select.innerHTML = "";
    for (const item of items) {
      const option = document.createElement("option");
      option.value = item.id;
      option.textContent = labeler(item);
      select.appendChild(option);
    }
  }

  function hydrateSelection(view, message = "Ready — choose a battle mode.") {
    try {
      const fighter = selectedCharacter();
      const monster = selectedMonster();
      if (!fighter || !monster) throw new Error("Selected matchup is unavailable.");
      view.hydrateRoster({ fighter, monster });
      view.resetArena(message, 5);
      syncControls(false);
    } catch (error) { console.error("Matchup hydration failed", error); view.setStatus("Matchup could not be loaded."); }
  }

  async function loadRulesCoverage(rulesView) {
    try {
      const endpoint = apiBase ? `${apiBase}/api/rules/coverage` : "rules-coverage.json";
      const response = await fetch(endpoint);
      if (!response.ok) throw new Error(`Rules coverage returned ${response.status}`);
      rulesView.render(await response.json());
    } catch (error) {
      console.error("Rules coverage load failed", error);
      rulesView.setError("Rules coverage could not be loaded.");
    }
  }

  async function loadCatalog(view) {
    try {
      if (apiBase) {
        const response = await fetch(`${apiBase}/api/test/roster`);
        if (!response.ok) throw new Error(`Test roster returned ${response.status}`);
        catalog = await response.json();
      } else {
        if (!previewRoster) throw new Error("Secure preview test roster is unavailable.");
        catalog = {
          characters: Object.values(previewRoster.characters),
          monsters: Object.values(previewRoster.monsters),
        };
      }
      populateSelect(characterSelect, catalog.characters, (item) => `${item.name} · ${item.archetype} ${item.level}`);
      populateSelect(monsterSelect, catalog.monsters, (item) => `${item.name} · CR ${item.challenge_rating}`);
      characterSelect.value = "aldric-vane-l1";
      monsterSelect.value = "srd-goblin-warrior";
      hydrateSelection(view, "Secure random test roster ready — choose a matchup.");
    } catch (error) {
      console.error("Test roster load failed", error);
      view.resetArena("Test roster could not be loaded.", 5);
    }
  }

  async function requestBattle(mode) {
    const characterId = characterSelect.value;
    const monsterId = monsterSelect.value;
    try {
      if (!apiBase) {
        if (mode === "ambush") return previewAmbush.buildTestAmbush(monsterId);
        return previewEngine.buildTestBattle(characterId, monsterId, mode);
      }
      const endpoint = mode === "ambush"
        ? `/api/test/ambush/${encodeURIComponent(monsterId)}`
        : `/api/test/battle/${encodeURIComponent(characterId)}/${encodeURIComponent(monsterId)}/${mode}`;
      const response = await fetch(`${apiBase}${endpoint}`, { method: "POST" });
      if (!response.ok) throw new Error(`Battle API returned ${response.status}`);
      return await response.json();
    } catch (error) { console.error("Battle request failed", error); throw error; }
  }

  async function startFight(view, mode, fallbackDistance) {
    try {
      syncControls(true);
      view.resetArena(apiBase ? "Requesting battle..." : "Rolling secure random battle...", fallbackDistance);
      const battle = await requestBattle(mode);
      view.hydrateRoster({ fighter: battle.fighter.template, monster: battle.monster.template });
      view.resetArena("Rolling initiative...", battle.battlefield.starting_distance_ft);
      await view.replay(battle.events);
      view.setStatus(battle.winner_name ? `${battle.winner_name} wins in round ${battle.rounds}!` : "The duel is a draw.");
    } catch (error) {
      console.error("Fight failed", error);
      view.setStatus(apiBase ? "Battle failed. Check the FastAPI deployment." : "Secure preview battle failed.");
    } finally { syncControls(false); }
  }

  try {
    const view = window.createIronPitArenaView(arenaState);
    const rulesView = window.createIronPitRulesView();
    characterSelect.addEventListener("change", () => hydrateSelection(view));
    monsterSelect.addEventListener("change", () => hydrateSelection(view));
    meleeButton.addEventListener("click", () => startFight(view, "melee", 5));
    rangedButton.addEventListener("click", () => startFight(view, "ranged", 20));
    ambushButton.addEventListener("click", () => startFight(view, "ambush", 60));
    syncControls(true);
    loadCatalog(view);
    loadRulesCoverage(rulesView);
  } catch (error) {
    console.error("App initialization failed", error);
    document.querySelector("#status").textContent = "Arena initialization failed.";
  }
})();
