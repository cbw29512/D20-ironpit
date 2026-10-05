(() => {
  "use strict";

  const HIT_KINDS = new Set(["attacks-against-advantage", "speed"]);
  const D = () => window.IRON_PIT_DICE, X = () => window.IRON_PIT_BROWSER_EXHAUSTION;
  const C = () => window.IRON_PIT_BROWSER_DEBUFF_COUNTERS || { prevented: () => false };
  const validate = (item) => window.IRON_PIT_BROWSER_MODIFIER_VALIDATION.validate(item);

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
      state.active_modifiers = state.active_modifiers.filter((item) => !(item.source_id === sourceId
        && item.expires_source_turn_end_round != null && item.expires_source_turn_end_round <= round));
      removed += before - state.active_modifiers.length;
    }
    return removed;
  }

  function expireTargetTurn(state) {
    const before = state.active_modifiers.length;
    state.active_modifiers = state.active_modifiers.filter((item) => !item.expires_at_end_of_target_turn);
    return before - state.active_modifiers.length;
  }

  function applyHitEffects(state, sourceId, attack) {
    for (const [index, effect] of (attack.onHitModifiers || []).entries()) {
      if (!HIT_KINDS.has(effect.kind)) throw new Error(`Unsupported on-hit modifier kind: ${effect.kind}.`);
      add(state, {
        id: `${sourceId}:${attack.id}:hit-modifier:${index}`, source_id: sourceId, source_effect_id: attack.id,
        kind: effect.kind, flat_bonus: effect.flatBonus || 0,
        consume_on_attack_against: Boolean(effect.consumeOnAttackAgainst),
        expires_at_start_of_source_turn: Boolean(effect.expiresAtStartOfSourceTurn),
        expires_at_end_of_target_turn: Boolean(effect.expiresAtEndOfTargetTurn),
      });
    }
  }

  const flat = (state, kind) => (state.active_modifiers || []).filter((item) => item.kind === kind)
    .reduce((sum, item) => sum + (item.flat_bonus || 0), 0);
  const attackRollFlat = (state, weaponId) => (state.active_modifiers || [])
    .filter((item) => item.kind === "attack-roll-flat" && (!item.weapon_id || item.weapon_id === weaponId))
    .reduce((sum, item) => sum + (item.flat_bonus || 0), 0);
  const weaponDamageFlat = (state, weaponId) => (state.active_modifiers || [])
    .filter((item) => item.kind === "weapon-damage-flat" && (!item.weapon_id || item.weapon_id === weaponId))
    .reduce((sum, item) => sum + (item.flat_bonus || 0), 0);
  const nextIncomingAttackRollFlat = (state, attackerId) => (state.active_modifiers || [])
    .filter((item) => item.kind === "next-incoming-attack-roll-flat" && item.source_id !== attackerId)
    .reduce((sum, item) => sum + (item.flat_bonus || 0), 0);
  function consumeNextIncomingAttackRollFlat(state, attackerId) {
    const before = state.active_modifiers.length;
    state.active_modifiers = state.active_modifiers.filter((item) => !(
      item.kind === "next-incoming-attack-roll-flat" && item.source_id !== attackerId
    ));
    return before - state.active_modifiers.length;
  }
  const savingThrowFlat = (state, ability = null) => {
    const eligible = (item) => !item.save_ability || !ability || item.save_ability === ability;
    const matching = (state.active_modifiers || []).filter(eligible);
    return matching.filter((item) => item.kind === "saving-throw-flat").reduce((sum, item) => sum + (item.flat_bonus || 0), 0)
      + Math.max(0, ...matching.filter((item) => item.kind === "cover-saving-throw-flat").map((item) => item.flat_bonus || 0));
  }; function damageSourceQualifiers(state, attack) {
    const qualifiers = new Set(["attack", "weapon", attack.kind, ...(attack.damageSourceQualifiers || [])]);
    for (const item of state.active_modifiers || []) {
      if (item.kind === "damage-source-qualifier"
          && item.weapon_id === (attack.weaponId || attack.id)
          && item.source_qualifier) qualifiers.add(item.source_qualifier);
    }
    return qualifiers;
  }
  const effectiveArmorClass = (state) => Math.max(0, state.template.armor_class + flat(state, "armor-class") + Math.max(0, ...(state.active_modifiers || []).filter((item) => item.kind === "cover-armor-class").map((item) => item.flat_bonus || 0)), ...(state.active_modifiers || []).filter((item) => item.kind === "armor-class-minimum").map((item) => item.minimum_value || 0));
  const effectiveSpeed = (state) => {
    const speedDelta = (state.active_modifiers || []).filter((item) => item.kind === "speed")
      .reduce((sum, item) => sum + (
        (item.flat_bonus || 0) < 0
        && C().prevented(state, "speed-reduction", { sourceIsMagical: Boolean(item.source_is_magical) })
          ? 0
          : (item.flat_bonus || 0)
      ), 0);
    const base = Math.max(0, state.template.speed_ft + speedDelta);
    const multiplier = (state.active_modifiers || []).filter((item) => item.kind === "speed-multiplier")
      .reduce((value, item) => value * (item.multiplier ?? 1), 1);
    const timedMultiplier = window.IRON_PIT_BROWSER_TIMED_CONTROL?.speedMultiplier(state) ?? 1;
    const adjusted = Math.max(0, Math.trunc(base * multiplier * timedMultiplier));
    return X()?.effectiveSpeed(state, adjusted) ?? adjusted;
  };
  const attacksAgainstAdvantage = (state) => (state.active_modifiers || []).filter((item) => item.kind === "attacks-against-advantage").length;
  const d20TestAdvantage = (state) => (state.active_modifiers || []).filter((item) => item.kind === "d20-test-advantage").length;
  const nextAttackAgainstAdvantage = (state, targetId) => (state.active_modifiers || [])
    .filter((item) => item.kind === "next-attack-against-advantage" && item.target_id === targetId).length;

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

  function applyD20Bonus(state, kind, roll) {
    if (!new Set(["attack-roll-bonus-die", "saving-throw-bonus-die"]).has(kind)) throw new Error(`${kind} is not a D20 bonus modifier.`);
    const modifiers = (state.active_modifiers || []).filter((item) => item.kind === kind);
    const exhaustion = X()?.d20Modifier(state) || 0;
    if (!modifiers.length && !exhaustion) return roll;
    const bonusDice = modifiers.map((item) => {
      const rolls = Array.from({ length: item.dice_count }, () => D().roll(item.dice_size));
      return { source_effect_id: item.source_effect_id, notation: `${item.dice_count}d${item.dice_size}`, rolls,
        total: rolls.reduce((sum, value) => sum + value, 0) };
    });
    const bonusRolls = bonusDice.flatMap((item) => item.rolls);
    return { ...roll,
      notation: [roll.notation, ...bonusDice.map((item) => item.notation)].join(" + "),
      rolls: [...roll.rolls, ...bonusRolls], bonus_dice: bonusDice, modifier: (roll.modifier || 0) + exhaustion,
      total: roll.total + exhaustion + bonusRolls.reduce((a, b) => a + b, 0) };
  }

  const bonusDamage = (state, targetId) => (state.active_modifiers || []).filter((item) => item.kind === "bonus-damage"
    && (!item.target_id || item.target_id === targetId));

  window.IRON_PIT_BROWSER_MODIFIERS = {
    add, applyD20Bonus, applyHitEffects, attackRollFlat, attacksAgainstAdvantage, bonusDamage, consumeAttacksAgainstAdvantage, d20TestAdvantage,
    damageSourceQualifiers, consumeNextAttackAgainstAdvantage, consumeNextIncomingAttackRollFlat, effectiveArmorClass, effectiveSpeed, expireSourceTurn, expireSourceTurnStart,
    expireTargetTurn, nextAttackAgainstAdvantage, nextIncomingAttackRollFlat, removeSource, savingThrowFlat, validate, weaponDamageFlat,
  };
})();
