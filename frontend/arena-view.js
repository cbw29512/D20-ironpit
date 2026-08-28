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
      const alternates = template.alternate_weapon_attacks?.length
        ? ` · Alt: ${template.alternate_weapon_attacks.map((attack) => attack.weapon.name).join(", ")}`
        : "";
      return `${rank} · ${template.weapon_attack.weapon.name}${offHand} · ${titleCase(template.visual.armor)}${alternates}`;
    } catch (error) { console.error("Template description failed", error); return "Combatant"; }
  }

  window.createIronPitArenaView = function createIronPitArenaView(arenaState) {
    try {
      const status = document.querySelector("#status");
      const log = document.querySelector("#battle-log");
      const distance = document.querySelector("#distance");

      function slotForId(actorId) {
        try {
          if (actorId === arenaState.fighter.id) return "fighter";
          if (actorId === arenaState.goblin.id) return "goblin";
          return null;
        } catch (error) { console.error("Arena slot lookup failed", error); return null; }
      }

      function setEffect(slot, effectId = "", label = "") {
        try {
          const chip = document.querySelector(`#${slot}-effects`);
          const node = document.querySelector(`#${slot}`);
          chip.dataset.effect = effectId;
          chip.textContent = label;
          chip.hidden = !effectId;
          node.classList.toggle("sapped", effectId === "sap");
        } catch (error) { console.error("Effect render failed", error); }
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

      function resetArena(message = "Rolling initiative...", startingDistance = 5) {
        try {
          log.innerHTML = "";
          for (const slot of ["fighter", "goblin"]) {
            document.querySelector(`#${slot}`).className.baseVal = `stick${slot === "goblin" ? " goblin" : ""}`;
            setHp(slot, arenaState[slot].maxHp);
            setEffect(slot);
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
            const actorSlot = slotForId(event.actor_id);
            const targetSlot = slotForId(event.target_id);
            const consumedSap = event.event_type === "attack"
              && actorSlot
              && document.querySelector(`#${actorSlot}-effects`).dataset.effect === "sap";
            const item = document.createElement("li");
            let detail = event.description;
            if (event.attack_roll) detail += ` [${formatD20(event.attack_roll)}]`;
            if (event.damage_roll) detail += ` Damage ${event.damage_roll.total}.`;
            if (event.healing_roll) detail += ` Healing roll ${event.healing_roll.total}.`;
            if (event.feature_id) item.classList.add("feature-event");
            item.textContent = detail;
            log.appendChild(item);
            item.scrollIntoView({ block: "nearest" });
            await animations.play(event);
            if (consumedSap) setEffect(actorSlot);
            if (event.feature_id === "sap" && targetSlot && Number(event.hp_after) > 0) {
              setEffect(targetSlot, "sap", "SAP · next attack Disadvantage");
            }
          }
        } catch (error) { console.error("Battle replay failed", error); throw error; }
      }

      return {
        hydrateRoster,
        resetArena,
        replay,
        setStatus: (message) => { status.textContent = message; },
      };
    } catch (error) {
      console.error("Arena view initialization failed", error);
      throw error;
    }
  };
})();
