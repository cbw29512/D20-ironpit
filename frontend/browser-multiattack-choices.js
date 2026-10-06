(() => {
  "use strict";
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const slotData = (slot) => Array.isArray(slot) ? { attackIds: slot, saveActionIds: [] }
    : { attackIds: slot.attackIds || [], saveActionIds: slot.saveActionIds || [] };

  function validatedSlots(member) {
    try {
      const definition = member.state.template.attack_action;
      if (!definition) return [];
      const slots = definition.slots;
      if (!Array.isArray(slots) || !slots.length || slots.length > 8) throw new Error("Invalid Multiattack slots.");
      const attacks = new Set((member.state.template.attacks || []).map((item) => item.id));
      const saves = new Set((member.state.template.saving_throw_actions || []).map((item) => item.id));
      for (const slot of slots) {
        const data = slotData(slot);
        if (!data.attackIds.length && !data.saveActionIds.length) throw new Error("Empty Multiattack slot.");
        const unknown = [...data.attackIds.filter((id) => !attacks.has(id)), ...data.saveActionIds.filter((id) => !saves.has(id))];
        if (unknown.length) throw new Error(`Unknown Multiattack IDs: ${unknown.join(", ")}`);
      }
      return slots;
    } catch (error) {
      console.error("Failed browser Multiattack source validation", { id: member?.combatant_id, error });
      throw error;
    }
  }

  function saveChoice(member, setup, data) {
    try {
      const allowed = new Set(data.saveActionIds);
      for (const target of F().targetOrder(member, setup)) {
        const action = (member.state.template.saving_throw_actions || []).find((item) =>
          allowed.has(item.id) && V().legalAction(item, target, F().saveDistance(member, target, item.range), member.combatant_id));
        if (action) return { target, save: action, distance: F().saveDistance(member, target, action.range) };
      }
      return null;
    } catch (error) {
      console.error("Failed browser Multiattack save choice", { id: member?.combatant_id, error });
      throw error;
    }
  }

  function legalChoiceAvailable(member, setup) {
    try {
      // Validate every slot before admitting any part of the Action.
      return validatedSlots(member).some((slot) => {
        const data = slotData(slot);
        return Boolean(F().chooseSlotAttack(member, setup, data.attackIds) || saveChoice(member, setup, data));
      });
    } catch (error) {
      console.error("Failed browser Multiattack legality", { id: member?.combatant_id, error });
      throw error;
    }
  }

  function available(member, setup) {
    try {
      return Boolean(E().available(member.state, "action") && legalChoiceAvailable(member, setup));
    } catch (error) {
      console.error("Failed browser Multiattack availability", { id: member?.combatant_id, error });
      throw error;
    }
  }

  function meleeAvailable(member, setup) {
    try {
      return validatedSlots(member).some((slot) =>
        F().chooseSlotAttack(member, setup, slotData(slot).attackIds)?.attack.kind === "melee");
    } catch (error) {
      console.error("Failed browser Multiattack melee probe", { id: member?.combatant_id, error });
      throw error;
    }
  }

  function expectedDamage(member, setup) {
    try {
      let total = 0;
      for (const slot of validatedSlots(member)) {
        const data = slotData(slot), chosen = F().chooseSlotAttack(member, setup, data.attackIds);
        if (chosen) total += F().weaponMeanDamage(chosen.attack);
        else {
          const saved = saveChoice(member, setup, data);
          if (saved) total += (saved.save.damageDiceCount || 0) * ((saved.save.damageDiceSize || 6) + 1) / 2 + (saved.save.damageBonus || 0);
        }
      }
      return total;
    } catch (error) {
      console.error("Failed browser Multiattack damage estimate", { id: member?.combatant_id, error });
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_MULTIATTACK_CHOICES = {
    slotData, saveChoice, available, legalChoiceAvailable, meleeAvailable, expectedDamage,
  };
})();
