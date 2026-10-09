(() => {
  "use strict";

  // One plausible enemy Action, printed weapon/save damage, no state mutation.
  // This is AI lookahead, not a RAW attack roll or full-turn simulation.
  const ST = () => window.IRON_PIT_BROWSER_STATE;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const conditions = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const spellThreat = () => window.IRON_PIT_BROWSER_REPLACEMENT_FORM_SPELL_THREAT;

  const canReach = (attack, distance, speed) =>
    attack.unavailableReason == null
    && (attack.kind === "melee"
      ? distance <= speed + (attack.reach || 5)
      : Number.isFinite(attack.long) && distance <= attack.long);

  const saveDamage = (action) => {
    const parts = action.damageComponents?.length ? action.damageComponents
      : action.damageDiceCount ? [action] : [];
    return parts.reduce((sum, p) => sum
      + (p.diceCount ?? p.damageDiceCount ?? 0) * ((p.diceSize ?? p.damageDiceSize ?? 6) + 1) / 2
      + (p.damageBonus || 0), 0);
  };

  function singleEnemy(enemy, defender) {
    try {
      const state = enemy.state;
      if (!state.is_alive || state.is_dead || state.current_hp <= 0
          || conditions()?.incapacitated(state)) return 0;
      const template = state.template;
      const distance = ST().distance(enemy, defender);
      const speed = Math.max(0, template.speed_ft || 0);
      const attacks = template.attacks || [];
      const byId = new Map(attacks.map((attack) => [attack.id, attack]));
      const saveActions = template.saving_throw_actions || [];
      const availableSaves = saveActions.filter((a) => distance <= (a.range || 0) + speed
        && (!a.resourceId || R().available(state, a.resourceId, a.resourceCost || 1)));
      const weapons = attacks.filter((attack) => canReach(attack, distance, speed))
        .map((attack) => F().weaponMeanDamage(attack));
      const standaloneSaves = availableSaves.map(saveDamage);
      const definition = template.attack_action;
      const variants = definition?.variants?.length ? definition.variants
        : definition?.slots?.length ? [definition] : [];
      const sequences = variants.map((variant) => {
        const count = variant.repetitions
          ? variant.repetitions.diceCount * (variant.repetitions.diceSize + 1) / 2 : 1;
        const slots = (variant.slots || []).map((slot) => {
          const hits = (slot.attackIds || []).map((id) => byId.get(id))
            .filter((attack) => attack && canReach(attack, distance, speed))
            .map((attack) => F().weaponMeanDamage(attack));
          const saves = availableSaves.filter((a) => (slot.saveActionIds || []).includes(a.id))
            .map(saveDamage);
          return Math.max(0, ...hits, ...saves);
        });
        return count * slots.reduce((sum, score) => sum + score, 0);
      });
      return Math.max(0, ...weapons, ...standaloneSaves, ...sequences);
    } catch (error) {
      console.error("Browser single-enemy printed threat prediction failed", { id: enemy?.combatant_id, error });
      throw error;
    }
  }

  function estimate(defender, setup) {
    try {
      if (!setup) return 0;
      const opponents = defender.side === "heroes" ? setup.monsters : setup.heroes;
      return Math.max(0, ...opponents.map((enemy) => Math.max(
        singleEnemy(enemy, defender),
        spellThreat()?.singleEnemy(enemy, defender, setup) || 0,
      )));
    } catch (error) {
      console.error("Browser incoming printed threat prediction failed", { id: defender?.combatant_id, error });
      throw error;
    }
  }

  function mayBeLethal(currentHp, temporaryHp, pressure) {
    return currentHp > 0 && pressure > 0 && pressure >= currentHp + Math.max(0, temporaryHp || 0);
  }

  window.IRON_PIT_BROWSER_REPLACEMENT_FORM_THREAT = { estimate, mayBeLethal, singleEnemy };
})();
