(() => {
  "use strict";

  const FRONT_SLOTS = [0, 1, 2];
  const BACK_SLOTS = [3, 4, 5];
  const sideMembers = (member, setup) => member.side === "heroes" ? setup.heroes : setup.monsters;
  const enemies = (member, setup) => member.side === "heroes" ? setup.monsters : setup.heroes;
  const rankForSlot = (slot) => Number(slot) < 3 ? "front" : "back";

  function slotDefeated(member) {
    const s = member.state;
    if (s.template.kind === "character") return s.is_dead || !s.is_alive;
    return s.current_hp <= 0 || s.is_dead || !s.is_alive;
  }

  function frontOccupants(members) {
    return members.filter((item) => item.formation_rank === "front" && !slotDefeated(item));
  }

  function openFrontSlot(member, setup) {
    const occupied = new Set(frontOccupants(sideMembers(member, setup)).map((item) => item.formation_slot));
    return FRONT_SLOTS.find((slot) => !occupied.has(slot)) ?? null;
  }

  function backlineCapable(member) {
    const t = member.state.template;
    const ranged = (t.attacks || []).some((attack) => attack.kind === "ranged");
    const rangedSave = (t.saving_throw_actions || []).some((action) => Number(action.range || 0) > 5);
    return ranged || rangedSave;
  }

  function holdsBack(member, setup) {
    if (member.formation_rank !== "back" || !backlineCapable(member)) return false;
    return frontOccupants(sideMembers(member, setup)).length > 0;
  }

  function targetPool(member, setup) {
    const opposing = enemies(member, setup), front = frontOccupants(opposing);
    return front.length ? front : opposing;
  }

  function reservePlan(member, setup) {
    if (member.formation_rank !== "back" || backlineCapable(member)) return null;
    const slot = openFrontSlot(member, setup);
    return slot == null ? { type: "wait" } : { type: "advance", slot };
  }

  function advance(sequence, round, member, slot, setup) {
    const from = member.formation_slot;
    member.formation_rank = "front"; member.formation_slot = slot;
    member.position_ft = member.side === "heroes" ? 0 : setup.starting_distance_ft;
    return {
      sequence, round_number: round, event_type: "formation", actor_id: member.combatant_id,
      actor_name: member.state.template.name, feature_id: "advance-to-front", from_slot: from, to_slot: slot,
      animation: "advance", description: `${member.state.template.name} advances from the back line into front slot ${slot + 1}.`,
    };
  }

  function wait(sequence, round, member) {
    const state = member.state;
    if (!state.action_available) return null;
    state.action_available = false;
    if (!state.active_effect_ids.includes("dodge")) state.active_effect_ids.push("dodge");
    return {
      sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
      actor_name: state.template.name, feature_id: "backline-dodge", animation: "dodge",
      description: `${state.template.name} holds the back line and Dodges while waiting for a front slot.`,
    };
  }

  window.IRON_PIT_BROWSER_FORMATIONS = {
    BACK_SLOTS, FRONT_SLOTS, advance, backlineCapable, holdsBack, openFrontSlot,
    rankForSlot, reservePlan, targetPool, wait,
  };
})();
