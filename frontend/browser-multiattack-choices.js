(() => {
  "use strict";
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const slotData = (slot) => Array.isArray(slot)
    ? { attackIds: slot, saveActionIds: [], requiresPreviousHit: false, sameTargetAsPrevious: false }
    : {
      attackIds: slot.attackIds || [], saveActionIds: slot.saveActionIds || [],
      requiresPreviousHit: Boolean(slot.requiresPreviousHit),
      sameTargetAsPrevious: Boolean(slot.sameTargetAsPrevious),
    };

  function validatedVariants(member) {
    try {
      const definition = member.state.template.attack_action;
      if (!definition) return [];
      if (Boolean(definition.slots?.length) === Boolean(definition.variants?.length)) throw new Error("Multiattack requires slots or variants.");
      const variants = definition.variants?.length ? definition.variants : [{ id: definition.id, slots: definition.slots }];
      if (!Array.isArray(variants) || variants.length > 16 || new Set(variants.map((v) => v.id)).size !== variants.length) throw new Error("Invalid Multiattack variants.");
      for (const variant of variants) {
        if (definition.variants?.length && typeof variant.id !== "string") throw new Error("Invalid Multiattack variant ID.");
        if (![null, undefined, "melee", "ranged"].includes(variant.attackKind)) throw new Error("Invalid sequence mode.");
        if (!Array.isArray(variant.slots) || !variant.slots.length || variant.slots.length > 8) throw new Error("Invalid Multiattack slots.");
        const first = slotData(variant.slots[0]);
        if (first.requiresPreviousHit || first.sameTargetAsPrevious) throw new Error("First Multiattack slot cannot depend on a previous slot.");
      }
      const slots = variants.flatMap((v) => v.slots);
      const attacks = new Set((member.state.template.attacks || []).map((item) => item.id));
      const saves = new Set((member.state.template.saving_throw_actions || []).map((item) => item.id));
      for (const slot of slots) {
        const data = slotData(slot);
        if (!data.attackIds.length && !data.saveActionIds.length) throw new Error("Empty Multiattack slot.");
        if (data.attackIds.length > 16 || data.saveActionIds.length > 16) throw new Error("Invalid Multiattack choice count.");
        if ((slot.requiresPreviousHit !== undefined && typeof slot.requiresPreviousHit !== "boolean")
          || (slot.sameTargetAsPrevious !== undefined && typeof slot.sameTargetAsPrevious !== "boolean")) {
          throw new Error("Invalid conditional Multiattack slot policy.");
        }
        const unknown = [...data.attackIds.filter((id) => !attacks.has(id)), ...data.saveActionIds.filter((id) => !saves.has(id))];
        if (unknown.length) throw new Error(`Unknown Multiattack IDs: ${unknown.join(", ")}`);
      }
      const byId = new Map((member.state.template.attacks || []).map((a) => [a.id, a]));
      for (const variant of variants) {
        if (variant.attackKind && variant.slots.some((slot) => slotData(slot).attackIds.some((id) => byId.get(id).kind !== variant.attackKind))) throw new Error("Multiattack variant contradicts its attack kind.");
      }
      return variants;
    } catch (error) {
      console.error("Failed browser Multiattack source validation", { id: member?.combatant_id, error });
      throw error;
    }
  }

  function saveChoice(member, setup, data, targetOverride = null) {
    try {
      const allowed = new Set(data.saveActionIds);
      const normalTargets = F().targetOrder(member, setup);
      const targets = targetOverride ? (normalTargets.includes(targetOverride) ? [targetOverride] : []) : normalTargets;
      for (const target of targets) {
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

  function sequenceDamage(member, setup, variant, mode) {
    try {
      let total = 0, previousTarget = null, previousAttackAvailable = false;
      for (const slot of variant.slots) {
        const data = slotData(slot);
        if (data.requiresPreviousHit && !previousAttackAvailable) {
          previousTarget = null; previousAttackAvailable = false; continue;
        }
        if (data.sameTargetAsPrevious && !previousTarget) {
          previousAttackAvailable = false; continue;
        }
        const targetOverride = data.sameTargetAsPrevious ? previousTarget : null;
        const choice = F().chooseSlotAttack(member, setup, data.attackIds, mode, targetOverride);
        if (choice) {
          total += F().weaponMeanDamage(choice.attack);
          previousTarget = choice.target; previousAttackAvailable = true; continue;
        }
        const saved = saveChoice(member, setup, data, targetOverride);
        const parts = saved?.save.damageComponents?.length ? saved.save.damageComponents : saved ? [saved.save] : [];
        total += parts.reduce((sum, p) => sum + (p.damageDiceCount ?? p.diceCount ?? 0) * ((p.damageDiceSize ?? p.diceSize ?? 6) + 1) / 2 + (p.damageBonus || 0), 0);
        previousTarget = saved?.target || null; previousAttackAvailable = false;
      }
      return total;
    } catch (error) { console.error("Failed Multiattack sequence scoring", { id: member?.combatant_id, error }); throw error; }
  }

  function selectSequence(member, setup) {
    try {
      const variants = validatedVariants(member);
      const melee = variants.some((v) => (!v.attackKind || v.attackKind === "melee") && v.slots.some((slot) =>
        F().chooseSlotAttack(member, setup, slotData(slot).attackIds, "melee")?.attack.kind === "melee"));
      const mode = melee ? "melee" : "ranged";
      const candidates = variants.filter((v) => !v.attackKind || v.attackKind === mode);
      candidates.sort((a, b) => sequenceDamage(member, setup, b, mode) - sequenceDamage(member, setup, a, mode));
      const variant = candidates[0];
      if (!variant || !variant.slots.some((slot) => {
        const data = slotData(slot);
        return F().chooseSlotAttack(member, setup, data.attackIds, mode) || saveChoice(member, setup, data);
      })) return null;
      return { variant, mode, slots: variant.slots };
    } catch (error) { console.error("Failed complete Multiattack selection", { id: member?.combatant_id, error }); throw error; }
  }

  function legalChoiceAvailable(member, setup) { return Boolean(selectSequence(member, setup)); }

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
      const selected = selectSequence(member, setup);
      return Boolean(selected && selected.slots.some((slot) =>
        F().chooseSlotAttack(member, setup, slotData(slot).attackIds, selected.mode)?.attack.kind === "melee"));
    } catch (error) {
      console.error("Failed browser Multiattack melee probe", { id: member?.combatant_id, error });
      throw error;
    }
  }

  function expectedDamage(member, setup) {
    try {
      const selected = selectSequence(member, setup);
      return selected ? sequenceDamage(member, setup, selected.variant, selected.mode) : 0;
    } catch (error) {
      console.error("Failed browser Multiattack damage estimate", { id: member?.combatant_id, error });
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_MULTIATTACK_CHOICES = {
    slotData, saveChoice, selectSequence, validatedVariants, available, legalChoiceAvailable, meleeAvailable, expectedDamage,
  };
})();
