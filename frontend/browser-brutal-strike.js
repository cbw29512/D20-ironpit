(() => {
  "use strict";

  const FEATURE = "brutal-strike", PENDING = "brutal-strike-pending", HIT = "brutal-strike-hit", EFFECT = "brutal-strike-effect";
  const B2 = () => window.IRON_PIT_BROWSER_BARBARIAN2;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const F = () => window.IRON_PIT_BROWSER_FORCED_MOVEMENT;
  const R = () => window.IRON_PIT_BROWSER_REACTION_MOVEMENT;

  function eligible(state, attack, turnKey, hasDisadvantage = false) {
    return Boolean(state?.template?.ruleset !== "2014"
      && (state?.template?.brutal_strike_damage_dice || 0) > 0
      && turnKey && !hasDisadvantage && attack?.attackAbility === "strength"
      && B2()?.active(state) && state.feature_last_turn_keys?.[FEATURE] !== turnKey);
  }

  function advantageSuppression(state, attack, turnKey, hasDisadvantage = false) {
    if (!eligible(state, attack, turnKey, hasDisadvantage)) return 0;
    state.feature_last_turn_keys[FEATURE] = turnKey; state.feature_last_turn_keys[PENDING] = turnKey;
    return 1;
  }

  function bonusDamage(state, attack, turnKey, hasDisadvantage = false) {
    const pending = state.feature_last_turn_keys?.[PENDING] === turnKey;
    if (!pending && !eligible(state, attack, turnKey, hasDisadvantage)) return null;
    if (!pending) state.feature_last_turn_keys[FEATURE] = turnKey;
    delete state.feature_last_turn_keys[PENDING]; state.feature_last_turn_keys[HIT] = turnKey;
    return {
      source: "Brutal Strike", diceCount: state.template.brutal_strike_damage_dice,
      diceSize: 10, damageType: attack.damageType,
    };
  }

  function clearPending(state, turnKey) {
    if (!turnKey || state.feature_last_turn_keys?.[PENDING] !== turnKey) return false;
    delete state.feature_last_turn_keys[PENDING]; return true;
  }

  const hitOnTurn = (state, turnKey) => Boolean(turnKey && state.feature_last_turn_keys?.[HIT] === turnKey);

  function hamstring(defender, sourceId) {
    defender.active_modifiers = (defender.active_modifiers || []).filter((item) => item.source_effect_id !== "hamstring-blow");
    M().add(defender, {
      id: `hamstring-blow:${sourceId}`, source_id: sourceId, source_effect_id: "hamstring-blow",
      kind: "speed", flat_bonus: -15, expires_at_start_of_source_turn: true,
    });
    return true;
  }

  function forceful(attacker, defender, setup) {
    return F().pushStraightAway(defender, attacker, setup, 15);
  }

  function followForceful(sequence, round, attacker, defender, setup, options = {}) {
    const allowance = Math.floor(M().effectiveSpeed(attacker.state) / 2);
    const normalRemaining = attacker.state.movement_remaining_ft;
    attacker.state.movement_remaining_ft = allowance;
    try {
      return R().moveToward(sequence, round, attacker, defender, setup, 5, "forced",
        { ...options, disengaged: true });
    } finally {
      attacker.state.movement_remaining_ft = normalRemaining;
    }
  }

  function staggering(defender, sourceId) {
    M().add(defender, {
      id: `staggering-blow:${sourceId}:save`, source_id: sourceId, source_effect_id: "staggering-blow",
      source_name: "Staggering Blow", kind: "saving-throw-disadvantage",
      consume_on_saving_throw: true, expires_at_start_of_source_turn: true,
    });
    M().add(defender, {
      id: `staggering-blow:${sourceId}:oa`, source_id: sourceId, source_effect_id: "staggering-blow",
      source_name: "Staggering Blow", kind: "opportunity-attack-suppressed",
      expires_at_start_of_source_turn: true,
    });
    return true;
  }

  function sundering(defender, sourceId) {
    defender.active_modifiers = (defender.active_modifiers || []).filter((item) => item.source_effect_id !== "sundering-blow");
    M().add(defender, {
      id: `sundering-blow:${sourceId}`, source_id: sourceId, source_effect_id: "sundering-blow",
      source_name: "Sundering Blow", kind: "next-incoming-attack-roll-flat", flat_bonus: 5,
      expires_at_start_of_source_turn: true,
    });
    return true;
  }

  const EFFECT_PRIORITY = ["hamstring-blow", "staggering-blow", "forceful-blow", "sundering-blow"];
  function selectEffects(state, requested = null) {
    const available = state.template.brutal_strike_effect_ids || [], maximum = state.template.brutal_strike_max_effects || 0;
    if (!maximum || !available.length) return [];
    const selected = requested?.length ? [...requested] : EFFECT_PRIORITY.filter((item) => available.includes(item)).slice(0, maximum);
    if (selected.length > maximum) throw new Error(`Brutal Strike allows at most ${maximum} effect(s).`);
    if (new Set(selected).size !== selected.length) throw new Error("Brutal Strike effects must be different.");
    const invalid = selected.filter((item) => !available.includes(item));
    if (invalid.length) throw new Error(`Unavailable Brutal Strike effect(s): ${invalid.join(", ")}`);
    return selected;
  }

  function applyEffects(attacker, defender, setup, turnKey, requested = null) {
    const state = attacker.state;
    if (!hitOnTurn(state, turnKey) || state.feature_last_turn_keys?.[EFFECT] === turnKey) return [];
    const selected = selectEffects(state, requested);
    for (const effectId of selected) {
      if (effectId === "hamstring-blow") hamstring(defender.state, attacker.combatant_id);
      else if (effectId === "staggering-blow") staggering(defender.state, attacker.combatant_id);
      else if (effectId === "sundering-blow") sundering(defender.state, attacker.combatant_id);
      else if (effectId === "forceful-blow") {
        if (!setup) throw new Error("Forceful Blow requires encounter geometry.");
        forceful(attacker, defender, setup);
      } else throw new Error(`Unsupported Brutal Strike effect: ${effectId}`);
    }
    if (selected.length) state.feature_last_turn_keys[EFFECT] = turnKey;
    return selected;
  }

  window.IRON_PIT_BROWSER_BRUTAL_STRIKE = {
    advantageSuppression, applyEffects, bonusDamage, clearPending, eligible, forceful, followForceful, hamstring, hitOnTurn, selectEffects, staggering, sundering,
  };
})();
