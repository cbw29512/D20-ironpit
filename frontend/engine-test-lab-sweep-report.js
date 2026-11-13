(() => {
  "use strict";
  // Sweep report schema:
  // - start_case/completed are absolute 1-based case indexes.
  // - processed/passed/failed count only the current run segment.
  // - failure_cases stores [case_number, ...error_code_ids] for EVERY failure.
  // - failure_codebook translates compact IDs to exact error messages.
  // - failures is a small set of examples, never the entire 100k matrix.
  // The immutable source_rosters snapshot + seed allow exact matchup replay.
  const SAMPLE_LIMIT = 100;
  const EVENT_SAMPLE_LIMIT = 30;

  function verifyRuntime() {
    try {
      // A missing shared module must block the sweep up front, not produce
      // tens of thousands of misleading monster-specific failure records.
      const required = [
        ["formation attack", "IRON_PIT_BROWSER_FORMATION_ENGAGEMENT", "weaponTargetAllowed"],
        ["formation area", "IRON_PIT_BROWSER_FORMATION_AREA_TARGETING", "coneFrontlineTargets"],
        ["death trigger", "IRON_PIT_BROWSER_DEATH_TRIGGER_DISPATCH", "resolvePending"],
        ["breakable control", "IRON_PIT_BROWSER_BREAKABLE_CONDITION_OBJECT", "preferFreshLimitedControl"],
        ["target-chosen save", "IRON_PIT_BROWSER_TARGET_CHOSEN_SAVE", "choose"],
      ];
      const missing = required.filter(([, key, method]) =>
        typeof window[key]?.[method] !== "function");
      if (missing.length)
        throw new Error("Test All cannot start: missing shared browser runtimes: "
          + missing.map(row => row[0]).join(", ") + ". Refresh the beta page.");
    } catch (error) {
      console.error("Test All shared runtime preflight failed", error);
      throw error;
    }
  }

  function create(plan, seed, startIndex) {
    try {
      if (!Number.isInteger(startIndex) || startIndex < 0 || startIndex >= plan.total)
        throw new RangeError("Test All starting case must exist in the plan.");
      return {
        generated_at: new Date().toISOString(), seed,
        engine: "IRON_PIT_BROWSER_TURBO.runSeeded",
        coverage_kind: "observed fight behavior only; not full RAW certification",
        mode: plan.mode, total: plan.total, start_case: startIndex + 1,
        completed: startIndex, processed: 0, passed: 0, failed: 0,
        skipped: plan.total, stopped: false, warnings: 0,
        source_rosters: (plan.editions || []).map(group => ({
          edition: group.edition,
          hero_ids: [...group.hero_ids], monster_ids: [...group.monster_ids],
        })),
        by_edition: {
          "2014": {passed: 0, failed: 0},
          "2024": {passed: 0, failed: 0},
        },
        failures: [], failure_cases: [], failure_codebook: [],
        error_counts: {},
        observed: {event_types: {}, feature_ids: {}, conditions: {}, damage_types: {}},
        report_format: "v2: compact all-case failures with bounded detailed examples",
      };
    } catch (error) {
      console.error("Could not create bounded Iron Pit test report", error);
      throw error;
    }
  }

  function failure(report, entry, index, seed, problems, replay) {
    try {
      const codes = problems.map(problem => {
        const count = report.error_counts[problem] || 0;
        report.error_counts[problem] = count + 1;
        let code = report.failure_codebook.indexOf(problem);
        if (code < 0) {
          code = report.failure_codebook.push(problem) - 1;
          // One console notification per failure class, not per fight.
          console.warn("Iron Pit Test All failure category", {
            case_number: index + 1, problem, seed, label: entry.label,
          });
        }
        return code;
      });
      report.failure_cases.push([index + 1, ...codes]);
      report.failed += 1;
      report.by_edition[entry.selection.ruleset].failed += 1;
      if (report.failures.length < SAMPLE_LIMIT) {
        report.failures.push({
          case_number: index + 1, kind: entry.kind, label: entry.label,
          selection: entry.selection, seed, problems,
          diagnostic_id: replay?.diagnostic_id || null,
          ...(replay?.battle ? {
            sample_events: (replay.battle.events || []).slice(0, EVENT_SAMPLE_LIMIT),
          } : {}),
        });
      }
    } catch (error) {
      console.error("Unable to record compact test failure", {index, error});
      throw error;
    }
  }

  function advance(report, index, problems) {
    try {
      if (!problems.length) {
        report.passed += 1;
      }
      report.processed += 1;
      report.completed = index + 1;
      report.skipped = report.total - report.processed;
    } catch (error) {
      console.error("Unable to advance Test All report", {index, error});
      throw error;
    }
  }

  window.IRON_PIT_TEST_ALL_REPORT = {verifyRuntime, create, failure, advance};
})();
