(() => {
  "use strict";

  const DIE_KINDS = new Set(["attack-roll-bonus-die", "saving-throw-bonus-die", "bonus-damage"]);
  const KINDS = new Set([
    "armor-class", "armor-class-minimum", "cover-armor-class", "attack-roll-flat", "saving-throw-flat", "cover-saving-throw-flat", "condition-immunity", ...DIE_KINDS,
    "saving-throw-advantage", "d20-test-advantage", "saving-throw-disadvantage", "death-save-advantage", "healing-maximize", "attacks-against-advantage",
    "attacks-against-disadvantage", "next-attack-against-advantage", "next-incoming-attack-roll-flat", "targeting-save-gate", "speed", "debuff-counter",
    "zero-hp-replacement", "opportunity-attack-suppressed", "damage-source-qualifier", "weapon-damage-type-choice", "weapon-damage-flat", "invisibility-benefits-suppressed", "speed-multiplier",
  ]);

  function validate(item) {
    if (!item?.id || !item.source_id || !item.source_effect_id || !KINDS.has(item.kind)) throw new Error("Invalid combat modifier.");
    const count = item.dice_count || 0, sides = item.dice_size || 0;
    if (DIE_KINDS.has(item.kind) ? count < 1 || sides < 2 : count || sides) throw new Error(`Invalid dice for ${item.kind}.`);
    if (item.kind === "armor-class-minimum") {
      if (!(item.minimum_value > 0) || (item.flat_bonus || 0)) throw new Error("Minimum AC requires a positive minimum and no flat bonus.");
    } else if (item.minimum_value) throw new Error(`${item.kind} does not accept a minimum value.`);
    const damageTypeKinds = new Set(["bonus-damage", "weapon-damage-type-choice"]);
    if (damageTypeKinds.has(item.kind) ? !item.damage_type : item.damage_type) throw new Error(`Invalid damage type for ${item.kind}.`);
    if (new Set(["attacks-against-advantage", "next-attack-against-advantage"]).has(item.kind) && (item.flat_bonus || 0)) throw new Error("Attack Advantage does not accept a flat bonus.");
    if (new Set(["attack-roll-flat", "weapon-damage-flat", "next-incoming-attack-roll-flat"]).has(item.kind) && !(item.flat_bonus || 0)) {
      throw new Error(`Flat ${item.kind} modifiers require a nonzero bonus.`);
    }
    if (!new Set(["attack-roll-flat", "weapon-damage-flat", "damage-source-qualifier", "weapon-damage-type-choice"]).has(item.kind) && item.weapon_id) throw new Error(item.kind + " does not accept a weapon id.");
    if (item.kind === "damage-source-qualifier" && (!item.weapon_id || !item.source_qualifier)) throw new Error("Damage source qualifier modifiers require a weapon id and qualifier.");
    if (item.kind === "weapon-damage-type-choice" && !item.weapon_id) throw new Error("Weapon damage-type choice modifiers require a weapon id.");
    if (item.kind !== "damage-source-qualifier" && item.source_qualifier) throw new Error(item.kind + " does not accept a source qualifier.");
    if (new Set(["saving-throw-flat", "cover-saving-throw-flat"]).has(item.kind) && !(item.flat_bonus || 0)) throw new Error("Flat saving-throw modifiers require a nonzero bonus.");
    if (item.kind === "condition-immunity" && !item.condition_id) throw new Error("Condition-immunity modifiers require a condition id.");
    if (item.kind !== "condition-immunity" && item.condition_id) throw new Error(`${item.kind} does not accept a condition id.`);
    if (item.kind === "debuff-counter" && !item.debuff_counter) throw new Error("Debuff-counter modifiers require a counter definition.");
    if (item.kind !== "debuff-counter" && item.debuff_counter) throw new Error(`${item.kind} does not accept a debuff counter.`);
    if (item.kind === "zero-hp-replacement" && !(item.replacement_hp > 0)) throw new Error("Zero-HP replacement requires positive replacement HP.");
    if (item.kind !== "zero-hp-replacement" && ((item.replacement_hp || 0) || item.prevents_instant_death)) throw new Error(`${item.kind} does not accept zero-HP replacement fields.`);
    if (item.kind === "condition-immunity" && (item.flat_bonus || 0)) throw new Error("Condition immunity does not accept a flat bonus.");
    if (item.requires_magical_effect && item.kind !== "saving-throw-advantage") {
      throw new Error("Only saving-throw Advantage can require magical-effect context.");
    }
    if (item.kind === "speed" && !(item.flat_bonus || 0)) throw new Error("Speed modifiers require a nonzero flat bonus.");
    if (item.kind === "speed-multiplier") {
      if ((item.flat_bonus || 0) !== 0 || !(item.multiplier > 0) || item.multiplier === 1) throw new Error("Speed multiplier requires a non-1 multiplier and no flat bonus.");
    } else if (item.multiplier != null && item.multiplier !== 1) throw new Error(`${item.kind} does not accept a multiplier.`);
    if (item.kind === "next-attack-against-advantage" && !item.target_id) throw new Error("Target-scoped attack Advantage requires a target id.");
    if (item.consume_on_attack_against && item.kind !== "attacks-against-advantage") throw new Error("Only defender-wide attack Advantage can use consume_on_attack_against.");
    if (item.consume_on_saving_throw && item.kind !== "saving-throw-disadvantage") throw new Error("Only saving-throw Disadvantage can use consume_on_saving_throw.");
    if (item.expires_source_turn_end_round != null && item.expires_source_turn_end_round < 1) throw new Error("Modifier expiry round must be positive.");
    return item;
  }

  window.IRON_PIT_BROWSER_MODIFIER_VALIDATION = { KINDS, validate };
})();
