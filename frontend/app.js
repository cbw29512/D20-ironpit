(() => {
  "use strict";
  const fighterMax = 12;
  const goblinMax = 10;
  const button = document.querySelector("#fight-button");
  const status = document.querySelector("#status");
  const log = document.querySelector("#battle-log");

  function sleep(ms) {
    try { return new Promise((resolve) => setTimeout(resolve, ms)); }
    catch (error) { console.error("Sleep helper failed", error); return Promise.resolve(); }
  }

  function setHp(id, current, max) {
    try {
      const safe = Math.max(0, Math.min(current, max));
      document.querySelector(`#${id}-hp`).textContent = `${safe} / ${max} HP`;
      document.querySelector(`#${id}-hp-bar`).style.width = `${(safe / max) * 100}%`;
      if (safe === 0) document.querySelector(`#${id}`).classList.add("dead");
    } catch (error) { console.error("HP render failed", error); }
  }

  function resetArena() {
    try {
      log.innerHTML = "";
      for (const id of ["fighter", "goblin"]) document.querySelector(`#${id}`).className.baseVal = `stick${id === "goblin" ? " goblin" : ""}`;
      setHp("fighter", fighterMax, fighterMax);
      setHp("goblin", goblinMax, goblinMax);
      status.textContent = "Rolling initiative...";
    } catch (error) { console.error("Arena reset failed", error); }
  }

  async function animateAttack(event) {
    try {
      const actor = event.actor_id === "aldric-vane-l1" ? "fighter" : "goblin";
      const target = actor === "fighter" ? "goblin" : "fighter";
      const actorNode = document.querySelector(`#${actor}`);
      const targetNode = document.querySelector(`#${target}`);
      actorNode.classList.add("swing");
      if (event.critical) actorNode.classList.add("critical");
      await sleep(260);
      if (event.hit) targetNode.classList.add("hit");
      if (event.hp_after !== null) setHp(target, event.hp_after, target === "fighter" ? fighterMax : goblinMax);
      await sleep(420);
      actorNode.classList.remove("swing", "critical");
      targetNode.classList.remove("hit");
    } catch (error) { console.error("Attack animation failed", error); }
  }

  async function replay(events) {
    try {
      for (const event of events) {
        const item = document.createElement("li");
        let detail = event.description;
        if (event.attack_roll) detail += ` [${event.attack_roll.rolls.join(", ")} + ${event.attack_roll.modifier} = ${event.attack_roll.total}]`;
        if (event.damage_roll) detail += ` Damage ${event.damage_roll.total}.`;
        item.textContent = detail;
        log.appendChild(item);
        item.scrollIntoView({block:"nearest"});
        if (event.event_type === "attack") await animateAttack(event);
        else await sleep(300);
      }
    } catch (error) { console.error("Battle replay failed", error); throw error; }
  }

  async function startFight() {
    try {
      button.disabled = true;
      resetArena();
      const base = window.IRON_PIT_API_BASE || "http://localhost:8000";
      const response = await fetch(`${base}/api/battles/demo`, {method:"POST"});
      if (!response.ok) throw new Error(`Battle API returned ${response.status}`);
      const battle = await response.json();
      await replay(battle.events);
      status.textContent = battle.winner_name ? `${battle.winner_name} wins in round ${battle.rounds}!` : "The duel is a draw.";
    } catch (error) {
      console.error("Fight failed", error);
      status.textContent = "Battle failed. Check that the FastAPI server is running.";
    } finally { button.disabled = false; }
  }

  try { button.addEventListener("click", startFight); resetArena(); status.textContent = "Ready."; }
  catch (error) { console.error("App initialization failed", error); status.textContent = "Arena initialization failed."; }
})();
