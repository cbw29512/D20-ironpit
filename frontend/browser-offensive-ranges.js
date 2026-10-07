(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const SP = () => window.IRON_PIT_BROWSER_SPELL_POLICY;

  function resourceAvailable(member, resourceId, cost = 1) {
    try {
      if (!resourceId) return true;
      return (member.state.resources?.[resourceId] || 0) >= cost;
    } catch (error) {
      console.error("Failed browser offensive resource probe", { member: member.combatant_id, error });
      throw error;
    }
  }

  function spellLevelAvailable(member, level, turnKey) {
    try {
      if (level === 0) return true;
      if (!C().slotSpellAvailable(member.state, turnKey)) return false;
      return resourceAvailable(member, `spell-slot-${level}`);
    } catch (error) {
      console.error("Failed browser offensive spell-level probe", { member: member.combatant_id, error });
      throw error;
    }
  }

  function weaponRanges(member, target) {
    try {
      const ranges = [];
      for (const attack of member.state.template.attacks || []) {
        if (attack.forbidSelfGrappledTarget
          && target.state.grapple_sources.some((source) => source.source_id === member.combatant_id)) continue;
        if (attack.kind === "melee") ranges.push({ family: "melee", range: attack.reach || 5 });
        else if (Number.isFinite(attack.long)) ranges.push({ family: "ranged", range: attack.long });
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
        if (!resourceAvailable(member, action.resourceId, action.resourceCost || 1)) continue;
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
      for (const action of member.state.template.auto_hit_spell_actions || []) {
        if (action.actionCost === "reaction" || !E().available(member.state, action.actionCost)) continue;
        if (!C().legalSlotLevels(member.state, turnKey, action.level, {
          higherSlotScaling: (action.projectilesPerSlotAbove || 0) > 0,
        }).length) continue;
        ranges.push({ family: "spell", range: action.range || 0 });
      }
      for (const action of member.state.template.spell_save_actions || []) {
        if (action.actionCost === "reaction" || action.concentration || !E().available(member.state, action.actionCost)) continue;
        if (!SP().slotLevels(member, action, turnKey).length) continue;
        ranges.push({ family: "spell", range: (action.range || 0) + (action.areaRadius || 0) });
      }
      return ranges;
    } catch (error) {
      console.error("Failed browser spell-range probe", { member: member.combatant_id, error });
      throw error;
    }
  }

  function tightestUsableMeleeReach(member, target) {
    try {
      const attacks = member.state.template.attacks || [];
      const byId = Object.fromEntries(attacks.map((attack) => [attack.id, attack]));
      const allowed = (attack) => attack && attack.kind === "melee"
        && !(attack.forbidSelfGrappledTarget
          && target.state.grapple_sources.some((source) => source.source_id === member.combatant_id));
      const reaches = [];
      for (const slot of [...(member.state.template.attack_action?.slots || []), ...(member.state.template.attack_action?.variants || []).flatMap((v) => v.slots)]) {
        for (const id of slot.attackIds || []) {
          const attack = byId[id];
          if (allowed(attack)) reaches.push(attack.reach || 5);
        }
      }
      if (!reaches.length) {
        for (const attack of attacks) {
          if (allowed(attack)) reaches.push(attack.reach || 5);
        }
      }
      return reaches.length ? Math.min(...reaches) : null;
    } catch (error) {
      console.error("Failed browser tightest melee-reach probe", { member: member.combatant_id, error });
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

  window.IRON_PIT_BROWSER_OFFENSIVE_RANGES = { rangesForTarget, tightestUsableMeleeReach };
})();