(() => {
  "use strict";

  const RULESETS = Object.freeze(["2014", "2024"]);
  const P = () => window.IRON_PIT_BROWSER_MAIN_ACTION_PROFILES;
  const CATEGORIES = () => P().CATEGORIES;
  const PROFILES = () => P().PROFILES;
  const knownCategories = () => new Set(Object.values(CATEGORIES()));
  const providers = new Map();

  function requireProfile(profileId) {
    const profile = PROFILES()[profileId];
    if (!profile) throw new Error(`Unknown Main Action opportunity profile: ${String(profileId)}.`);
    return profile;
  }

  function rulesetFrom(ctx) {
    if (!ctx || typeof ctx !== "object" || Array.isArray(ctx)) {
      throw new Error("Main Action selection requires a context object.");
    }
    if (!Number.isInteger(ctx.sequence) || ctx.sequence < 0) {
      throw new Error("Main Action selection requires a non-negative integer sequence.");
    }
    const ruleset = ctx.member?.state?.template?.ruleset;
    if (!RULESETS.includes(ruleset)) {
      throw new Error(`Main Action selection requires ruleset 2014 or 2024; received ${String(ruleset)}.`);
    }
    return ruleset;
  }

  function validateProvider(descriptor) {
    if (!descriptor || typeof descriptor !== "object" || Array.isArray(descriptor)) {
      throw new Error("Main Action provider must be a descriptor object.");
    }
    if (typeof descriptor.id !== "string" || !descriptor.id.trim()) {
      throw new Error("Main Action provider requires a stable non-empty id.");
    }
    if (!knownCategories().has(descriptor.category)) {
      throw new Error(`Main Action provider "${descriptor.id}" has unknown category: ${String(descriptor.category)}.`);
    }
    if (!Array.isArray(descriptor.rulesets) || descriptor.rulesets.length === 0) {
      throw new Error(`Main Action provider "${descriptor.id}" must declare one or more rulesets.`);
    }
    if (new Set(descriptor.rulesets).size !== descriptor.rulesets.length
      || descriptor.rulesets.some((ruleset) => !RULESETS.includes(ruleset))) {
      throw new Error(`Main Action provider "${descriptor.id}" has invalid ruleset scope.`);
    }
    if (typeof descriptor.discover !== "function" || typeof descriptor.resolve !== "function") {
      throw new Error(`Main Action provider "${descriptor.id}" requires discover(ctx) and resolve(ctx, candidate).`);
    }
  }

  function registerProvider(descriptor) {
    validateProvider(descriptor);
    const id = descriptor.id.trim();
    if (providers.has(id)) throw new Error(`Main Action provider "${id}" is already registered.`);
    providers.set(id, {
      id,
      category: descriptor.category,
      rulesets: [...descriptor.rulesets],
      discover: descriptor.discover,
      resolve: descriptor.resolve,
    });
  }

  function providerFailure(provider, stage, ctx, error) {
    console.error("Main Action provider failed", {
      providerId: provider.id,
      category: provider.category,
      stage,
      combatant: ctx.member?.combatant_id,
      ruleset: ctx.member?.state?.template?.ruleset,
      error,
    });
    const wrapped = new Error(`Main Action provider "${provider.id}" failed during ${stage}: ${error.message || error}.`);
    wrapped.cause = error;
    throw wrapped;
  }

  function discoverCandidates(profileId, ctx) {
    const profile = requireProfile(profileId);
    const ruleset = rulesetFrom(ctx);
    const allowed = new Set(profile);
    const candidates = [];
    for (const provider of providers.values()) {
      if (!allowed.has(provider.category) || !provider.rulesets.includes(ruleset)) continue;
      let discovered;
      try { discovered = provider.discover({ ...ctx, opportunityProfile: profileId }); }
      catch (error) { providerFailure(provider, "discover", ctx, error); }
      if (discovered == null) continue;
      if (typeof discovered !== "object" || Array.isArray(discovered)) {
        throw new Error(`Main Action provider "${provider.id}" discover result must be null or an object.`);
      }
      const payload = discovered.payload ?? {};
      if (typeof payload !== "object" || Array.isArray(payload)) {
        throw new Error(`Main Action provider "${provider.id}" candidate payload must be an object.`);
      }
      candidates.push(Object.freeze({ providerId: provider.id, category: provider.category, opportunityProfile: profileId, combatantId: ctx.member.combatant_id, turnKey: ctx.turnKey ?? null, payload }));
    }
    return candidates;
  }

  function selectCandidate(profileId, candidates) {
    const profile = requireProfile(profileId);
    if (!Array.isArray(candidates)) throw new Error("Main Action candidates must be an array.");
    for (const category of profile) {
      const matching = candidates.filter((candidate) => candidate?.opportunityProfile === profileId && candidate?.category === category);
      if (matching.length > 1) {
        throw new Error(`Main Action policy found multiple candidates in category "${category}".`);
      }
      if (matching.length === 1) return matching[0];
    }
    return null;
  }

  function resolveCandidate(profileId, candidate, ctx) {
    const ruleset = rulesetFrom(ctx), profile = requireProfile(profileId);
    if (!candidate || typeof candidate !== "object") throw new Error("Main Action resolution requires a candidate.");
    if (candidate.opportunityProfile !== profileId || candidate.combatantId !== ctx.member.combatant_id
      || candidate.turnKey !== (ctx.turnKey ?? null)
      || !candidate.payload || typeof candidate.payload !== "object" || Array.isArray(candidate.payload)) {
      throw new Error("Main Action candidate does not match the current opportunity/combatant/turn.");
    }
    const provider = providers.get(candidate.providerId);
    if (!profile.includes(candidate.category)
      || !provider || provider.category !== candidate.category || !provider.rulesets.includes(ruleset)) {
      throw new Error("Main Action candidate does not match its opportunity profile/provider/ruleset.");
    }
    let result;
    try { result = provider.resolve({ ...ctx, opportunityProfile: profileId }, candidate); }
    catch (error) { providerFailure(provider, "resolve", ctx, error); }
    if (!result || !Array.isArray(result.events)
      || !Number.isInteger(result.sequence) || result.sequence < ctx.sequence) {
      throw new Error(`Main Action provider "${provider.id}" returned an invalid resolution result.`);
    }
    return { events: result.events, sequence: result.sequence };
  }

  function _resetForTests() { providers.clear(); }

  window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION = {
    get CATEGORIES() { return CATEGORIES(); }, get PROFILES() { return PROFILES(); }, registerProvider, discoverCandidates, selectCandidate,
    resolveCandidate, _resetForTests,
  };
})();
