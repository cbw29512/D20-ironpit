(() => {
  "use strict";
  // Per-fight schema: immutable identifying fields + the EXACT browser engine
  // events. We replay a single recorded seed, never retain 918 x 100 rounds
  // of events in the summary report (which previously exceeded 400 MB).
  function replayCase(row, attemptIndex) {
    try {
      if (!row || !["2014", "2024"].includes(row.edition) ||
          !["monster", "pregen"].includes(row.kind) || !row.card_id ||
          !Array.isArray(row.attempts))
        throw new Error("Select a source-backed Punching Bag case.");
      if (!Number.isInteger(attemptIndex) || attemptIndex < 0 ||
          attemptIndex >= row.attempts.length)
        throw new RangeError("Selected combat attempt does not exist.");
      const recorded = row.attempts[attemptIndex];
      if (!Number.isInteger(recorded.seed) || recorded.seed < 1 ||
          recorded.seed > 0xffffffff)
        throw new RangeError("Selected combat attempt has an invalid seed.");
      const fight = window.IRON_PIT_TEST_BAG_FIGHT;
      const formatter = window.IRON_PIT_BATTLE_LOG_EXPORT;
      if (!fight?.run || !formatter?.textFromBattle)
        throw new Error("Shared combat replay or battle-log formatter is missing.");
      const entry = {kind: "punching_bag", edition: row.edition,
        source_kind: row.kind, source_id: row.card_id};
      const {replay} = fight.run(entry, recorded.seed);
      const battle = replay?.battle;
      if (!battle || !Array.isArray(battle.events) || !battle.events.length)
        throw new Error("The seeded engine did not produce combat events.");
      if (recorded.diagnostic_id && recorded.diagnostic_id !== replay.diagnostic_id)
        throw new Error("Replay diagnostic differs from the recorded fight; do not label this as the same combat.");
      if (recorded.event_count != null && recorded.event_count !== battle.events.length)
        throw new Error("Replay event count changed since this test was recorded.");
      if (recorded.outcome && recorded.outcome !== battle.outcome)
        throw new Error("Replay outcome differs from the original seeded fight.");
      const metadata = {
        schema_version: 1, type: "iron_pit_combat_transcript",
        edition: row.edition, kind: row.kind, card_id: row.card_id,
        card_name: row.card_name, opponent: "Punching Bag",
        attempt: recorded.attempt, seed: recorded.seed,
        diagnostic_id: replay.diagnostic_id,
        outcome: battle.outcome, rounds: battle.rounds,
        event_count: battle.events.length,
      };
      const narrative = [
        "IRON PIT — ACTUAL COMBAT LOG",
        `${metadata.card_name} (${metadata.edition} ${metadata.kind}) vs ${metadata.opponent}`,
        `Attempt ${metadata.attempt} · Seed ${metadata.seed} · Replay ${metadata.diagnostic_id}`,
        `Outcome ${metadata.outcome} · Rounds ${metadata.rounds} · Events ${metadata.event_count}`,
        "----- START OF COMBAT -----",
        formatter.textFromBattle(battle),
        "----- END OF COMBAT -----",
      ].join("\n");
      return {metadata, narrative, event_json: {...metadata, events: battle.events}};
    } catch (error) {
      console.error("Source-backed Punching Bag combat transcript failed", {
        card_id: row?.card_id, attemptIndex, error,
      });
      throw error;
    }
  }
  window.IRON_PIT_TEST_BAG_COMBAT_LOG = {replayCase};
})();