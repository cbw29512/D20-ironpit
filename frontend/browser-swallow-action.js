(() => {
  "use strict";

  const SIZES = ["tiny", "small", "medium", "large", "huge", "gargantuan"];

  function choose(member, setup) {
    try {
      if (!window.IRON_PIT_ACTION_ECONOMY?.available(member.state, "action")) return null;
      for (const action of member.state.template.swallowActions || []) {
        if (!["action_attack", "attack_sequence"].includes(action.deliveryMode || "action_attack")) continue;
        if (action.maxSwallowed != null
          && (member.state.swallowed_target_ids || []).length >= action.maxSwallowed) continue;
        const attack = (member.state.template.attacks || []).find(item => item.id === action.attackId);
        if (!attack || attack.kind !== "melee") {
          throw new Error("Swallow must reference a certified melee Bite.");
        }
        const maxSize = SIZES.indexOf(action.maxTargetSize);
        if (maxSize < 0) throw new Error("Swallow has an uncertified target size.");
        const opponents = member.side === "heroes" ? setup.monsters : setup.heroes;
        for (const target of opponents) {
          const state = target.state;
          if (!state.is_alive || state.is_dead || state.current_hp <= 0 || state.swallowed) continue;
          if (SIZES.indexOf(state.template.size) < 0) {
            throw new Error("Swallow target size is uncertified.");
          }
          if (SIZES.indexOf(state.template.size) > maxSize) continue;
          if (
            action.requiresExistingGrapple
            && !(state.grapple_sources || []).some(grapple => grapple.source_id === member.combatant_id)
          ) continue;
          const distance = window.IRON_PIT_BROWSER_STATE.distance(member, target);
          if (distance > (attack.reach || 5)) continue;
          return { action, attack, target, distance };
        }
      }
      return null;
    } catch (error) {
      console.error("Browser Swallow action discovery failed.", {
        combatant: member?.combatant_id, error,
      });
      throw error;
    }
  }

  function resolve(sequence, round, member, setup, turnKey, targetId, attackId) {
    try {
      const chosen = choose(member, setup);
      if (!chosen || chosen.target.combatant_id !== targetId || chosen.action.attackId !== attackId) {
        throw new Error("Swallow candidate is no longer legal.");
      }
      if (chosen.action.deliveryMode === "attack_sequence") {
        // A source-declared held-target Action spends no additional attack roll.
        const swallow = window.IRON_PIT_BROWSER_SWALLOW;
        const economy = window.IRON_PIT_ACTION_ECONOMY;
        if (!swallow?.swallowAfterBite || !economy?.spend)
          throw new Error("Held-target containment requires universal state and Action economy.");
        economy.spend(member.state, "action");
        if (!swallow.swallowAfterBite(
          member.combatant_id, member.state, targetId,
          chosen.target.state, chosen.action, true,
        )) throw new Error("A legal held-target containment Action failed.");
        return { events: [{
          sequence, round_number: round, event_type: "feature",
          actor_id: member.combatant_id, actor_name: member.state.template.name,
          target_id: targetId, target_name: chosen.target.state.template.name,
          feature_id: chosen.action.sourceName, animation: "feature",
          applied_condition_ids: ["blinded", "restrained"],
          description: `${member.state.template.name} uses ${chosen.action.sourceName} on `
            + `Grappled ${chosen.target.state.template.name}: Blinded and Restrained.`,
        }], sequence: sequence + 1 };
      }
      const bite = { ...chosen.attack, controlEffect: null, grappleTargetPolicy: "normal" };
      const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(
        sequence, round, member, chosen.target, bite, chosen.distance,
        { spendAction: true, setup, turnKey, featureId: "swallow" },
      );
      const swallow = window.IRON_PIT_BROWSER_SWALLOW;
      if (!swallow?.swallowAfterBite) throw new Error("Swallow state runtime is not loaded.");
      if (
        event.hit
        && swallow.swallowAfterBite(
          member.combatant_id, member.state, targetId,
          chosen.target.state, chosen.action, true,
        )
      ) {
        event.description += " " + chosen.target.state.template.name
          + " is swallowed: Blinded, Restrained, and protected by total external cover.";
        event.applied_condition_ids = [
          ...new Set([...(event.applied_condition_ids || []), "blinded", "restrained"]),
        ];
      }
      return { events: [event], sequence: sequence + 1 };
    } catch (error) {
      console.error("Browser Swallow action resolution failed.", {
        combatant: member?.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SWALLOW_ACTION = { choose, resolve };
})();
