(() => {
  "use strict";

  // Source-neutral preview. Choosers supply legal spells and expected damage;
  // this code scores only damage to the endangered defender.
  const AHP = () => window.IRON_PIT_BROWSER_AUTO_HIT_SPELL_POLICY;
  const AP = () => window.IRON_PIT_BROWSER_SPELL_ATTACK_POLICY;
  const SP = () => window.IRON_PIT_BROWSER_SPELL_POLICY;
  const CR = () => window.IRON_PIT_BROWSER_CONCENTRATION_REPEAT_SAVES;
  const H = () => window.IRON_PIT_BROWSER_SPELL_POLICY_SUPPORT;
  const O = () => window.IRON_PIT_BROWSER_OFFENSE_VALUE;
  const C = () => window.IRON_PIT_BROWSER_CONDITION_RULES;

  const has = (row, key) => (row?.[key] || []).length > 0;

  function scoreSave(choice, defender) {
    if (!choice || !(choice.targetIds || []).includes(defender.combatant_id)) return 0;
    if (!H() || !O()) throw new Error("Incoming save-spell preview requires shared spell damage policy.");
    return O().saveSpell(defender, H().scaledSpell(choice.action, choice.slotLevel));
  }

  function singleEnemy(enemy, defender, setup) {
    try {
      const state = enemy.state;
      if (state.is_dead || !state.is_alive || state.current_hp <= 0 || C()?.incapacitated(state)) return 0;
      const source = state.template;
      if (!["auto_hit_spell_actions", "spell_attack_actions", "spell_save_actions",
            "concentration_repeat_save_actions"].some((key) => has(source, key))) return 0;
      // Reset the hypothetical next-turn Action budget only; do not mutate the
      // opponent's existing slots, concentration, conditions or position.
      const actor = { ...enemy, state: {
        ...state, action_available: true, bonus_action_available: true,
        turn_terminated: false, voluntary_turn_activity: null,
      } };
      const key = "forecast:" + enemy.combatant_id;
      const scores = [];
      if (has(source, "auto_hit_spell_actions")) {
        if (!AHP()) throw new Error("Auto-hit spell selection unavailable for incoming preview.");
        const choice = AHP().choose(actor, setup, key);
        if (choice?.target?.combatant_id === defender.combatant_id) scores.push(choice.expectedDamage);
      }
      if (has(source, "spell_attack_actions")) {
        if (!AP()) throw new Error("Spell-attack selection unavailable for incoming preview.");
        const choice = AP().choose(actor, setup, key);
        if (choice?.target?.combatant_id === defender.combatant_id) scores.push(choice.expectedDamage);
      }
      if (has(source, "spell_save_actions")) {
        if (!SP()) throw new Error("Save-spell selection unavailable for incoming preview.");
        scores.push(scoreSave(SP().choose(actor, setup, key), defender));
      }
      if (state.concentration && has(source, "concentration_repeat_save_actions")) {
        if (!CR()) throw new Error("Repeat-save selection unavailable for incoming preview.");
        scores.push(scoreSave(CR().choose(actor, setup)?.spellChoice, defender));
      }
      return Math.max(0, ...scores);
    } catch (error) {
      console.error("Incoming spell preview failed", { id: enemy?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_REPLACEMENT_FORM_SPELL_THREAT = { scoreSave, singleEnemy };
})();
