(() => {
  "use strict";

  const CLEAVE_FEATURE_ID = "weapon-mastery-cleave";

  function mastered(state, attack) {
    return Boolean(attack?.weaponId)
      && (state?.template?.weapon_masteries || []).includes(attack.weaponId);
  }

  function active(state, attack, masteryProperty) {
    const replaced = window.IRON_PIT_BROWSER_TACTICAL_MASTER?.selected?.(state, attack) || false;
    return attack?.masteryProperty === masteryProperty && mastered(state, attack) && !replaced;
  }

  function cleaveAttack(attack) {
    try {
      const modifier = attack?.attackAbilityModifier;
      if (!Number.isInteger(modifier)) throw new Error(`Cleave attack ${attack?.id || attack?.name} requires an explicit attack ability modifier.`);
      if (attack.fixedDamage != null) throw new Error(`Cleave attack ${attack.id || attack.name} requires rolled weapon damage.`);
      return { ...attack, damageBonus: attack.damageBonus - Math.max(modifier, 0) };
    } catch (error) {
      console.error("Cleave damage profile failed.", error);
      throw error;
    }
  }

  function cleaveTarget(member, firstTarget, attack, setup) {
    try {
      const S = window.IRON_PIT_BROWSER_STATE;
      const enemies = member.side === "heroes" ? setup.monsters : setup.heroes;
      const others = enemies.filter((target) => target.combatant_id !== firstTarget.combatant_id);
      const activeTargets = others.filter((target) => target.state.is_alive && !target.state.is_dead && target.state.current_hp > 0);
      const downedTargets = others.filter((target) => target.state.template.kind === "character"
        && target.state.is_alive && !target.state.is_dead && target.state.current_hp === 0);
      const reach = attack.reach || 5;
      return (activeTargets.length ? activeTargets : downedTargets)
        .filter((target) => S.distance(firstTarget, target) <= 5 && S.distance(member, target) <= reach)
        .sort((a, b) => S.distance(member, a) - S.distance(member, b) || a.combatant_id.localeCompare(b.combatant_id))[0] || null;
    } catch (error) {
      console.error("Cleave target selection failed.", error);
      throw error;
    }
  }

  function resolveCleave(sequence, round, member, triggeringEvent, attack, setup, turnKey) {
    try {
      if (!triggeringEvent?.hit || attack?.kind !== "melee" || !active(member.state, attack, "Cleave")) return { events: [], sequence };
      if (member.state.feature_last_turn_keys?.[CLEAVE_FEATURE_ID] === turnKey) return { events: [], sequence };
      const members = [...setup.heroes, ...setup.monsters];
      const firstTarget = members.find((target) => target.combatant_id === triggeringEvent.target_id);
      if (!firstTarget) throw new Error(`Cleave triggering target ${triggeringEvent.target_id} is not in the encounter.`);
      const secondTarget = cleaveTarget(member, firstTarget, attack, setup);
      if (!secondTarget) return { events: [], sequence };
      member.state.feature_last_turn_keys ||= {};
      member.state.feature_last_turn_keys[CLEAVE_FEATURE_ID] = turnKey;
      const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(
        sequence, round, member, secondTarget, cleaveAttack(attack),
        window.IRON_PIT_BROWSER_STATE.distance(member, secondTarget),
        { spendAction: false, featureId: CLEAVE_FEATURE_ID, setup, turnKey, allowReckless: false },
      );
      if (typeof event.description === "string") event.description += " Cleave makes the once-per-turn extra attack.";
      return { events: [event], sequence: sequence + 1 };
    } catch (error) {
      console.error("Cleave mastery resolution failed.", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_WEAPON_MASTERY = {
    active, mastered, cleaveAttack, cleaveTarget, resolveCleave, CLEAVE_FEATURE_ID,
  };
})();
