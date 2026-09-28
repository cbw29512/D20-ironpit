(() => {
  "use strict";

  function install() {
    try {
      const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
      const rage = window.IRON_PIT_BROWSER_RAGE;
      if (!hooks || !rage) {
        throw new Error("Rage hooks require ability-hooks and rage runtimes.");
      }
      const bonusPhase = hooks.PHASES.BONUS_ACTION_WINDOW;
      const finalizePhase = hooks.PHASES.TURN_FINALIZE;
      const bonusIds = () => new Set(hooks.abilitiesFor(bonusPhase).map((item) => item.id));

      if (!bonusIds().has("rage-enter")) hooks.registerAbility(bonusPhase, {
        id: "rage-enter", priority: 10, rulesets: ["2014", "2024"],
        appliesTo: (_member, ctx) => ctx.bonusActionCheckpoint === "beforeEscape",
        resolve: ({ sequence, round, member, setup, turnKey }) => {
          const event = rage.enter(sequence, round, member);
          if (!event) return null;
          const events = [event];
          let nextSequence = sequence + 1;
          const fraction = member.state.template.instinctive_pounce_fraction || 0;
          if (fraction > 0) {
            const movement = window.IRON_PIT_BROWSER_ACTIVATION_MOVEMENT;
            if (!movement) throw new Error("Rage Instinctive Pounce requires activation-movement runtime.");
            const moved = movement.resolve(
              nextSequence, round, member, setup, { speedFraction: fraction, turnKey },
            );
            events.push(...moved.events);
            nextSequence = moved.sequence;
            window.IRON_PIT_BROWSER_PALADIN_AURAS_2014?.sync(setup);
          }
          return { events, sequence: nextSequence, claimed: true };
        },
      });

      if (!bonusIds().has("rage-maintain")) hooks.registerAbility(bonusPhase, {
        id: "rage-maintain", priority: 120, rulesets: ["2024"],
        appliesTo: (_member, ctx) => ctx.bonusActionCheckpoint === "postAction",
        resolve: ({ sequence, round, member }) => {
          const event = rage.maintain(sequence, round, member);
          return event ? { events: [event], sequence: sequence + 1, claimed: true } : null;
        },
      });

      if (!hooks.abilitiesFor(finalizePhase).some((item) => item.id === "rage-expiry-cleanup")) {
        hooks.registerAbility(finalizePhase, {
          id: "rage-expiry-cleanup", priority: 100, rulesets: ["2014", "2024"],
          resolve: ({ sequence, round, member }) => ({
            ...rage.cleanupExpired(sequence, round, member),
            claimed: false,
          }),
        });
      }
    } catch (error) {
      console.error("Failed to install Rage ability hooks", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_RAGE_HOOKS = { install };
})();
