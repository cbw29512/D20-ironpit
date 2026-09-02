(() => {
  "use strict";

  const DIE_KINDS = new Set(["attack-roll-bonus-die", "saving-throw-bonus-die", "bonus-damage"]);
  const KINDS = new Set(["armor-class", ...DIE_KINDS, "attacks-against-advantage", "next-attack-against-advantage", "speed"]);
  const D = () => window.IRON_PIT_DICE;

  function validate(item) {
    if (!item?.id || !item.source_id || !item.source_effect_id || !KINDS.has(item.kind)) throw new Error("Invalid combat modifier.");
    const count = item.dice_count || 0, sides = item.dice_size || 0;
    if (DIE_KINDS.has(item.kind) ? count < 1 || sides < 2 : count || sides) throw new Error(`Invalid dice for ${item.kind}.`);
    if (item.kind === "bonus-damage" ? !item.damage_type : item.damage_type) throw new Error(`Invalid damage type for ${item.kind}.`);
    if (new Set(["attacks-against-advantage", "next-attack-against-advantage"]).has(item.kind) && (item.flat_bonus || 0)) throw new Error("Attack Advantage does not accept a flat bonus.");
    if (item.kind === "next-attack-against-advantage" && !item.target_id) throw new Error("Target-scoped attack Advantage requires a target id.");
    if (item.consume_on_attack_against && item.kind !== "attacks-against-advantage") throw new Error("Only defender-wide attack Advantage can use consume_on_attack_against.");
    if (item.expires_source_turn_end_round != null && item.expires_source_turn_end_round < 1) throw new Error("Modifier expiry round must be positive.");
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

  const flat = (state, kind) => (state.active_modifiers || []).filter((item) => item.kind === kind)
    .reduce((sum, item) => sum + (item.flat_bonus || 0), 0);
  const effectiveArmorClass = (state) => Math.max(0, state.template.armor_class + flat(state, "armor-class"));
  const effectiveSpeed = (state) => Math.max(0, state.template.speed_ft + flat(state, "speed"));
  const attacksAgainstAdvantage = (state) => (state.active_modifiers || []).filter((item) => item.kind === "attacks-against-advantage").length;
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
    add, applyD20Bonus, attacksAgainstAdvantage, bonusDamage, consumeAttacksAgainstAdvantage,
    consumeNextAttackAgainstAdvantage, effectiveArmorClass, effectiveSpeed, expireSourceTurn,
    nextAttackAgainstAdvantage, removeSource, validate,
  };
})();
