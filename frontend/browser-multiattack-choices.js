(() => {
  "use strict";
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const slotData = (slot) => Array.isArray(slot) ? { attackIds: slot, saveActionIds: [], previousAttack: null }
    : { attackIds: slot.attackIds || [], saveActionIds: slot.saveActionIds || [], previousAttack: slot.previousAttack ?? null };

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
        variant.slots.forEach((slot, index) => {
          const data = slotData(slot), rule = data.previousAttack;
          if (rule !== null) {
            if (typeof rule !== "object" || Array.isArray(rule) || Object.keys(rule).some(k => !["hit", "sameTarget"].includes(k))
                || typeof (rule.hit ?? false) !== "boolean" || typeof (rule.sameTarget ?? false) !== "boolean" || !(rule.hit || rule.sameTarget)) throw new Error("Invalid previous-attack requirement.");
            const previous = index ? slotData(variant.slots[index-1]) : null;
            if (!previous?.attackIds.length || previous.saveActionIds.length || !data.attackIds.length || data.saveActionIds.length) throw new Error("Previous-attack slots require an immediately preceding attack-only slot.");
          }
        });
      }
      const slots = variants.flatMap((v) => v.slots);
      const attacks = new Set((member.state.template.attacks || []).map((item) => item.id));
      const saves = new Set((member.state.template.saving_throw_actions || []).map((item) => item.id));
      for (const slot of slots) {
        const data = slotData(slot);
        if (!data.attackIds.length && !data.saveActionIds.length) throw new Error("Empty Multiattack slot.");
        if (data.attackIds.length > 16 || data.saveActionIds.length > 16) throw new Error("Invalid Multiattack choice count.");
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

  function followupTarget(data, previousHit, previousTargetId) {
    try {
      const rule = data.previousAttack;
      if (rule === null) return { eligible: true, targetId: null };
      if (previousHit == null || (rule.hit && previousHit !== true) || (rule.sameTarget && !previousTargetId)) return { eligible: false, targetId: null };
      return { eligible: true, targetId: rule.sameTarget ? previousTargetId : null };
    } catch (error) { console.error("Failed previous-attack slot condition", { previousTargetId, error }); throw error; }
  }
  function sequenceChoices(member, setup, variant, mode) {
    try {
      let previous = null;
      return variant.slots.map(slot => {
        const data = slotData(slot), followup = followupTarget(data, previous ? true : null, previous?.target.combatant_id);
        const choice = followup.eligible ? F().chooseSlotAttack(member, setup, data.attackIds, mode, followup.targetId) : null;
        const saved = followup.eligible && !choice ? saveChoice(member, setup, data) : null;
        previous = choice;
        return { choice, saved };
      });
    } catch (error) { console.error("Failed conditional sequence preview", { id: member?.combatant_id, error }); throw error; }
  }
  function sequenceDamage(member, setup, variant, mode) {
    try {
      return sequenceChoices(member, setup, variant, mode).reduce((total, { choice, saved }) => {
        if (choice) return total + F().weaponMeanDamage(choice.attack);
        const parts = saved?.save.damageComponents?.length ? saved.save.damageComponents : saved ? [saved.save] : [];
        return total + parts.reduce((sum, p) => sum + (p.damageDiceCount ?? p.diceCount ?? 0) * ((p.damageDiceSize ?? p.diceSize ?? 6) + 1) / 2 + (p.damageBonus || 0), 0);
      }, 0);
    } catch (error) { console.error("Failed Multiattack sequence scoring", { id: member?.combatant_id, error }); throw error; }
  }

  function selectSequence(member, setup) {
    try {
      const variants = validatedVariants(member);
      const melee = variants.some(v => (!v.attackKind || v.attackKind === "melee") && sequenceChoices(member, setup, v, "melee").some(({ choice }) => choice?.attack.kind === "melee"));
      const mode = melee ? "melee" : "ranged";
      const candidates = variants.filter((v) => !v.attackKind || v.attackKind === mode);
      candidates.sort((a, b) => sequenceDamage(member, setup, b, mode) - sequenceDamage(member, setup, a, mode));
      const variant = candidates[0];
      if (!variant || !sequenceChoices(member, setup, variant, mode).some(({ choice, saved }) => choice || saved)) return null;
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
      return Boolean(selected && sequenceChoices(member, setup, selected.variant, selected.mode).some(({ choice }) => choice?.attack.kind === "melee"));
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
    slotData, followupTarget, saveChoice, selectSequence, validatedVariants, available, legalChoiceAvailable, meleeAvailable, expectedDamage,
  };
})();
