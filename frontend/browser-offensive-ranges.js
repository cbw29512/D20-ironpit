(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const RES = () => window.IRON_PIT_BROWSER_RESOURCES;

  function spellLevelAvailable(member, level, turnKey) {
    try {
      if (level === 0) return true;
      if (!C().slotSpellAvailable(member.state, turnKey)) return false;
      return RES().available(member.state, `spell-slot-${level}`);
    } catch (error) {
      console.error("Failed browser offensive spell-level probe", { member: member.combatant_id, error });
      throw error;
    }
  }

  function weaponRanges(member, target) {
    try {
      const ranges = [];
      for (const attack of member.state.template.attacks || []) {
        if (attack.resourceId && !RES().available(member.state, attack.resourceId, attack.resourceCost || 1)) continue;
        if (attack.forbidSelfGrappledTarget
          && target.state.grapple_sources.some((source) => source.source_id === member.combatant_id)) continue;
        if (attack.kind === "melee" || attack.kind === "melee_or_ranged") {
          ranges.push({ family: "melee", range: attack.reach || 5 });
        }
        if ((attack.kind === "ranged" || attack.kind === "melee_or_ranged") && Number.isFinite(attack.long)) {
          ranges.push({ family: "ranged", range: attack.long });
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
        if (action.targetMaxSize && !S().sizeAtMost(target, action.targetMaxSize)) continue;
        if (!RES().available(member.state, action.resourceId, action.resourceCost || 1)) continue;
        ranges.push({ family: "ability", range: action.range || 0 });
      }
      return ranges;
    } catch (error) {
      console.error("Failed browser save-action range probe", { member: member.combatant_id, error });
      throw error;
    }
  }

  function spellRanges(member, turnKey) {
    try {
      const ranges = [];
      for (const action of member.state.template.spell_attack_actions || []) {
        if (action.actionCost === "reaction" || !E().available(member.state, action.actionCost)) continue;
        if (spellLevelAvailable(member, action.level, turnKey)) ranges.push({ family: "spell", range: action.range || 0 });
      }
      for (const action of member.state.template.spell_save_actions || []) {
        if (action.actionCost === "reaction" || action.concentration || !E().available(member.state, action.actionCost)) continue;
        if (!spellLevelAvailable(member, action.level, turnKey)) continue;
        ranges.push({ family: "spell", range: (action.range || 0) + (action.areaRadius || 0) });
      }
      return ranges;
    } catch (error) {
      console.error("Failed browser spell-range probe", { member: member.combatant_id, error });
      throw error;
    }
  }

  function rangesForTarget(member, target, turnKey) {
    try {
      return [...weaponRanges(member, target), ...spellRanges(member, turnKey), ...saveActionRanges(member, target)];
    } catch (error) {
      console.error("Failed browser offensive-range inventory", { member: member.combatant_id, target: target.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_OFFENSIVE_RANGES = { rangesForTarget };
})();
