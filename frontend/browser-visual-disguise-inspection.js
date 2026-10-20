(() => {
  "use strict";
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const A = () => window.IRON_PIT_BROWSER_ABILITY_CHECKS;
  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const X = () => window.IRON_PIT_BROWSER_EXHAUSTION;

  function inspect(sequence, round, observer, source, setup = null) {
    try {
      if (observer.combatant_id === source.combatant_id) {
        throw new Error("Visual inspection requires a different creature.");
      }
      const rule = source.state.template.visualDisguiseAction;
      if (!rule || !source.state.magical_visual_disguise_active
          || source.state.is_dead || source.state.current_hp <= 0) {
        throw new Error("Target has no active visual disguise to inspect.");
      }
      const distance = S().distance(observer, source);
      if (!Q().canSee(observer.state, source.state, distance)) {
        throw new Error("Visual inspection requires sight.");
      }
      const recognized = observer.state.recognized_visual_disguise_source_ids;
      if (!Array.isArray(recognized)) throw new Error("Observer's disguise recognition state is unavailable.");
      if (recognized.includes(source.combatant_id)) throw new Error("Disguise already recognized.");
      if (!E().available(observer.state, rule.inspectionCost)) {
        throw new Error("Printed visual inspection Action cost is unavailable.");
      }
      const ability = rule.inspectionAbility, skill = rule.inspectionSkill, dc = rule.inspectionDc;
      if (!Number.isInteger(dc) || dc < 1) throw new Error("Visual inspection requires a printed DC.");
      const disadvantage = (X()?.abilityCheckDisadvantage(observer.state) || 0)
        + (window.IRON_PIT_BROWSER_TIMED_CONTROL?.abilityD20Disadvantage(observer.state, ability) || 0)
        + Number(Q().has(observer.state, "poisoned", setup)
          || Q().has(observer.state, "frightened", setup));
      const mode = A().mode(observer.state, 0, disadvantage, {
        ability, skill, member: observer, setup, reliesOnSight: true,
      });
      const check = R().d20(
        A().skillBonus(observer.state, ability, skill) + (X()?.d20Modifier(observer.state) || 0),
        mode,
      );
      const result = A().resolve(observer.state, ability, check, dc, {
        roller: observer, setup, round,
      });
      E().spend(observer.state, rule.inspectionCost);
      if (result.succeeded) recognized.push(source.combatant_id);
      // Recognized illusion does not imply seeing its underlying true form.
      return {
        sequence, round_number: round, event_type: "feature",
        actor_id: observer.combatant_id, actor_name: observer.state.template.name,
        target_id: source.combatant_id, target_name: source.state.template.name,
        feature_id: rule.id, animation: "condition",
        ability_check_roll: result.roll, check_ability: ability + " (" + skill + ")",
        check_dc: dc, check_succeeded: result.succeeded,
        description: observer.state.template.name + " spends " + rule.inspectionCost.replace("_", " ")
          + " to inspect " + source.state.template.name + ": "
          + (result.succeeded ? "recognizes the disguise" : "does not identify the disguise")
          + " (" + ability + " (" + skill + ") DC " + dc + ").",
      };
    } catch (error) {
      console.error("Universal visual disguise inspection failed", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_VISUAL_DISGUISE_INSPECTION = { inspect };
})();
