(() => {
  "use strict";

  const actionCantrip = (spellLevel, actionCost) => spellLevel === 0 && actionCost === "action";

  function spellLevelFromResourceId(resourceId) {
    if (!resourceId || !resourceId.startsWith("spell-slot-")) return null;
    const level = Number.parseInt(resourceId.slice("spell-slot-".length), 10);
    if (!Number.isInteger(level) || level < 1 || level > 9) {
      throw new Error(`Invalid spell-slot resource id ${resourceId}.`);
    }
    return level;
  }

  function spellCastAvailable(state, turnKey, spellLevel, actionCost, options = {}) {
    if (!turnKey) throw new Error("Spell-cast legality requires an active turn key.");
    if (!Number.isInteger(spellLevel) || spellLevel < 0 || spellLevel > 9) {
      throw new Error("Spell level must be between 0 and 9.");
    }
    const expendsSpellSlot = Boolean(options.expendsSpellSlot);
    if (state.template.ruleset === "2024") {
      return !(expendsSpellSlot && state.spell_slot_expended_turn_key === turnKey);
    }
    if (state.template.ruleset === "2014") {
      if (actionCost === "bonus_action") {
        return state.non_action_cantrip_spell_cast_turn_key !== turnKey;
      }
      if (actionCantrip(spellLevel, actionCost)) return true;
      return state.bonus_action_spell_cast_turn_key !== turnKey;
    }
    throw new Error(`Unsupported spellcasting ruleset ${state.template.ruleset}.`);
  }

  function markSpellCast(state, turnKey, spellLevel, actionCost, options = {}) {
    const expendsSpellSlot = Boolean(options.expendsSpellSlot);
    if (!spellCastAvailable(state, turnKey, spellLevel, actionCost, { expendsSpellSlot })) {
      throw new Error("Spell cannot be cast under the active edition's per-turn casting rule.");
    }
    if (state.template.ruleset === "2024") {
      if (expendsSpellSlot) state.spell_slot_expended_turn_key = turnKey;
      return;
    }
    if (actionCost === "bonus_action") {
      state.bonus_action_spell_cast_turn_key = turnKey;
      state.non_action_cantrip_spell_cast_turn_key = turnKey;
    } else if (!actionCantrip(spellLevel, actionCost)) {
      state.non_action_cantrip_spell_cast_turn_key = turnKey;
    }
  }

  function slotSpellAvailable(state, turnKey, options = {}) {
    return spellCastAvailable(
      state,
      turnKey,
      options.spellLevel ?? 1,
      options.actionCost || "action",
      { expendsSpellSlot: true },
    );
  }

  function markSlotSpellCast(state, turnKey, options = {}) {
    markSpellCast(
      state,
      turnKey,
      options.spellLevel ?? 1,
      options.actionCost || "action",
      { expendsSpellSlot: true },
    );
  }

  function legalSlotLevels(state, turnKey, printedLevel, options = {}) {
    if (!Number.isInteger(printedLevel) || printedLevel < 0 || printedLevel > 9) {
      throw new Error("Printed spell level must be between 0 and 9.");
    }
    const actionCost = options.actionCost || "action";
    if (printedLevel === 0) {
      return spellCastAvailable(
        state, turnKey, 0, actionCost, { expendsSpellSlot: false },
      ) ? [0] : [];
    }
    if (!slotSpellAvailable(
      state, turnKey, { spellLevel: printedLevel, actionCost },
    )) return [];
    const maximum = options.higherSlotScaling ? 9 : printedLevel;
    const levels = [];
    for (let level = printedLevel; level <= maximum; level += 1) {
      if ((state.resources?.[`spell-slot-${level}`] || 0) > 0) levels.push(level);
    }
    return levels;
  }

  function safeDamageMaximizer(state, spellId, spellLevel) {
    const grant = state.template.spell_damage_maximizer || null;
    if (!grant || !(grant.eligible_spell_ids || []).includes(spellId)) return null;
    if (spellLevel < grant.minimum_spell_level || spellLevel > grant.maximum_spell_level) return null;
    const uses = state.feature_use_counts?.[grant.source_id] || 0;
    return uses < (grant.safe_uses || 0) ? grant : null;
  }

  function maximizedRolls(count, size) {
    if (!Number.isInteger(count) || count < 0 || !Number.isInteger(size) || size < 2) {
      throw new Error("Invalid maximized spell damage dice.");
    }
    return Array(count).fill(size);
  }

  function resolveDamageMaximizerAfterCast(sequence, round, caster, setup, grant, spellLevel) {
    if (!grant) return { events: [], sequence };
    if (spellLevel < grant.minimum_spell_level || spellLevel > grant.maximum_spell_level) {
      throw new Error("Spell level is outside the maximizer's declared range.");
    }
    caster.state.feature_use_counts ||= {};
    const usesBefore = caster.state.feature_use_counts[grant.source_id] || 0;
    caster.state.feature_use_counts[grant.source_id] = usesBefore + 1;
    if (usesBefore < (grant.safe_uses || 0)) return { events: [], sequence };

    const dicePerLevel = (grant.initial_self_damage_dice_per_spell_level || 0)
      + (usesBefore - (grant.safe_uses || 0)) * (grant.self_damage_increment_per_spell_level || 0);
    const diceCount = dicePerLevel * spellLevel;
    const diceSize = grant.self_damage_dice_size || 12;
    const rolls = window.IRON_PIT_DICE.rollMany(diceCount, diceSize);
    const amount = rolls.reduce((sum, value) => sum + value, 0);
    const hpBefore = caster.state.current_hp;
    const temporaryHpBefore = caster.state.temporary_hp;
    const states = [...setup.heroes, ...setup.monsters].map((member) => member.state);
    const attackRuntime = window.IRON_PIT_BROWSER_ATTACK;
    if (!attackRuntime?.applyDamage) throw new Error("Spell damage maximizer requires browser damage runtime.");
    attackRuntime.applyDamage(
      caster.state, amount, false, amount > 0 ? [grant.self_damage_type || "necrotic"] : [], states,
    );
    const event = {
      sequence, round_number: round, event_type: "feature",
      actor_id: caster.combatant_id, actor_name: caster.state.template.name,
      target_id: caster.combatant_id, target_name: caster.state.template.name,
      feature_id: grant.source_id,
      damage_roll: {
        notation: `${diceCount}d${diceSize}`, rolls, modifier: 0, total: amount,
      },
      damage_components: [{
        source: grant.source_name,
        notation: `${diceCount}d${diceSize}`,
        rolls, modifier: 0, damage_type: grant.self_damage_type || "necrotic",
        total: amount, applied_total: amount,
      }],
      hp_before: hpBefore, hp_after: caster.state.current_hp,
      temporary_hp_before: temporaryHpBefore, temporary_hp_after: caster.state.temporary_hp,
      animation: "spell-overchannel",
      description: `${caster.state.template.name} suffers ${grant.source_name} self-damage after maximizing a level ${spellLevel} spell.`,
    };
    return { events: [event], sequence: sequence + 1 };
  }

  window.IRON_PIT_BROWSER_SPELLCASTING = {
    legalSlotLevels, markSlotSpellCast, slotSpellAvailable, markSpellCast, spellCastAvailable,
    spellLevelFromResourceId,
    safeDamageMaximizer, maximizedRolls, resolveDamageMaximizerAfterCast,
  };
})();
