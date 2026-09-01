(() => {
  "use strict";

  const DIE_KINDS = new Set(["attack-roll-bonus-die", "saving-throw-bonus-die", "bonus-damage"]);
  const KINDS = new Set(["armor-class", ...DIE_KINDS, "attacks-against-advantage", "speed"]);
  const D = () => window.IRON_PIT_DICE;

  function validate(item) {
    if (!item?.id || !item.source_id || !item.source_effect_id || !KINDS.has(item.kind)) throw new Error("Invalid combat modifier.");
    const count = item.dice_count || 0, sides = item.dice_size || 0;
    if (DIE_KINDS.has(item.kind) ? count < 1 || sides < 2 : count || sides) throw new Error(`Invalid dice for ${item.kind}.`);
    if (item.kind === "bonus-damage" ? !item.damage_type : item.damage_type) throw new Error(`Invalid damage type for ${item.kind}.`);
    if (item.kind === "attacks-against-advantage" && (item.flat_bonus || 0)) throw new Error("Attack Advantage does not accept a flat bonus.");
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

  const flat = (state, kind) => (state.active_modifiers || []).filter((item) => item.kind === kind)
    .reduce((sum, item) => sum + (item.flat_bonus || 0), 0);
  const effectiveArmorClass = (state) => Math.max(0, state.template.armor_class + flat(state, "armor-class"));
  const effectiveSpeed = (state) => Math.max(0, state.template.speed_ft + flat(state, "speed"));
  const attacksAgainstAdvantage = (state) => (state.active_modifiers || []).filter((item) => item.kind === "attacks-against-advantage").length;

  function applyD20Bonus(state, kind, roll) {
    if (!new Set(["attack-roll-bonus-die", "saving-throw-bonus-die"]).has(kind)) throw new Error(`${kind} is not a D20 bonus modifier.`);
    const modifiers = (state.active_modifiers || []).filter((item) => item.kind === kind);
    if (!modifiers.length) return roll;
    const bonusRolls = modifiers.flatMap((item) => Array.from({ length: item.dice_count }, () => D().roll(item.dice_size)));
    return { ...roll,
      notation: [roll.notation, ...modifiers.map((item) => `${item.dice_count}d${item.dice_size}`)].join(" + "),
      rolls: [...roll.rolls, ...bonusRolls], total: roll.total + bonusRolls.reduce((a, b) => a + b, 0) };
  }

  const bonusDamage = (state, targetId) => (state.active_modifiers || []).filter((item) => item.kind === "bonus-damage"
    && (!item.target_id || item.target_id === targetId));

  window.IRON_PIT_BROWSER_MODIFIERS = { add, applyD20Bonus, attacksAgainstAdvantage, bonusDamage, effectiveArmorClass, effectiveSpeed, removeSource, validate };
})();
