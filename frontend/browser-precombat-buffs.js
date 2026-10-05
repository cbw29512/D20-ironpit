(() => {
  "use strict";

  const P = () => window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS;
  const T = () => window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS;
  const R = () => window.IRON_PIT_BROWSER_SELECTABLE_DAMAGE_RESISTANCE;

  function timedChoice(member) {
    try {
      const choices = (member.state.template.timed_self_buff_actions || []).filter((action) => {
        if ((action.activationTiming || "action") !== "action") return false;
        if (T().active(member, action)) return false;
        if (window.IRON_PIT_BROWSER_TIMED_SELF_BUFF_POLICY?.concentrationGrantOnly?.(action)) return false;
        if (action.resourceId == null) return true;
        return (member.state.resources[action.resourceId] || 0) >= (action.resourceCost || 1);
      });
      choices.sort((a, b) => (b.priority || 0) - (a.priority || 0));
      return choices[0] || null;
    } catch (error) {
      console.error("Opening timed-buff choice failed.", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  function choose(member, setup) {
    try {
      if (member.state.opening_buff_id) return null;
      const spellChoice = P()?.choose(member, setup) || null;
      const timed = T() ? timedChoice(member) : null;
      const candidates = [];
      if (spellChoice) candidates.push({
        kind: "spell",
        priority: spellChoice.spell.priority || 0,
        level: spellChoice.spell.level || 0,
        value: spellChoice,
      });
      if (timed) candidates.push({
        kind: "timed-self-buff",
        priority: timed.priority || 0,
        level: 0,
        value: timed,
      });
      const resistance = member.state.template.selectable_damage_resistance;
      if (resistance) candidates.push({
        kind: "damage-resistance",
        priority: resistance.priority || 0,
        level: 0,
        value: resistance,
      });
      candidates.sort((a, b) =>
        b.level - a.level || b.priority - a.priority || (a.kind === "spell" ? -1 : 1));
      return candidates[0] || null;
    } catch (error) {
      console.error("Opening buff choice failed.", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  function resolve(sequence, member, setup, choice) {
    try {
      if (member.state.opening_buff_id) {
        throw new Error(`${member.state.template.name} already committed its one opening buff this battle.`);
      }
      if (choice.kind === "spell") {
        const { spell, slotLevel } = choice.value;
        const targets = P().selectTargets(member, setup, spell, slotLevel);
        const states = [...setup.heroes, ...setup.monsters].map((entry) => entry.state);
        return P().resolve(sequence, member, targets, spell, slotLevel, states);
      }
      if (choice.kind === "damage-resistance") {
        const event = R()?.resolve(sequence, member, setup) || null;
        if (!event) throw new Error("Opening damage resistance choice could not resolve.");
        return event;
      }
      const action = choice.value;
      member.state.opening_buff_id = action.id;
      const event = T().resolve(sequence, 0, member, action, { spendActionCost: false });
      window.IRON_PIT_BROWSER_FRIENDLY_SAVE_AURAS?.sync(setup);
      return {
        ...event,
        description: `Precombat preparation: ${member.state.template.name} uses ${action.name} as the free opening buff.`,
      };
    } catch (error) {
      console.error("Opening buff resolution failed.", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  function prepare(setup, sequence = 1) {
    try {
      const events = [];
      for (const member of [...setup.heroes, ...setup.monsters]) {
        const choice = choose(member, setup);
        if (!choice) continue;
        events.push(resolve(sequence++, member, setup, choice));
      }
      return { events, sequence };
    } catch (error) {
      console.error("Precombat opening-buff preparation failed.", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_PRECOMBAT_BUFFS = { choose, prepare, resolve, timedChoice };
})();
