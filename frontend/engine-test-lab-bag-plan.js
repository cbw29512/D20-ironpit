(() => {
  "use strict";
  // Plan schema: {total, groups:[{edition, kind, ids}], at(index)}.
  // Each certified monster and pregen appears exactly once per edition.
  const EDITIONS = ["2014", "2024"];

  function create() {
    try {
      const roster = window.IRON_PIT_TEST_ALL_PLAN?.roster;
      if (!roster) throw new Error("The certified source-roster planner is missing.");
      const groups = EDITIONS.flatMap(edition => {
        const source = roster(edition);
        return [
          {edition, kind: "monster", ids: source.monster_ids},
          {edition, kind: "pregen", ids: source.hero_ids},
        ];
      });
      const total = groups.reduce((sum, group) => sum + group.ids.length, 0);
      if (!total) throw new Error("No source cards found for Punching Bag testing.");
      function at(index) {
        try {
          if (!Number.isInteger(index) || index < 0 || index >= total)
            throw new RangeError("Punching Bag test index out of bounds.");
          let remaining = index;
          for (const group of groups) {
            if (remaining >= group.ids.length) {
              remaining -= group.ids.length;
              continue;
            }
            return {
              kind: "punching_bag",
              edition: group.edition,
              source_kind: group.kind,
              source_id: group.ids[remaining],
              label: `${group.edition} ${group.kind}: ${group.ids[remaining]} vs Punching Bag`,
            };
          }
          throw new Error("Punching Bag plan index was not resolved.");
        } catch (error) {
          console.error("Failed Punching Bag test plan item", {index, error});
          throw error;
        }
      }
      return {total, groups, at};
    } catch (error) {
      console.error("Could not construct all-monster-and-pregen bag plan", error);
      throw error;
    }
  }
  window.IRON_PIT_TEST_BAG_PLAN = {create};
})();
