(() => {
  "use strict";
  try {
    const selection = window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
    if (!selection?.registerProvider || !selection.CATEGORIES.BARRIER) {
      throw new Error("Generic barrier provider requires the authoritative Action selector.");
    }
    selection.registerProvider({
      id: "source-neutral-offensive-barrier",
      category: selection.CATEGORIES.BARRIER,
      rulesets: ["2014", "2024"],
      discover: ({member, setup}) => {
        if (!(member.state.template.persistent_barrier_actions || [])
          .some((action) => action.onCreationSave)) return null;
        const runtime = window.IRON_PIT_BROWSER_BARRIER_OFFENSE;
        if (!runtime?.choose) throw new Error("Offensive barrier placement runtime missing.");
        const selected = runtime.choose(member, setup);
        return selected ? {payload: {
          selected, delivery: "ability", expectedDamage: selected.expectedDamage,
        }} : null;
      },
      resolve: ({sequence, round, member, setup, turnKey}, candidate) => {
        const runtime = window.IRON_PIT_BROWSER_BARRIER_OFFENSE;
        if (!runtime?.resolve) throw new Error("Offensive barrier resolution runtime missing.");
        return runtime.resolve(sequence, round, member, setup, turnKey, candidate.payload.selected);
      },
    });
  } catch (error) {
    console.error("Failed to register universal offensive barrier provider", {error});
    throw error;
  }
})();