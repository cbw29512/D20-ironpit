(() => {
  "use strict";
  const DIE_KINDS = new Set(["attack-roll-bonus-die", "saving-throw-bonus-die", "ability-check-bonus-die", "bonus-damage"]);
  const KINDS = new Set(["armor-class", ...DIE_KINDS, "attack-roll-advantage", "attack-roll-disadvantage", "ability-check-disadvantage", "attacks-against-advantage", "next-attack-advantage", "next-attack-against-advantage", "next-attack-disadvantage", "speed", "healing-prevented"]);
  const EFFECT_KINDS = new Set(["attacks-against-advantage", "next-attack-advantage", "next-attack-disadvantage", "speed", "healing-prevented"]);
  const D = () => window.IRON_PIT_DICE;
  function validate(item) {
    if (!item?.id || !item.source_id || !item.source_effect_id || !KINDS.has(item.kind)) throw new Error("Invalid combat modifier.");
    const count = item.dice_count || 0, sides = item.dice_size || 0;
    if (DIE_KINDS.has(item.kind) ? count < 1 || sides < 2 : count || sides) throw new Error(`Invalid dice for ${item.kind}.`);
    if (item.kind === "bonus-damage" ? !item.damage_type : item.damage_type) throw new Error(`Invalid damage type for ${item.kind}.`);
    if (new Set(["attack-roll-advantage", "attack-roll-disadvantage", "ability-check-disadvantage", "attacks-against-advantage", "next-attack-advantage", "next-attack-against-advantage", "next-attack-disadvantage"]).has(item.kind) && (item.flat_bonus || 0)) throw new Error("Attack roll-mode modifiers do not accept a flat bonus.");
    if (item.kind === "speed" && !(item.flat_bonus || 0)) throw new Error("Speed modifiers require a nonzero flat bonus.");
    if (item.kind === "next-attack-against-advantage" && !item.target_id) throw new Error("Target-scoped attack Advantage requires a target id.");
    if (item.consume_on_attack_against && item.kind !== "attacks-against-advantage") throw new Error("Only defender-wide attack Advantage can use consume_on_attack_against.");
    if (item.expires_source_turn_end_round != null && item.expires_source_turn_end_round < 1) throw new Error("Modifier expiry round must be positive.");
    if ((item.expires_current_turn_end_owner_id == null) !== (item.expires_current_turn_end_round == null)) throw new Error("Current-turn modifier expiry requires owner and round.");
    return item;
  }
  function add(state, modifier) {
    validate(modifier);
    const existing = (state.active_modifiers || []).find((item) => item.id === modifier.id);
    if (existing) {
      if (JSON.stringify(existing) === JSON.stringify(modifier)) return;
      throw new Error(`Modifier id ${modifier.id} already exists with different data.`);
    }
    state.active_modifiers.push({ ...modifier });
  }
  function removeSource(states, sourceId, effectId, concentrationOnly = false) {
    let removed = 0;
    for (const state of states || []) {
      const before = state.active_modifiers.length;
      state.active_modifiers = state.active_modifiers.filter((item) => !(item.source_id === sourceId
        && item.source_effect_id === effectId && (!concentrationOnly || item.concentration_required)));
      removed += before - state.active_modifiers.length;
    }
    return removed;
  }
  function expireSourceTurnStart(states, sourceId) {
    let removed = 0;
    for (const state of states || []) {
      const before = state.active_modifiers.length;
      state.active_modifiers = state.active_modifiers.filter((item) => !(item.source_id === sourceId && item.expires_at_start_of_source_turn));
      removed += before - state.active_modifiers.length;
    }
    return removed;
  }

  function expireSourceTurn(states, sourceId, round) {
    let removed = 0;
    for (const state of states || []) {
      const before = state.active_modifiers.length;
      state.active_modifiers = state.active_modifiers.filter((item) => !(
        (item.source_id === sourceId && item.expires_source_turn_end_round != null && item.expires_source_turn_end_round <= round)
        || (item.expires_current_turn_end_owner_id === sourceId && item.expires_current_turn_end_round != null && item.expires_current_turn_end_round <= round)
      ));
      removed += before - state.active_modifiers.length;
    }
    return removed;
  }

  function expireTargetTurn(state) {
    const before = state.active_modifiers.length;
    state.active_modifiers = state.active_modifiers.filter((item) => !(item.expires_at_end_of_target_turn
      || (item.expires_target_turn_serial != null && item.expires_target_turn_serial <= (state.turn_serial || 0))));
    return before - state.active_modifiers.length;
  }
  function applyEffect(state, sourceId, sourceEffectId, effect, index, trigger, round = null, turnOwnerId = null) {
    try {
      if (!EFFECT_KINDS.has(effect.kind)) throw new Error(`Unsupported combat modifier effect kind: ${effect.kind}.`);
      if (effect.expiresAtEndOfSourceTurn && round == null) throw new Error("End-of-source-turn modifier requires the current round.");
      if (effect.expiresAtEndOfCurrentTurn && (round == null || !turnOwnerId)) throw new Error("End-of-current-turn modifier requires round and turn owner.");
      add(state, {
        id: `${sourceId}:${sourceEffectId}:${trigger}-modifier:${index}`, source_id: sourceId, source_effect_id: sourceEffectId,
        kind: effect.kind, flat_bonus: effect.flatBonus || 0,
        consume_on_attack_against: Boolean(effect.consumeOnAttackAgainst),
        expires_at_start_of_source_turn: Boolean(effect.expiresAtStartOfSourceTurn),
        expires_at_end_of_target_turn: Boolean(effect.expiresAtEndOfTargetTurn),
        expires_source_turn_end_round: effect.expiresAtEndOfSourceTurn ? round : null,
        expires_current_turn_end_owner_id: effect.expiresAtEndOfCurrentTurn ? turnOwnerId : null,
        expires_current_turn_end_round: effect.expiresAtEndOfCurrentTurn ? round : null,
      });
    } catch (error) {
      console.error("Failed browser combat modifier application.", { sourceEffectId, error });
      throw error;
    }
  }

  function applyHitEffects(state, sourceId, attack, round = null) {
    try {
      for (const [index, effect] of (attack.onHitModifiers || []).entries()) {
        applyEffect(state, sourceId, attack.id, effect, index, "hit", round);
      }
    } catch (error) {
      console.error("Failed browser target hit modifiers.", { attack: attack?.id, error });
      throw error;
    }
  }
  const flat = (state, kind) => (state.active_modifiers || []).filter((item) => item.kind === kind)
    .reduce((sum, item) => sum + (item.flat_bonus || 0), 0);
  const effectiveArmorClass = (state) => Math.max(0, state.template.armor_class + flat(state, "armor-class"));
  const speedMultiplier = (state) => Math.min(1, ...(state.timed_effects || []).filter((effect) =>
    effect.speed_multiplier !== 1 && (!effect.requires_active_effect_id || state.active_effect_ids.includes(effect.requires_active_effect_id)))
    .map((effect) => effect.speed_multiplier));
  const effectiveSpeed = (state) => Math.max(0, Math.trunc((state.template.speed_ft + flat(state, "speed")) * speedMultiplier(state)));
  const attackRollAdvantage = (state) => (state.active_modifiers || []).filter((item) => item.kind === "attack-roll-advantage").length;
  const attackRollDisadvantage = (state) => (state.active_modifiers || []).filter((item) => item.kind === "attack-roll-disadvantage").length, abilityCheckDisadvantage = (state) => (state.active_modifiers || []).filter((item) => item.kind === "ability-check-disadvantage").length;
  const attacksAgainstAdvantage = (state) => (state.active_modifiers || []).filter((item) => item.kind === "attacks-against-advantage").length;
  const nextAttackAdvantage = (state) => (state.active_modifiers || []).filter((item) => item.kind === "next-attack-advantage").length;
  const nextAttackAgainstAdvantage = (state, targetId) => (state.active_modifiers || [])
    .filter((item) => item.kind === "next-attack-against-advantage" && item.target_id === targetId).length;
  const nextAttackDisadvantage = (state) => (state.active_modifiers || []).filter((item) => item.kind === "next-attack-disadvantage").length;

  function consumeAttacksAgainstAdvantage(state) {
    const before = state.active_modifiers.length;
    state.active_modifiers = state.active_modifiers.filter((item) => !(item.kind === "attacks-against-advantage" && item.consume_on_attack_against));
    return before - state.active_modifiers.length;
  }

  function consumeNextAttackAgainstAdvantage(state, targetId) {
    const before = state.active_modifiers.length;
    state.active_modifiers = state.active_modifiers.filter((item) => !(item.kind === "next-attack-against-advantage" && item.target_id === targetId));
    return before - state.active_modifiers.length;
  }
  function consumeNextAttackAdvantage(state) { const before = state.active_modifiers.length; state.active_modifiers = state.active_modifiers.filter((item) => item.kind !== "next-attack-advantage"); return before - state.active_modifiers.length; }
  function consumeNextAttackDisadvantage(state) { const before = state.active_modifiers.length; state.active_modifiers = state.active_modifiers.filter((item) => item.kind !== "next-attack-disadvantage"); return before - state.active_modifiers.length; }

  function applyD20Bonus(state, kind, roll) {
    if (!new Set(["attack-roll-bonus-die", "saving-throw-bonus-die", "ability-check-bonus-die"]).has(kind)) throw new Error(`${kind} is not a D20 bonus modifier.`);
    const modifiers = (state.active_modifiers || []).filter((item) => item.kind === kind);
    if (!modifiers.length) return roll;
    const bonusDice = modifiers.map((item) => {
      const rolls = Array.from({ length: item.dice_count }, () => D().roll(item.dice_size));
      return { source_effect_id: item.source_effect_id, notation: `${item.dice_count}d${item.dice_size}`, rolls,
        total: rolls.reduce((sum, value) => sum + value, 0) };
    });
    const bonusRolls = bonusDice.flatMap((item) => item.rolls);
    return { ...roll,
      notation: [roll.notation, ...bonusDice.map((item) => item.notation)].join(" + "),
      rolls: [...roll.rolls, ...bonusRolls], bonus_dice: bonusDice,
      total: roll.total + bonusRolls.reduce((a, b) => a + b, 0) };
  }

  const bonusDamage = (state, targetId) => (state.active_modifiers || []).filter((item) => item.kind === "bonus-damage"
    && (!item.target_id || item.target_id === targetId));

  window.IRON_PIT_BROWSER_MODIFIERS = {
    add, abilityCheckDisadvantage, applyD20Bonus, applyEffect, applyHitEffects, attackRollAdvantage, attackRollDisadvantage, attacksAgainstAdvantage, bonusDamage, consumeAttacksAgainstAdvantage,
    consumeNextAttackAdvantage, consumeNextAttackAgainstAdvantage, consumeNextAttackDisadvantage, effectiveArmorClass, effectiveSpeed, expireSourceTurn, expireSourceTurnStart,
    expireTargetTurn, nextAttackAdvantage, nextAttackAgainstAdvantage, nextAttackDisadvantage, removeSource, validate,
  };
})();
