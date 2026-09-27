(() => {
  "use strict";

  function slotSpellAvailable(state, turnKey) {
    if (!turnKey) throw new Error("Spell-slot legality requires an active turn key.");
    return state.spell_slot_expended_turn_key !== turnKey;
  }

  function legalSlotLevels(state, turnKey, printedLevel, options = {}) {
    if (printedLevel === 0) return [0];
    if (!Number.isInteger(printedLevel) || printedLevel < 1 || printedLevel > 9) {
      throw new Error("Printed spell level must be between 0 and 9.");
    }
    if (!slotSpellAvailable(state, turnKey)) return [];
    const maximum = options.higherSlotScaling ? 9 : printedLevel;
    const levels = [];
    for (let level = printedLevel; level <= maximum; level += 1) {
      if ((state.resources?.[`spell-slot-${level}`] || 0) > 0) levels.push(level);
    }
    return levels;
  }

  function markSlotSpellCast(state, turnKey) {
    if (!slotSpellAvailable(state, turnKey)) {
      throw new Error("A spell slot has already been expended to cast a spell on this turn.");
    }
    state.spell_slot_expended_turn_key = turnKey;
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
    legalSlotLevels, markSlotSpellCast, slotSpellAvailable,
    safeDamageMaximizer, maximizedRolls, resolveDamageMaximizerAfterCast,
  };
})();
