(() => {
  "use strict";

  function titleCase(value) {
    try { return String(value || "").replaceAll("-", " ").replace(/\b\w/g, (char) => char.toUpperCase()); }
    catch (error) { console.error("Title formatting failed", error); return String(value || ""); }
  }

  function describeTemplate(template) {
    try {
      const rank = template.level ? `${template.archetype} ${template.level}` : `CR ${template.challenge_rating}`;
      const offHand = template.visual.off_hand ? ` + ${titleCase(template.visual.off_hand)}` : "";
      const armor = template.visual.armor && template.visual.armor !== "none" ? ` · ${titleCase(template.visual.armor)}` : "";
      const alternates = template.alternate_weapon_attacks?.length
        ? ` · Alt: ${template.alternate_weapon_attacks.map((attack) => attack.weapon.name).join(", ")}`
        : "";
      return `${rank} · ${template.weapon_attack.weapon.name}${offHand}${armor}${alternates}`;
    } catch (error) { console.error("Template description failed", error); return "Combatant"; }
  }

  window.createIronPitArenaView = function createIronPitArenaView(arenaState) {
    try {
      const status = document.querySelector("#status");
      const log = document.querySelector("#battle-log");
      const distance = document.querySelector("#distance");

      function classForSlot(slot) {
        try {
          const bodyStyle = arenaState[slot].bodyStyle || (slot === "fighter" ? "humanoid" : "goblinoid");
          const shieldClass = arenaState[slot].hasShield === false ? " no-shield" : "";
          return `stick ${bodyStyle}${shieldClass}`;
        } catch (error) { console.error("Body style lookup failed", error); return "stick humanoid"; }
      }

      function setDistance(value) {
        try { distance.textContent = `${Math.max(0, Number(value) || 0)} ft`; }
        catch (error) { console.error("Distance render failed", error); }
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

      function renderTemplate(slot, template) {
        try {
          arenaState[slot].id = template.id;
          arenaState[slot].maxHp = template.max_hp;
          arenaState[slot].bodyStyle = template.visual.body_style || "humanoid";
          arenaState[slot].hasShield = template.visual.off_hand === "shield";
          const node = document.querySelector(`#${slot}`);
          node.className.baseVal = classForSlot(slot);
          document.querySelector(`#${slot}-name`).textContent = template.name;
          document.querySelector(`#${slot}-meta`).textContent = describeTemplate(template);
          node.setAttribute("aria-label", `${template.name}, ${describeTemplate(template)}`);
          setHp(slot, template.max_hp);
        } catch (error) { console.error(`Failed to render ${slot} template`, error); }
      }

      function hydrateRoster(roster) {
        try {
          renderTemplate("fighter", roster.fighter);
          renderTemplate("goblin", roster.monster);
        } catch (error) { console.error("Roster hydration failed", error); throw error; }
      }

      function resetArena(message = "Rolling initiative...", startingDistance = 5) {
        try {
          log.innerHTML = "";
          for (const slot of ["fighter", "goblin"]) {
            document.querySelector(`#${slot}`).className.baseVal = classForSlot(slot);
            setHp(slot, arenaState[slot].maxHp);
          }
          document.querySelector("#projectile").className = "projectile";
          setDistance(startingDistance);
          status.textContent = message;
        } catch (error) { console.error("Arena reset failed", error); }
      }

      function formatD20(roll) {
        try {
          const selected = roll.selected_roll ?? roll.rolls[0];
          const dice = roll.rolls.length > 1 ? `${roll.rolls.join(", ")} -> ${selected} ${roll.mode}` : `${selected}`;
          return `${dice} + ${roll.modifier} = ${roll.total}`;
        } catch (error) { console.error("D20 formatting failed", error); return "roll unavailable"; }
      }

      const animations = window.createIronPitAnimations(arenaState, setHp, setDistance);

      async function replay(events) {
        try {
          for (const event of events) {
            const item = document.createElement("li");
            let detail = event.description;
            if (event.attack_roll) detail += ` [${formatD20(event.attack_roll)}]`;
            if (event.damage_roll) {
              detail += ` Damage ${event.damage_roll.total}.`;
              if (event.damage_applied !== null && event.damage_applied !== undefined && event.damage_applied !== event.damage_roll.total) {
                detail += ` Applied ${event.damage_applied}.`;
              }
            }
            if (event.healing_roll) detail += ` Healing roll ${event.healing_roll.total}.`;
            item.textContent = detail;
            log.appendChild(item);
            item.scrollIntoView({ block: "nearest" });
            await animations.play(event);
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
