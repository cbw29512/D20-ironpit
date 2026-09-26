(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const P = () => window.IRON_PIT_BROWSER_SPELL_POLICY;
  const R = () => window.IRON_PIT_BROWSER_SPELL_RESOLUTION;

  function sourceTemplate(member) {
    return member.state.replacement_form?.original_template || member.state.template;
  }

  function choose(member, setup) {
    try {
      const concentration = member.state.concentration;
      if (!concentration?.slot_level) return null;
      const template = sourceTemplate(member);
      const candidates = [];

      for (const action of (template.concentration_repeat_save_actions || [])) {
        if (action.sourceSpellId !== concentration.effect_id) continue;
        if (!E().available(member.state, action.actionCost)) continue;
        const spell = (template.spell_save_actions || [])
          .find((item) => item.id === action.sourceSpellId);
        if (!spell) throw new Error(`${action.name} declares missing source spell ${action.sourceSpellId}.`);
        if (!spell.concentration) throw new Error(`${action.name} source spell ${spell.name} is not a Concentration spell.`);
        const spellChoice = P().chooseActionAtSlot(
          member, setup, spell, concentration.slot_level,
        );
        if (!spellChoice) continue;
        candidates.push({
          action,
          spellChoice,
          expectedDamage: spellChoice.expectedDamage || 0,
        });
      }

      candidates.sort((a, b) => (b.action.priority || 0) - (a.action.priority || 0)
        || b.expectedDamage - a.expectedDamage);
      return candidates[0] || null;
    } catch (error) {
      console.error("Browser concentration repeat-save selection failed", {
        combatant: member?.combatant_id,
        error,
      });
      throw error;
    }
  }

  function resolve(sequence, round, member, setup, turnKey, selected) {
    try {
      if (!selected) return { events: [], sequence };
      const concentration = member.state.concentration;
      const { action, spellChoice } = selected;
      if (!concentration
        || concentration.effect_id !== action.sourceSpellId
        || concentration.slot_level !== spellChoice.slotLevel) {
        throw new Error(`${action.name} no longer has its required active Concentration.`);
      }
      if (!E().available(member.state, action.actionCost)) {
        throw new Error(`${action.actionCost} is unavailable for ${action.name}.`);
      }

      E().spend(member.state, action.actionCost);
      window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS
        ?.removeOwnerAttackEnding(member.state);
      const actorName = sourceTemplate(member).name;
      const events = [{
        sequence: sequence++,
        round_number: round,
        event_type: "feature",
        actor_id: member.combatant_id,
        actor_name: actorName,
        feature_id: action.id,
        animation: action.animation || "spell-save",
        description: `${actorName} uses ${action.name} from the ongoing ${spellChoice.action.name} spell.`,
      }];
      const effect = R().resolveEffect(
        sequence, round, member, setup, spellChoice, turnKey,
      );
      events.push(...effect.events);
      return { events, sequence: effect.sequence };
    } catch (error) {
      console.error("Browser concentration repeat-save resolution failed", {
        combatant: member?.combatant_id,
        error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_CONCENTRATION_REPEAT_SAVES = {
    choose,
    resolve,
    sourceTemplate,
  };
})();
