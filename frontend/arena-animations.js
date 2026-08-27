(() => {
  "use strict";

  function sleep(ms) {
    try { return new Promise((resolve) => setTimeout(resolve, ms)); }
    catch (error) { console.error("Animation delay failed", error); return Promise.resolve(); }
  }

  function projectileGlyph(projectile) {
    try {
      if (projectile === "arrow" || projectile === "bolt") return "➤";
      if (projectile === "javelin") return "➟";
      return "•";
    } catch (error) { console.error("Projectile glyph lookup failed", error); return "•"; }
  }

  window.createIronPitAnimations = function createIronPitAnimations(arenaState, setHp, setDistance) {
    try {
      const projectile = document.querySelector("#projectile");

      function slotForId(combatantId) {
        try { return combatantId === arenaState.fighter.id ? "fighter" : "goblin"; }
        catch (error) { console.error("Combatant slot lookup failed", error); return "goblin"; }
      }

      async function animateProjectile(event) {
        try {
          const actor = slotForId(event.actor_id);
          projectile.textContent = projectileGlyph(event.projectile);
          projectile.className = `projectile ${actor === "fighter" ? "fly-right" : "fly-left"}`;
          if (event.critical) projectile.classList.add("projectile-critical");
          await sleep(520);
          projectile.className = "projectile";
        } catch (error) { console.error("Projectile animation failed", error); }
      }

      async function animateAttack(event) {
        try {
          const actor = slotForId(event.actor_id);
          const target = actor === "fighter" ? "goblin" : "fighter";
          const actorNode = document.querySelector(`#${actor}`);
          const targetNode = document.querySelector(`#${target}`);
          const previousWeapon = actorNode.dataset.weapon;
          if (event.weapon_id) actorNode.dataset.weapon = event.weapon_id;

          if (event.animation === "projectile") await animateProjectile(event);
          else {
            actorNode.classList.add("swing");
            if (event.critical) actorNode.classList.add("critical");
            await sleep(260);
          }

          if (event.hit) targetNode.classList.add("hit");
          if (event.hp_after !== null) setHp(target, event.hp_after);
          await sleep(380);
          actorNode.classList.remove("swing", "critical");
          targetNode.classList.remove("hit");
          actorNode.dataset.weapon = previousWeapon || "none";
        } catch (error) { console.error("Attack animation failed", error); }
      }

      async function animateHealing(event) {
        try {
          const slot = slotForId(event.actor_id);
          const node = document.querySelector(`#${slot}`);
          node.classList.add("healing");
          await sleep(220);
          if (event.hp_after !== null) setHp(slot, event.hp_after);
          await sleep(420);
          node.classList.remove("healing");
        } catch (error) { console.error("Healing animation failed", error); }
      }

      async function animateMovement(event) {
        try {
          const slot = slotForId(event.actor_id);
          const node = document.querySelector(`#${slot}`);
          if (event.distance_before_ft !== null) setDistance(event.distance_before_ft);
          node.classList.add("advance");
          await sleep(280);
          if (event.distance_after_ft !== null) setDistance(event.distance_after_ft);
          await sleep(220);
          node.classList.remove("advance");
        } catch (error) { console.error("Movement animation failed", error); }
      }

      async function animateForcedMovement(event) {
        try {
          const slot = slotForId(event.target_id);
          const node = document.querySelector(`#${slot}`);
          if (event.distance_before_ft !== null) setDistance(event.distance_before_ft);
          node.classList.add("pushed");
          await sleep(280);
          if (event.distance_after_ft !== null) setDistance(event.distance_after_ft);
          await sleep(220);
          node.classList.remove("pushed");
        } catch (error) { console.error("Forced movement animation failed", error); }
      }

      async function animateCondition(event) {
        try {
          const slot = slotForId(event.target_id || event.actor_id);
          const node = document.querySelector(`#${slot}`);
          if (event.condition === "prone") node.classList.toggle("prone", event.condition_active === true);
          await sleep(320);
        } catch (error) { console.error("Condition animation failed", error); }
      }

      async function play(event) {
        try {
          if (event.event_type === "attack") return await animateAttack(event);
          if (event.event_type === "healing") return await animateHealing(event);
          if (event.event_type === "movement") return await animateMovement(event);
          if (event.event_type === "forced_movement") return await animateForcedMovement(event);
          if (event.event_type === "condition") return await animateCondition(event);
          await sleep(event.event_type === "dash" ? 220 : 300);
        } catch (error) { console.error("Battle event animation failed", error); }
      }

      return { play };
    } catch (error) {
      console.error("Animation system initialization failed", error);
      throw error;
    }
  };
})();
