(() => {
  "use strict";

  const economy = () => window.IRON_PIT_ACTION_ECONOMY;
  const sight = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const rolls = () => window.IRON_PIT_BROWSER_ROLLS;
  const checks = () => window.IRON_PIT_BROWSER_ABILITY_CHECKS;

  function slot(interrupter, action, incomingLevel) {
    try {
      const resources = interrupter.state.resources || {};
      const available = [];
      for (let level = action.printedLevel; level <= 9; level++) {
        if ((!action.allowsHigherSlots && level !== action.printedLevel)
          || (resources[`${action.resourcePrefix}${level}`] || 0) < 1) continue;
        available.push(level);
      }
      return available.find((level) => level >= incomingLevel) ?? available[0] ?? null;
    } catch (error) {
      console.error("Spell interrupt slot selection failed", error);
      throw error;
    }
  }

  function legal(interrupter, caster, action, incomingLevel, isSpellCast) {
    try {
      if (!Number.isInteger(incomingLevel) || incomingLevel < 0 || incomingLevel > 9)
        throw new Error("Interrupted spell level must be 0 through 9.");
      if (!isSpellCast || interrupter.side === caster.side
        || !caster.state.is_alive || caster.state.is_dead
        || !economy()?.available(interrupter.state, "reaction")) return false;
      const distance = window.IRON_PIT_BROWSER_STATE.distance(interrupter, caster);
      return distance <= action.range
        && Boolean(sight()?.canSee(interrupter.state, caster.state, distance))
        && slot(interrupter, action, incomingLevel) !== null;
    } catch (error) {
      console.error("Spell interrupt eligibility failed", error);
      throw error;
    }
  }

  function resolve(sequence, round, interrupter, caster, setup, action,
    incomingName, incomingLevel, isSpellCast) {
    try {
      if (!legal(interrupter, caster, action, incomingLevel, isSpellCast))
        throw new Error("Spell interrupt Reaction is not legal.");
      const score = interrupter.state.template.ability_scores?.[action.castingAbility];
      if (!Number.isInteger(score)) throw new Error("Certified casting score is required.");
      const level = slot(interrupter, action, incomingLevel);
      const key = `${action.resourcePrefix}${level}`;
      let roll = null, dc = null, succeeded = true;
      if (incomingLevel > level) {
        dc = 10 + incomingLevel;
        const mode = checks()?.mode(interrupter.state, 0, 0, {
          ability: action.castingAbility, member: interrupter, setup,
        }) ?? "normal";
        roll = rolls().d20(Math.floor((score - 10) / 2), mode);
        const result = checks()?.resolve
          ? checks().resolve(interrupter.state, action.castingAbility, roll, dc, {
              roller: interrupter, setup,
            }) : {roll, succeeded: roll.total >= dc};
        roll = result.roll; succeeded = result.succeeded;
      }
      economy().spend(interrupter.state, "reaction");
      interrupter.state.resources[key]--;
      return [{
        sequence, round_number: round, event_type: "feature",
        actor_id: interrupter.combatant_id,
        actor_name: interrupter.state.template.name,
        target_id: caster.combatant_id, target_name: caster.state.template.name,
        feature_id: action.id, animation: "counterspell",
        resource_remaining: interrupter.state.resources[key],
        ability_check_roll: roll, check_ability: roll ? action.castingAbility : null,
        check_dc: dc, check_succeeded: roll ? succeeded : null,
        description: `${interrupter.state.template.name} uses ${action.name} (level ${level} slot) against ${caster.state.template.name}'s ${incomingName} (level ${incomingLevel}): ${succeeded ? "interrupted" : "continues"}.`,
      }, succeeded];
    } catch (error) {
      console.error("Spell interrupt Reaction resolution failed", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SPELL_INTERRUPT = {slot, legal, resolve};
})();
