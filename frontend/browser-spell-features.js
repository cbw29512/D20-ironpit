(() => {
  "use strict";

  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const D = () => window.IRON_PIT_DICE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;

  function availableGrant(state, spellId, slotLevel) {
    try {
      for (const grant of (state.template.spell_specific_cast_grants || [])) {
        if (grant.spell_id !== spellId || grant.slot_level !== slotLevel) continue;
        if (grant.unlimited) return grant;
        if ((state.resources?.[grant.resource_id] || 0) >= (grant.resource_cost || 1)) return grant;
      }
      return null;
    } catch (error) {
      console.error("Spell-specific cast grant lookup failed", { spellId, error });
      throw error;
    }
  }

  function legalSaveSpellLevels(state, turnKey, action) {
    try {
      const levels = new Set(C().legalSlotLevels(state, turnKey, action.level, {
        higherSlotScaling: (action.upcastDicePerLevel || 0) > 0,
      }));
      if (action.level > 0 && availableGrant(state, action.id, action.level)) levels.add(action.level);
      return [...levels].sort((a, b) => a - b);
    } catch (error) {
      console.error("Legal save-spell level lookup failed", { spell: action?.id, error });
      throw error;
    }
  }

  function spendGrant(state, action, slotLevel) {
    try {
      const grant = availableGrant(state, action.id, slotLevel);
      if (!grant || grant.unlimited) return { grant, remaining: null };
      const cost = grant.resource_cost || 1;
      state.resources[grant.resource_id] -= cost;
      return { grant, remaining: state.resources[grant.resource_id] };
    } catch (error) {
      console.error("Spell-specific cast grant spend failed", { spell: action?.id, error });
      throw error;
    }
  }

  function damageMaximizerAvailable(state, action) {
    try {
      const grant = state.template.spell_damage_maximizer;
      if (!grant || action.level === 0) return false;
      if (action.level < grant.minimum_spell_level || action.level > grant.maximum_spell_level) return false;
      return Boolean((action.damageDiceCount || 0) || action.damageComponents?.length);
    } catch (error) {
      console.error("Spell damage maximizer eligibility failed", { spell: action?.id, error });
      throw error;
    }
  }

  function shouldAutoMaximize(state, action) {
    try {
      if (!damageMaximizerAvailable(state, action)) return false;
      const grant = state.template.spell_damage_maximizer;
      return (state.feature_use_counts?.[grant.source_id] || 0) < (grant.free_uses || 0);
    } catch (error) {
      console.error("Spell damage maximizer policy failed", { spell: action?.id, error });
      throw error;
    }
  }

  function maximizedRolls(action) {
    try {
      if (action.damageComponents?.length) {
        return action.damageComponents.map((part) => Array(part.diceCount || 0).fill(part.diceSize));
      }
      return Array(action.damageDiceCount || 0).fill(action.damageDiceSize);
    } catch (error) {
      console.error("Maximized spell damage roll construction failed", { spell: action?.id, error });
      throw error;
    }
  }

  function applyMaximizerCost(caster, action, setup) {
    try {
      const grant = caster.state.template.spell_damage_maximizer;
      if (!grant) return null;
      const uses = caster.state.feature_use_counts?.[grant.source_id] || 0;
      caster.state.feature_use_counts[grant.source_id] = uses + 1;
      if (uses < (grant.free_uses || 0)) return null;

      const repeatIndex = uses - (grant.free_uses || 0);
      const dicePerLevel = (grant.repeat_base_dice_per_spell_level || 2)
        + repeatIndex * (grant.repeat_increment_dice_per_spell_level || 1);
      const count = dicePerLevel * action.level;
      const rolls = D().rollMany(count, grant.self_damage_die_size || 12);
      const total = rolls.reduce((sum, roll) => sum + roll, 0);
      const hpBefore = caster.state.current_hp;
      const tempBefore = caster.state.temporary_hp || 0;
      const states = [...setup.heroes, ...setup.monsters].map((member) => member.state);
      A().applyDamage(caster.state, total, false, [grant.self_damage_type || "necrotic"], states);
      return { grant, count, rolls, total, hpBefore, hpAfter: caster.state.current_hp,
        tempBefore, tempAfter: caster.state.temporary_hp || 0 };
    } catch (error) {
      console.error("Spell damage maximizer self-damage failed", { caster: caster?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SPELL_FEATURES = {
    availableGrant, legalSaveSpellLevels, spendGrant,
    damageMaximizerAvailable, shouldAutoMaximize, maximizedRolls, applyMaximizerCost,
  };
})();
