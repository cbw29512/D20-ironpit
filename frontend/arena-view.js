(() => {
  "use strict";

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

  window.createIronPitArenaView = function createIronPitArenaView(arenaState) {
    try {
      const status = document.querySelector("#status");
      const log = document.querySelector("#battle-log");

      function setHp(slot, current) {
        try {
          const max = arenaState[slot].maxHp;
          const safe = Math.max(0, Math.min(current, max));
          document.querySelector(`#${slot}-hp`).textContent = `${safe} / ${max} HP`;
          document.querySelector(`#${slot}-hp-bar`).style.width = `${(safe / max) * 100}%`;
          if (safe === 0) document.querySelector(`#${slot}`).classList.add("dead");
        } catch (error) { console.error("HP render failed", error); }
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

      function formatD20(roll) {
        try {
          const selected = roll.selected_roll ?? roll.rolls[0];
          const dice = roll.rolls.length > 1 ? `${roll.rolls.join(", ")} -> ${selected} ${roll.mode}` : `${selected}`;
          return `${dice} + ${roll.modifier} = ${roll.total}`;
        } catch (error) { console.error("D20 formatting failed", error); return "roll unavailable"; }
      }

      async function replay(events) {
        try {
          for (const event of events) {
            const item = document.createElement("li");
            let detail = event.description;
            if (event.attack_roll) detail += ` [${formatD20(event.attack_roll)}]`;
            if (event.damage_roll) detail += ` Damage ${event.damage_roll.total}.`;
            item.textContent = detail;
            log.appendChild(item);
            item.scrollIntoView({ block: "nearest" });
            if (event.event_type === "attack") await animateAttack(event);
            else await sleep(300);
          }
        } catch (error) { console.error("Battle replay failed", error); throw error; }
      }

      return { hydrateRoster, resetArena, replay, setStatus: (message) => { status.textContent = message; } };
    } catch (error) {
      console.error("Arena view initialization failed", error);
      throw error;
    }
  };
})();
