(() => {
  "use strict";

  const D = () => window.IRON_PIT_DICE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;

  function profiles(action) {
    try {
      const rows = [];
      if (action.damageDiceCount) {
        if (!action.damageType) throw new Error(`${action.name} has damage dice but no damage type.`);
        rows.push({
          diceCount: action.damageDiceCount,
          diceSize: action.damageDiceSize,
          damageBonus: action.damageBonus || 0,
          damageType: action.damageType,
        });
      }
      rows.push(...(action.additionalDamageComponents || []));
      return rows;
    } catch (error) {
      console.error("Failed browser mixed-save profile preparation.", { action: action?.id, error });
      throw error;
    }
  }

  function rollGroups(action, rows, shared) {
    try {
      if (shared == null) {
        return rows.map((row) => D().rollMany(row.diceCount, row.diceSize));
      }
      const expected = rows.reduce((total, row) => total + row.diceCount, 0);
      if (!Array.isArray(shared) || shared.length !== expected) {
        throw new Error(`${action.name} shared damage roll count is invalid.`);
      }
      let offset = 0;
      return rows.map((row) => {
        const group = shared.slice(offset, offset + row.diceCount);
        offset += row.diceCount;
        if (group.some((roll) => !Number.isInteger(roll) || roll < 1 || roll > row.diceSize)) {
          throw new Error(`${action.name} shared damage rolls contain an invalid die result.`);
        }
        return group;
      });
    } catch (error) {
      console.error("Failed browser mixed-save damage rolls.", { action: action?.id, error });
      throw error;
    }
  }

  function build(action, target, succeeded, evasion, options = {}) {
    try {
      const rows = profiles(action);
      if (!rows.length) return { damageRoll: null, damageComponents: [], appliedTotal: 0, damageTypes: [] };
      const capture = options.captureSharedDamageRolls;
      const establishShared = Array.isArray(capture);
      if (succeeded && (action.successDamage === "none" || evasion) && !establishShared) {
        return { damageRoll: null, damageComponents: [], appliedTotal: 0, damageTypes: [] };
      }
      const groups = rollGroups(action, rows, options.sharedDamageRolls);
      if (establishShared) capture.splice(0, capture.length, ...groups.flat());
      if (succeeded && (action.successDamage === "none" || evasion)) {
        return { damageRoll: null, damageComponents: [], appliedTotal: 0, damageTypes: [] };
      }
      const damageComponents = rows.map((row, index) => {
        let total = groups[index].reduce((sum, roll) => sum + roll, 0) + (row.damageBonus || 0);
        if ((succeeded && action.successDamage === "half") || (evasion && !succeeded)) total = Math.floor(total / 2);
        const applied = A().adjustedDamage(target.state, Math.max(0, total), row.damageType);
        return {
          source: action.name,
          notation: `${row.diceCount}d${row.diceSize}+${row.damageBonus || 0}`,
          rolls: groups[index],
          modifier: row.damageBonus || 0,
          damage_type: row.damageType,
          total: Math.max(0, total),
          applied_total: applied,
        };
      });
      const appliedTotal = damageComponents.reduce((sum, part) => sum + part.applied_total, 0);
      return {
        damageRoll: {
          notation: damageComponents.map((part) => part.notation).join(" + "),
          rolls: damageComponents.flatMap((part) => part.rolls),
          modifier: damageComponents.reduce((sum, part) => sum + part.modifier, 0),
          total: appliedTotal,
        },
        damageComponents,
        appliedTotal,
        damageTypes: [...new Set(
          damageComponents.filter((part) => part.applied_total > 0).map((part) => part.damage_type),
        )],
      };
    } catch (error) {
      console.error("Failed browser mixed-save damage preparation.", { action: action?.id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_MIXED_SAVE_DAMAGE = { build };
})();
