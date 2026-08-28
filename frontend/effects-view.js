((root) => {
  "use strict";

  function updateEffectStore(store, changes = []) {
    try {
      const touched = new Set();
      for (const change of changes || []) {
        if (!change?.actor_id || !change?.effect_id) continue;
        if (!store.has(change.actor_id)) store.set(change.actor_id, new Map());
        const actorEffects = store.get(change.actor_id);
        if (change.operation === "remove") actorEffects.delete(change.effect_id);
        else if (change.operation === "apply") actorEffects.set(change.effect_id, change);
        touched.add(change.actor_id);
      }
      return touched;
    } catch (error) {
      console.error("Combat-card effect state update failed", error);
      throw error;
    }
  }

  function chipText(effect) {
    try {
      const prefix = effect.kind === "buff" ? "BUFF" : "DEBUFF";
      return `${prefix} · ${effect.label || effect.effect_id}`;
    } catch (error) {
      console.error("Combat-card effect label failed", error);
      return "EFFECT";
    }
  }

  function createIronPitEffectView(slotForId) {
    const store = new Map();

    function renderActor(actorId) {
      try {
        const slot = slotForId(actorId);
        if (!slot) return;
        const container = document.querySelector(`#${slot}-effects`);
        container.innerHTML = "";
        const effects = [...(store.get(actorId)?.values() || [])];
        effects.sort((a, b) => String(a.kind).localeCompare(String(b.kind)));
        for (const effect of effects) {
          const chip = document.createElement("span");
          chip.className = "effect-chip";
          chip.dataset.kind = effect.kind || "debuff";
          chip.dataset.effect = effect.effect_id;
          chip.textContent = chipText(effect);
          if (effect.detail) chip.title = effect.detail;
          container.appendChild(chip);
        }
        container.closest(".effects").hidden = effects.length === 0;
      } catch (error) {
        console.error("Combat-card effect render failed", error);
      }
    }

    function applyChanges(changes = []) {
      try {
        for (const actorId of updateEffectStore(store, changes)) renderActor(actorId);
      } catch (error) {
        console.error("Combat-card effect application failed", error);
        throw error;
      }
    }

    function resetAll() {
      try {
        store.clear();
        for (const slot of ["fighter", "goblin"]) {
          const container = document.querySelector(`#${slot}-effects`);
          container.innerHTML = "";
          container.closest(".effects").hidden = true;
        }
      } catch (error) {
        console.error("Combat-card effect reset failed", error);
      }
    }

    return { applyChanges, resetAll };
  }

  root.createIronPitEffectView = createIronPitEffectView;
  if (typeof module !== "undefined" && module.exports) {
    module.exports = { chipText, updateEffectStore };
  }
})(typeof window !== "undefined" ? window : globalThis);
