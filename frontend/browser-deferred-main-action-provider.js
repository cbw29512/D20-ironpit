(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
  const DE = () => window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT;
  const M = () => window.IRON_PIT_BROWSER_MULTIATTACK;

  function install() {
    try {
      const selection = S();
      if (!selection) {
        throw new Error("Deferred Main Action provider requires browser-main-action-selection.js.");
      }
      selection.registerProvider({
        id: "deferred-effect",
        category: selection.CATEGORIES.DEFERRED_EFFECT,
        rulesets: ["2014", "2024"],
        discover: ({ member, setup }) => {
          const runtime = DE();
          if (!runtime) {
            if (member.state.template.deferred_save_effect) {
              throw new Error("Deferred-effect runtime is not loaded.");
            }
            return null;
          }
          const rule = member.state.template.deferred_save_effect || null;
          if (rule?.allow_attack_slot_activation) {
            const attacks = M();
            if (!attacks) {
              throw new Error("Attack/Multiattack runtime is not loaded for deferred-effect selection.");
            }
            if (attacks.legalChoiceAvailable(member, setup)) return null;
          }
          const target = runtime.candidate(member, setup);
          return target ? { payload: { targetId: target.combatant_id } } : null;
        },
        resolve: ({ sequence, round, member, setup }, candidate) => {
          const runtime = DE();
          if (!runtime) throw new Error("Deferred-effect runtime is not loaded.");
          const event = runtime.resolve(sequence, round, member, setup, candidate.payload.targetId);
          if (!event) throw new Error("Deferred-effect candidate became illegal before resolution.");
          return { events: [event], sequence: sequence + 1 };
        },
      });
    } catch (error) {
      console.error("Deferred Main Action provider installation failed", { error });
      throw error;
    }
  }

  install();
  window.IRON_PIT_BROWSER_DEFERRED_MAIN_ACTION_PROVIDER = { install };
})();
