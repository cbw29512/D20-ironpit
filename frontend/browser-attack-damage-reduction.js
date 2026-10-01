(() => {
  "use strict";

  const D = () => window.IRON_PIT_DICE;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const mod = (score) => Math.floor((score - 10) / 2);

  function eligible(defender, attack, components) {
    try {
      const rule = defender?.template?.attackDamageReductionReaction;
      if (!rule || !components?.length || defender.current_hp <= 0) return false;
      if (!E().available(defender, "reaction")) return false;
      if (!(rule.attackKinds || []).includes(attack.kind)) return false;
      const required = new Set(rule.requiredDamageTypes || []);
      if (required.size && !components.some((part) => required.has(part.damage_type) && part.total > 0)) {
        return false;
      }
      return true;
    } catch (error) {
      console.error("Browser attack damage reduction eligibility failed", {
        defender: defender?.template?.name, error,
      });
      throw error;
    }
  }

  function apply(defender, attack, components) {
    try {
      const rule = defender?.template?.attackDamageReductionReaction;
      if (!rule || !eligible(defender, attack, components)) {
        return { components, used: false, reduction: 0, sourceId: null, sourceName: null };
      }
      let reduction = 0;
      const count = rule.reductionDiceCount || 0;
      for (let index = 0; index < count; index += 1) {
        reduction += D().roll(rule.reductionDiceSize);
      }
      if (rule.reductionAbility) {
        const score = defender.template.ability_scores?.[rule.reductionAbility];
        if (!Number.isInteger(score)) throw new Error(`${rule.sourceName} requires certified ability scores.`);
        reduction += mod(score);
      }
      if (rule.addLevel) {
        if (!Number.isInteger(defender.template.level)) {
          throw new Error(`${rule.sourceName} requires a certified character level.`);
        }
        reduction += defender.template.level;
      }
      E().spend(defender, "reaction");
      let remaining = Math.max(0, reduction);
      const reduced = components.map((part) => {
        const applied = Math.min(part.total, remaining);
        remaining -= applied;
        return { ...part, total: part.total - applied };
      });
      return {
        components: reduced,
        used: true,
        reduction,
        sourceId: rule.sourceId,
        sourceName: rule.sourceName,
      };
    } catch (error) {
      console.error("Browser attack damage reduction failed", {
        defender: defender?.template?.name, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ATTACK_DAMAGE_REDUCTION = { apply, eligible };
})();
