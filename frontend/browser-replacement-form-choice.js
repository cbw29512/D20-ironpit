(() => {
  "use strict";

  function chooseProfitableChangeShape(current, candidates, expectedFutureTurns, changeShapeActionCost) {
    if (!Number.isInteger(expectedFutureTurns) || expectedFutureTurns < 0) {
      throw new Error("Future turn estimate must be a nonnegative integer.");
    }
    if (!Number.isFinite(changeShapeActionCost) || changeShapeActionCost < 0) {
      throw new Error("Change Shape Action opportunity cost must be finite and nonnegative.");
    }
    const valid = (row) => {
      if (!row || !row.formTemplateId) throw new Error("Each form requires a source ID.");
      for (const key of ["outgoingDamagePerRound", "incomingDamagePerRound", "controlValuePerRound", "incomingConditionCostPerRound"]) {
        const value = Number(row[key] ?? 0);
        if (!Number.isFinite(value) || value < 0) {
          throw new Error("Projected source combat values must be finite and nonnegative.");
        }
      }
    };
    valid(current);
    if (!current.legallyCompiled) throw new Error("Baseline form must be source-validated.");
    const seen = new Set();
    let bestScore = 0;
    let bestId = null;
    for (const row of candidates) {
      valid(row);
      if (row.formTemplateId === current.formTemplateId || seen.has(row.formTemplateId)) {
        throw new Error("Change Shape shortlist includes baseline or duplicate.");
      }
      seen.add(row.formTemplateId);
      if (!row.legallyCompiled) continue;
      const delta = (
        Number(row.outgoingDamagePerRound) - Number(current.outgoingDamagePerRound)
        + Number(current.incomingDamagePerRound) - Number(row.incomingDamagePerRound)
        + Number(row.controlValuePerRound || 0) - Number(current.controlValuePerRound || 0)
        + Number(current.incomingConditionCostPerRound || 0) - Number(row.incomingConditionCostPerRound || 0)
      );
      const score = delta * expectedFutureTurns - changeShapeActionCost;
      if (score > bestScore || (score === bestScore && bestId !== null && row.formTemplateId < bestId)) {
        bestScore = score;
        bestId = row.formTemplateId;
      }
    }
    return bestId;
  }

  function chooseProfitableReplacementForm(current, candidates, expectedFutureTurns, transformationOpportunityCost) {
    // Only source-certified legal forms and accurate class/source Action,
    // Bonus Action, resource, form HP and Temporary HP projections may enter.
    return chooseProfitableChangeShape(
      current, candidates, expectedFutureTurns, transformationOpportunityCost,
    );
  }

  // Pure expected-value selector: never invokes a transformation by itself.
  // Combat projections and full source capability merge must be certified before binding.
  window.IRON_PIT_BROWSER_REPLACEMENT_FORM_CHOICE = { chooseProfitableChangeShape, chooseProfitableReplacementForm };
})();
