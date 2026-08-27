(() => {
  "use strict";

  const button = document.querySelector("#fight-button");
  const status = document.querySelector("#status");
  const log = document.querySelector("#battle-log");
  const arenaState = {
    fighter: { id: "aldric-vane-l1", maxHp: 12 },
    goblin: { id: "srd-goblin-warrior", maxHp: 10 },
  };

  function sleep(ms) {
    try { return new Promise((resolve) => setTimeout(resolve, ms)); }
    catch (error) { console.error("Sleep helper failed", error); return Promise.resolve(); }
  }

  function titleCase(value) {
    try { return String(value || "").replaceAll("-", " ").replace(/\b\w/g, (char) => char.toUpperCase()); }
    catch (error) { console.error("Title formatting failed", error); return String(value || ""); }
  }

  function describeTemplate(template) {
    try {
      const rank = template.level ? `${template.archetype} ${template.level}` : `CR ${template.challenge_rating}`;
      const offHand = template.visual.off_hand ? ` + ${titleCase(template.visual.off_hand)}` : "";
      return `${rank} · ${template.weapon.name}${offHand} · ${titleCase(template.visual.armor)}`;
    } catch (error) { console.error("Template description failed", error); return "Combatant"; }
  }

  function renderTemplate(slot, template) {
    try {
      arenaState[slot].id = template.id;
      arenaState[slot].maxHp = template.max_hp;
      document.querySelector(`#${slot}-name`).textContent = template.name;
      document.querySelector(`#${slot}-meta`).textContent = describeTemplate(template);
      document.querySelector(`#${slot}`).setAttribute("aria-label", `${template.name}, ${describeTemplate(template)}`);
      setHp(slot, template.max_hp);
    } catch (error) { console.error(`Failed to render ${slot} template`, error); }
  }

  function hydrateRoster(roster) {
    try {
      renderTemplate("fighter", roster.fighter);
      renderTemplate("goblin", roster.monster);
    } catch (error) { console.error("Roster hydration failed", error); throw error; }
  }

  function setHp(slot, current) {
    try {
      const max = arenaState[slot].maxHp;
      const safe = Math.max(0, Math.min(current, max));
      document.querySelector(`#${slot}-hp`).textContent = `${safe} / ${max} HP`;
      document.querySelector(`#${slot}-hp-bar`).style.width = `${(safe / max) * 100}%`;
      if (safe === 0) document.querySelector(`#${slot}`).classList.add("dead");
    } catch (error) { console.error("HP render failed", error); }
  }

  function resetArena(message = "Rolling initiative...") {
    try {
      log.innerHTML = "";
      for (const slot of ["fighter", "goblin"]) {
        document.querySelector(`#${slot}`).className.baseVal = `stick${slot === "goblin" ? " goblin" : ""}`;
        setHp(slot, arenaState[slot].maxHp);
      }
      status.textContent = message;
    } catch (error) { console.error("Arena reset failed", error); }
  }

  async function animateAttack(event) {
    try {
      const actor = event.actor_id === arenaState.fighter.id ? "fighter" : "goblin";
      const target = actor === "fighter" ? "goblin" : "fighter";
      const actorNode = document.querySelector(`#${actor}`);
      const targetNode = document.querySelector(`#${target}`);
      actorNode.classList.add("swing");
      if (event.critical) actorNode.classList.add("critical");
      await sleep(260);
      if (event.hit) targetNode.classList.add("hit");
      if (event.hp_after !== null) setHp(target, event.hp_after);
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
        item.scrollIntoView({ block: "nearest" });
        if (event.event_type === "attack") await animateAttack(event);
        else await sleep(300);
      }
    } catch (error) { console.error("Battle replay failed", error); throw error; }
  }

  async function loadRoster() {
    try {
      const base = window.IRON_PIT_API_BASE || "http://localhost:8000";
      const response = await fetch(`${base}/api/roster/demo`);
      if (!response.ok) throw new Error(`Roster API returned ${response.status}`);
      hydrateRoster(await response.json());
      resetArena("Ready.");
    } catch (error) {
      console.error("Roster load failed", error);
      resetArena("Roster API unavailable. Enter the Pit will retry the battle API.");
    }
  }

  async function startFight() {
    try {
      button.disabled = true;
      resetArena("Requesting battle...");
      const base = window.IRON_PIT_API_BASE || "http://localhost:8000";
      const response = await fetch(`${base}/api/battles/demo`, { method: "POST" });
      if (!response.ok) throw new Error(`Battle API returned ${response.status}`);
      const battle = await response.json();
      hydrateRoster({ fighter: battle.fighter.template, monster: battle.monster.template });
      resetArena();
      await replay(battle.events);
      status.textContent = battle.winner_name ? `${battle.winner_name} wins in round ${battle.rounds}!` : "The duel is a draw.";
    } catch (error) {
      console.error("Fight failed", error);
      status.textContent = "Battle failed. Check the FastAPI deployment and CORS settings.";
    } finally { button.disabled = false; }
  }

  try {
    button.addEventListener("click", startFight);
    loadRoster();
  } catch (error) {
    console.error("App initialization failed", error);
    status.textContent = "Arena initialization failed.";
  }
})();
