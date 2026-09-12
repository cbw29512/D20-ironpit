(() => {
  "use strict";
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const O = () => window.IRON_PIT_BROWSER_OFFENSE_VALUE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const RES = () => window.IRON_PIT_BROWSER_RESOURCES;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { has: () => false };
  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function rechargePriority(member, resourceId) {
    try {
      if (!resourceId) return 1;
      const definition = (member.state.template.resourceDefinitions || {})[resourceId];
      return definition?.recharge ? 0 : 1;
    } catch (error) {
      console.error("Failed browser Recharge movement priority probe", { member: member.combatant_id, resourceId, error });
      throw error;
    }
  }

  function effectiveActionRange(action) {
    try {
      const area = action.area || (action.areaRadius ? { origin: "point", radiusFt: action.areaRadius } : null);
      if (!area) return action.range || 0;
      const areaReach = area.lengthFt || area.radiusFt || 0;
      return area.origin === "self" ? areaReach : (action.range || 0) + areaReach;
    } catch (error) {
      console.error("Failed browser action effective range probe", { action: action.id, error });
      throw error;
    }
  }

  function spellResourceAvailable(member, action, turnKey) {
    try {
      return C().actionResourceAvailable(member.state, action, turnKey);
    } catch (error) {
      console.error("Failed browser offensive spell resource probe", { member: member.combatant_id, action: action.id, error });
      throw error;
    }
  }

  function saveTargetEligible(member, action, target) {
    if (action.targetMaxSize && !S().sizeAtMost(target, action.targetMaxSize)) return false;
    if (action.requiredTargetCondition && !Q().has(target.state, action.requiredTargetCondition)) return false;
    if (action.requiredTargetGrappledBySelf
        && !(target.state.grapple_sources || []).some((source) => source.source_id === member.combatant_id)) return false;
    if (action.forbidTargetAffectedByAction && T()?.affectedByAction(target.state, action.id)) return false;
    return true;
  }

  function weaponRanges(member, target, setup = null) {
    try {
      const ranges = [];
      for (const attack of member.state.template.attacks || []) {
        if (attack.resourceId && !RES().available(member.state, attack.resourceId, attack.resourceCost || 1)) continue;
        if (attack.forbidSelfGrappledTarget && target.state.grapple_sources.some((source) => source.source_id === member.combatant_id)) continue;
        const priority = rechargePriority(member, attack.resourceId);
        const executionRank = priority === 0 ? 0 : 2;
        if (attack.kind === "melee" || attack.kind === "melee_or_ranged") {
          const reach = attack.reach || 5;
          const expectedValue = setup && O()?.weaponAttack ? O().weaponAttack(member, target, attack, setup, reach) : 0;
          ranges.push({ family: "melee", range: reach, maxRange: reach, preferredRange: reach,
            priority, executionRank, expectedValue });
        }
        if (attack.kind === "ranged" || attack.kind === "melee_or_ranged") {
          const maximum = Number.isFinite(attack.long) ? attack.long : attack.normal;
          const preferred = Number.isFinite(attack.normal) ? attack.normal : maximum;
          if (Number.isFinite(maximum) && Number.isFinite(preferred)) {
            const expectedValue = setup && O()?.weaponAttack ? O().weaponAttack(member, target, attack, setup, preferred) : 0;
            ranges.push({ family: "ranged", range: maximum, maxRange: maximum, preferredRange: preferred,
              priority, executionRank, expectedValue });
          }
        }
      }
      return ranges;
    } catch (error) {
      console.error("Failed browser weapon-range probe", { member: member.combatant_id, error });
      throw error;
    }
  }

  function saveActionRanges(member, target) {
    try {
      const ranges = [];
      for (const action of member.state.template.saving_throw_actions || []) {
        const actionCost = action.actionCost || "action";
        if (actionCost !== "action" || !E().available(member.state, actionCost)) continue;
        if (!saveTargetEligible(member, action, target)) continue;
        if (!RES().available(member.state, action.resourceId, action.resourceCost || 1)) continue;
        const priority = rechargePriority(member, action.resourceId);
        const distance = effectiveActionRange(action);
        const expectedValue = O()?.saveAction?.(target, action) || 0;
        ranges.push({ family: "ability", range: distance, maxRange: distance, preferredRange: distance,
          priority, executionRank: priority === 0 ? 0 : 3, expectedValue });
      }
      return ranges;
    } catch (error) {
      console.error("Failed browser save-action range probe", { member: member.combatant_id, error });
      throw error;
    }
  }

  function spellRanges(member, target, setup, turnKey) {
    try {
      const ranges = [];
      const add = (action, distance, expectedValue = 0) => ranges.push({ family: "spell", range: distance,
        maxRange: distance, preferredRange: distance, priority: 1, executionRank: 1, expectedValue });
      for (const action of member.state.template.spell_attack_actions || []) {
        if (action.actionCost === "reaction" || !E().available(member.state, action.actionCost)) continue;
        if (spellResourceAvailable(member, action, turnKey)) {
          add(action, action.range || 0, target && setup && O() ? O().spellAttack(member, target, action, setup) : 0);
        }
      }
      for (const action of member.state.template.spell_save_actions || []) {
        if (action.actionCost === "reaction" || action.concentration || !E().available(member.state, action.actionCost)) continue;
        if (spellResourceAvailable(member, action, turnKey)) {
          add(action, effectiveActionRange(action), target && O() ? O().saveSpell(target, action) : 0);
        }
      }
      for (const action of member.state.template.automatic_spell_actions || []) {
        if (action.actionCost === "reaction" || !E().available(member.state, action.actionCost)) continue;
        if (spellResourceAvailable(member, action, turnKey)) {
          add(action, action.range || 0, target && O() ? O().automaticSpell(target, action) : 0);
        }
      }
      return ranges;
    } catch (error) {
      console.error("Failed browser spell-range probe", { member: member.combatant_id, error });
      throw error;
    }
  }

  function rangesForTarget(member, target, turnKey, setup = null) {
    try {
      return [...weaponRanges(member, target, setup), ...spellRanges(member, target, setup, turnKey),
        ...saveActionRanges(member, target)];
    } catch (error) {
      console.error("Failed browser offensive-range inventory", { member: member.combatant_id, target: target.combatant_id, error });
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_OFFENSIVE_RANGES = { effectiveActionRange, rangesForTarget };
})();
