# QYBE High-Level Development Plan

**Status:** Directional architecture and roadmap  
**Updated:** 2026-07-27  
**Base branch:** `dev`  
**Implementation rule:** roadmap items do not enable production behavior by themselves.

## 1. Product direction

QYBE is a local-first business AI orchestration platform built on the Onyx/QYBE application foundation. A user should be able to express a normal business request while QYBE determines, under organization policy:

- the task and business domain;
- required capabilities and workflow;
- permitted data movement and tools;
- the most appropriate model and inference runtime;
- whether execution remains local or may use an approved external provider;
- how evidence, provenance, cost, latency, and quality are recorded.

QYBE should reuse the mature chat, RAG, connectors, actions/MCP, Deep Research, code execution, document generation, administration, access-control, and deployment foundations inherited from Onyx rather than rebuilding them.

## 2. Non-negotiable constraints

1. The orchestration router remains **shadow-only** until explicitly enabled through a reviewed feature flag.
2. Organization privacy and security policy overrides user model, tool, workflow, and provider preferences.
3. Raw business prompts, private document contents, secrets, and unredacted tool outputs must not be stored in telemetry.
4. Local models and local execution are preferred when they meet the task's quality and latency requirements.
5. External model or tool use requires a positive data-egress decision.
6. New infrastructure capabilities must be provider-neutral and replaceable through adapters.
7. Every optimization must be benchmarked against an unmodified baseline; token reduction alone is not a success criterion.
8. Feature work uses focused branches from an updated `dev`, focused commits, and targeted automated tests.

## 3. Target control-plane flow

The directional control plane is:

```text
User request
  -> Shadow RouteDecision
  -> ChatModelSelectionPreference
  -> ChatWorkflowPreference / TaskModePreference
  -> WorkflowDefinition / WorkflowPlan
  -> CapabilityPlan
  -> DataClassification
  -> DataEgressDecision
  -> ToolPlan
  -> ModelPlan
  -> RuntimePlan
  -> ContextOptimizationPlan
  -> ExecutionGraphPreview
  -> controlled live execution behind feature flags
```

The plan is intentionally declarative. QYBE should first explain what it would do, then execute only after each layer is observable, testable, and governed.

## 4. Core architecture tracks

### 4.1 Orchestration control plane

- Keep the existing multidimensional router advisory and shadow-only.
- Add explicit user preferences for automatic/local/mixed/explicit model selection.
- Add workflow/task preferences without removing existing manual modes.
- Introduce a versioned, provider-neutral `WorkflowDefinition` and `WorkflowRun` model for reusable user and domain workflows.
- Compile workflow definitions into policy-enriched execution graphs rather than executing framework-specific YAML or code directly.
- Build `CapabilityPlan` as a provider-neutral description of required abilities.
- Generate an `ExecutionGraphPreview` before controlled execution.
- Separate planner, worker, and verifier roles where this reduces cost or improves reliability.

### 4.2 Domain packs

- Continue provider-based domain packs rather than hardcoded domain logic.
- Support static defaults and YAML/administrative overlays.
- Keep business function, industry, task type, risk, and data class as separate dimensions.
- Allow domain packs to recommend capabilities, evaluation criteria, tools, and model characteristics, not to bypass policy.
- Add `visual_reasoning_canvas` as an optional capability for engineering and academic domain packs, with handwriting, equations, diagrams, spatial context, evidence binding, and explicit AI-draft review.
- Follow the dedicated [PenEcho visual reasoning integration plan](PENECHO_VISUAL_REASONING_DOMAIN_PLAN.md): QYBE owns orchestration, policy, RAG, provenance, persistence, and model/runtime selection, while PenEcho remains a replaceable reference implementation or isolated adapter candidate rather than a core dependency.

### 4.3 Model and runtime resolution

- Preserve the abstraction `Capability Planner -> Model Resolver -> Runtime Resolver`.
- Auto-detect available local models and runtimes instead of maintaining a fixed model list.
- Track runtime metadata such as context limit, quantization, throughput, latency, concurrency, tool support, multimodal support, and hardware requirements.
- Support Ollama first while keeping adapters open for vLLM, TensorRT-LLM, SGLang, LiteLLM, and later runtimes.
- Treat runtime recommendations as advisory until benchmarked on EdgeXpert/DGX Spark.

### 4.4 Privacy, security, and governance

- Classify the request and each retrieved/tool-produced data object before any external call.
- Enforce organization-level egress, retention, model, tool, and connector policy.
- Keep prompt-safe telemetry limited to hashes, identifiers, decisions, timings, counts, and approved derived metrics.
- Preserve provenance from source retrieval through generated artifact or action.
- Require administrative auditability for policy overrides and controlled live execution.

### 4.5 Tool and MCP planning

- Represent tool use as a `ToolPlan` with capability, authorization, data class, side effects, retry policy, and verification requirements.
- Prefer typed, bounded tool outputs over unstructured text.
- Separate read-only discovery from state-changing actions.
- Require confirmation or policy approval for material external side effects.

### 4.6 Documents and business artifacts

- Continue the Documents/Univer track for editable business artifacts.
- Keep artifact generation separate from final approval and external publication.
- Preserve source citations and evidence links in reports and generated documentation.
- Add document workflows incrementally without coupling them to one model provider.

### 4.7 Knowledge-to-skill compiler

- Treat book/document-to-skill compilation as an R&D track, not an immediate production dependency.
- Use rights/classification checks, isolated extraction, normalized corpora, local-model compilation, provenance checks, private disabled drafts, administrative review, versioning, and rollback.
- Benchmark RAG-only, compiled-skill-only, and hybrid Skill+RAG behavior.

### 4.8 Sandbox business application builder

- Explore local-first generation of small internal business applications in an isolated sandbox.
- Reuse QYBE document, connector, tool, code-execution, and policy infrastructure.
- Require generated code review, tests, dependency inspection, egress controls, and explicit deployment approval.

### 4.9 Web discovery and browser execution

- Separate web discovery from page execution: a provider-neutral `SearchProvider` finds candidate URLs, while a provider-neutral `BrowserProvider` retrieves pages, executes permitted JavaScript, performs bounded interactions, and returns typed content with provenance.
- Keep OpenSERP, SearXNG, external search APIs, and future discovery providers replaceable; Lightpanda is not a search-engine replacement.
- Define QYBE-owned browser adapters for static HTTP retrieval, Lightpanda, and Chromium/Playwright.
- Route static and simple pages to HTTP retrieval, JavaScript-dependent extraction to the Lightpanda fast path, and screenshots, PDFs, visual verification, complex authentication, unsupported sites, or failed Lightpanda sessions to Chromium.
- Retain Lightpanda as an experimental optional provider, not the sole browser runtime and not a production default until QYBE-specific compatibility and reliability gates pass.
- Keep QYBE responsible for orchestration, model selection, tool planning, session policy, evidence, and fallback; do not delegate these responsibilities to Lightpanda's native LLM-agent mode.
- Apply `DataClassification`, `DataEgressDecision`, organization allow/deny policy, SSRF protection, private-network and metadata-endpoint blocking, response-size limits, navigation timeouts, cookie/session isolation, retention limits, and complete source provenance before controlled use.
- Deploy Lightpanda as an isolated, version-pinned, glibc-based ARM64 sidecar where appropriate, with telemetry and core dumps disabled, health checks, bounded concurrency, process recycling, and automatic Chromium fallback.
- Benchmark extraction correctness, JavaScript compatibility, latency, memory, crash rate, timeout rate, session isolation, and fallback frequency on a representative QYBE web corpus; upstream benchmark claims are not QYBE performance evidence.
- Preserve an explicit licensing boundary: prefer unmodified process-level integration through MCP, CDP, or CLI, retain notices and corresponding-source obligations, and require legal review before modifying or commercially redistributing AGPL-covered Lightpanda components.

### 4.10 User-defined workflows and runtime adapters

- Build a template-first workflow builder with constrained step types, typed inputs/outputs, graph validation, budgets, approvals, checkpoints, versioning, and execution preview.
- Start with an Academic Research and Writing workflow: evidence-first source research, outline approval, bounded chapter generation, citation validation, consistency checks, and editable artifact assembly.
- Keep workflow definitions independent of any execution framework.
- Define a QYBE-owned `WorkflowRuntimeAdapter` so QYBE-native, PraisonAI, and future runtimes remain replaceable.
- QYBE retains authority over identity, RBAC, secrets, tools, connectors, model/runtime resolution, data classification, egress, provenance, persistence, telemetry, and artifacts.
- Follow the dedicated [PraisonAI workflow runtime integration plan](PRAISONAI_WORKFLOW_RUNTIME_PLAN.md). PraisonAI is a high-opportunity isolated adapter candidate and reference implementation, not the QYBE orchestration or policy authority.

## 5. Context and cost optimization track

QYBE should have a provider-neutral `ContextOptimizationPlan` between runtime planning and the final model request. It may select deterministic reduction, cache alignment, retrieval compaction, reversible storage, or passthrough based on content type, sensitivity, task risk, model context, and measured benefit.

The target interface should describe:

- content type and sensitivity;
- original token estimate;
- allowed transformations;
- protected messages and evidence;
- selected strategy and reason;
- reversibility/retrieval mechanism;
- expected token and latency impact;
- quality-risk classification;
- audit/shadow/active mode.

This track must remain independent of any single optimization library.

## 6. Headroom evaluation and decision

### 6.1 Evaluated project

- Repository: [headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom)
- Evaluated release line: `v0.32.0` (latest release observed on 2026-07-23)
- License: Apache-2.0
- Maturity marker: Beta
- Main integration surfaces: Python library, local proxy, MCP server, TypeScript SDK, and coding-agent wrappers.

Headroom implements a context-optimization pipeline that includes content routing, deterministic compression of structured tool output and logs, cache-prefix alignment, context-window management, reversible Compress-Cache-Retrieve (CCR), metrics, and optional ML-based components.

### 6.2 Why it is relevant to QYBE

Headroom is relevant in two distinct scopes.

#### A. Immediate developer-side use

It may reduce paid coding-agent input/output during long QYBE development sessions, particularly when sessions contain repeated JSON, command output, build/test logs, diffs, issue data, and accumulated tool results.

This use is outside the QYBE product runtime:

```text
Claude Code / Codex / supported coding agent
  -> local Headroom proxy or wrapper
  -> model provider
```

This is the lowest-risk path because it does not change QYBE application behavior.

#### B. Future QYBE product R&D

Headroom is a useful reference implementation and optional adapter candidate for the planned `ContextOptimizationPlan`, especially for:

- large structured connector/tool results;
- repetitive logs and test/build output;
- prefix-cache stabilization;
- reversible retrieval of omitted detail;
- optimization metrics and audit/simulation modes.

It must not become the QYBE orchestration authority. QYBE policy, data classification, evidence protection, model selection, and execution planning remain outside and above any Headroom adapter.

### 6.3 Important limitations and risks

1. **Workload dependence.** The strongest reported gains are for large JSON arrays, logs, and long tool-heavy sessions. Short chats and code-centric turns may save little.
2. **Quality risk.** Reversible storage prevents permanent deletion but does not guarantee the model will realize that omitted information must be retrieved.
3. **Latency variance.** Typical overhead may be modest, but large or ML-based transformations can add material latency and tail latency.
4. **Rapid evolution.** Documentation and behavior are changing quickly; public claims for code, RAG, and image compression are not fully consistent across current documentation pages.
5. **Dependency and supply-chain surface.** Full installations include a substantial optional dependency graph. QYBE must pin, scan, and minimize extras.
6. **Telemetry defaults.** Headroom telemetry is enabled by default. Any QYBE evaluation must explicitly set `HEADROOM_TELEMETRY=off` and independently verify emitted data.
7. **Proxy criticality.** A transparent proxy enters the provider request path and therefore requires fail-open/passthrough behavior, health checks, timeouts, circuit breaking, and credential isolation.
8. **Local storage governance.** CCR, memory, metrics, and learning stores can contain sensitive context and must be session-scoped, access-controlled, retention-limited, and encrypted where required.
9. **Instruction-file mutation.** `headroom learn` can update agent instruction files. It must not write tracked `CLAUDE.md`, `AGENTS.md`, or equivalent files automatically in the QYBE repository.
10. **Local-model economics.** On local inference, token reduction may improve context capacity and latency, but it does not directly reduce per-token API cost; compression CPU/ML overhead must be justified separately.

### 6.4 Decision

**Decision: include Headroom in the QYBE high-level plan as an experimental, replaceable optimization technology—not as a core production dependency.**

The immediate recommendation is a controlled developer-side pilot. Product integration remains a later R&D track after the orchestration control plane, data classification, data-egress policy, and execution-plan preview are stable.

## 7. Headroom adoption phases

### Phase H0 — Static review and threat model

- Pin the exact Headroom version under evaluation.
- Review the proxy, compression, CCR, telemetry, logging, credential-forwarding, and learning code paths.
- Produce a dependency/SBOM and vulnerability scan for only the required extras.
- Define sensitive-data handling, retention, deletion, and fail-open rules.

**Exit:** approved threat model and no unbounded prompt/tool-content logging.

### Phase H1 — Developer-side audit pilot

- Run Headroom locally around one supported coding agent.
- Disable telemetry and automatic instruction-file writes.
- Start in audit/simulate mode where available.
- Use a separate local workspace and do not commit generated Headroom state.
- Measure representative QYBE tasks: repository exploration, test failures, build logs, GitHub triage, and long refactoring sessions.

**Exit:** at least 15% net paid-token reduction on representative paid-agent sessions with no statistically meaningful regression in task completion, patch correctness, or test outcomes.

### Phase H2 — Developer-side optimized pilot

- Enable only deterministic, reversible transformations that passed H1.
- Protect current code, system instructions, user requirements, errors, failing tests, and recent diffs.
- Keep direct non-proxied agent invocation as a documented fallback.

**Exit:** stable operation over multiple QYBE development sessions and no credential, context-retrieval, or repository-state incidents.

### Phase H3 — QYBE shadow adapter

- Implement a QYBE-owned `ContextOptimizer` adapter contract.
- Add a Headroom adapter behind a feature flag.
- Feed it only policy-approved, typed tool outputs after `DataClassification` and `DataEgressDecision`.
- Record the proposed transform, token estimate, latency, protected fields, and quality-risk decision without altering the model request.

**Exit:** shadow metrics demonstrate a valuable eligible workload and acceptable projected risk.

### Phase H4 — Deterministic product pilot

- Enable deterministic compression for selected low-risk structured outputs only.
- Start with administrative or internal evaluation tenants.
- Keep user messages, system prompts, active code, citations, ACL metadata, and high-risk evidence unchanged.
- Require automatic passthrough on error, timeout, unsupported type, or negative measured savings.

**Exit:** quality gates pass on QYBE-specific golden datasets and adversarial omission tests.

### Phase H5 — Reversible retrieval and advanced optimization

- Add session-scoped CCR with explicit tool semantics and bounded retention.
- Test whether models reliably request originals when required.
- Evaluate optional ML text/code/image compression separately.
- Promote only strategies that outperform simpler QYBE-native compaction.

**Exit:** retrieval reliability, privacy, latency, and answer-quality thresholds are met under production-like load.

## 8. QYBE-specific evaluation matrix

Every candidate optimization must compare baseline and optimized runs using the same model, tools, prompt, data, and seed where supported.

| Dimension | Required measure |
|---|---|
| Correctness | task success, answer score, tool-call validity, test pass rate |
| Evidence | citation/source preservation, omitted critical facts, ACL metadata preservation |
| Agent behavior | number of tool calls, retries, retrieval requests, loops, premature completion |
| Tokens | input, cached input, output, retrieved-original tokens, net reduction |
| Latency | compression time, time to first token, total time, p50/p95/p99 |
| Cost | provider cost saved minus additional infrastructure/compute cost |
| Reliability | passthrough rate, proxy errors, timeout rate, recovery behavior |
| Privacy | emitted telemetry fields, local stored content, retention and deletion verification |
| Operability | health checks, observability, upgrade/rollback effort, configuration drift |

Minimum product-pilot gates:

- no raw prompt or private-content telemetry;
- no reduction in authorization or provenance metadata;
- no material regression in task success or tool-call correctness;
- measurable net benefit after compression and retrieval overhead;
- automatic passthrough and one-step rollback;
- version-pinned, scanned dependency set;
- organization policy can disable optimization globally or by data class.

## 9. Implementation boundaries

Do not:

- fork Headroom into QYBE core before the adapter evaluation is complete;
- route all chat traffic through it by default;
- compress user intent, system policy, active code, citations, permissions, or safety controls;
- rely on Headroom telemetry as QYBE product telemetry;
- expose provider credentials to an unauthenticated or network-accessible proxy;
- treat reported upstream benchmark percentages as QYBE performance evidence;
- allow `headroom learn` to modify tracked repository instructions automatically.

Prefer:

- a QYBE-owned provider-neutral interface;
- audit/shadow-first rollout;
- deterministic and typed transforms before ML transforms;
- local execution with telemetry disabled;
- content-addressed, bounded, reversible storage;
- QYBE-specific golden datasets and adversarial tests;
- a simple passthrough fallback.

## 10. Roadmap priority

1. Stabilize the fresh QYBE/Onyx foundation, development workflow, branding, localization, and upstream upgrade process.
2. Continue shadow orchestration, preferences, `CapabilityPlan`, and evaluation APIs.
3. Implement data classification, egress decisions, and declarative tool/model/runtime plans.
4. Define `WorkflowDefinition`, `WorkflowRun`, `WorkflowRuntimeAdapter`, and workflow-aware `ExecutionGraphPreview` contracts.
5. Build the template-first Academic Research and Writing workflow with evidence, outline approval, bounded chapter generation, citation checks, and editable artifact output.
6. Evaluate an isolated PraisonAI shadow adapter after QYBE policy, model, tool, persistence, and event boundaries are enforceable.
7. Add controlled live workflow execution, checkpoints, pause/resume, cancellation, retries, and hard budgets behind feature flags.
8. Define the provider-neutral web discovery and browser-execution contracts, then run a shadow extraction PoC with static HTTP, Lightpanda, and Chromium fallback on a representative QYBE corpus.
9. Define the visual-reasoning capability contract and complete the PenEcho architecture, security, and licensing evaluation for engineering and academic domain packs.
10. Run the developer-side Headroom pilot in parallel because it is isolated from product runtime.
11. Add `ContextOptimizationPlan` and a Headroom shadow adapter only after policy boundaries are stable.
12. Consider controlled production workflow execution, browser routing, and context optimization only after QYBE-specific quality, provenance, privacy, security, compatibility, latency, licensing, durability, and rollback gates pass.

## 11. Decision log

- **2026-07-27 — PraisonAI opportunity:** high strategic fit for user-defined and domain-template workflows, especially research, planning, iterative generation, validation, and artifact production.
- **2026-07-27 — PraisonAI boundary:** QYBE owns the canonical workflow schema, policy enrichment, model/tool brokers, run state, provenance, telemetry, and user experience. PraisonAI is a replaceable isolated runtime adapter candidate.
- **2026-07-27 — Workflow MVP:** begin with a governed Academic Research and Writing template before exposing a general visual workflow builder or arbitrary framework configuration.
- **2026-07-27 — Workflow rollout:** declarative definition and preview first; shadow adapter second; controlled execution, durability, advanced branching, parallelism, and loops only after measurable gates pass.
- **2026-07-27 — Lightpanda:** retained as an experimental optional `BrowserProvider` for JavaScript-rendered extraction and simple bounded browser interactions. It does not replace OpenSERP/SearXNG discovery or Chromium compatibility and visual execution.
- **2026-07-27 — Browser boundary:** QYBE owns search routing, organization policy, data classification, session isolation, tool orchestration, provenance, quality checks, and fallback. Lightpanda is a replaceable fast path; Chromium remains the compatibility, screenshot, PDF, visual-verification, and complex-authentication path.
- **2026-07-27 — Lightpanda rollout:** start with a pinned isolated ARM64 sidecar, telemetry and core dumps disabled, strict SSRF/network controls, shadow evaluation, and automatic fallback. AGPL obligations and commercial distribution implications require explicit review before modification or redistribution.
- **2026-07-23 — PenEcho:** retained as a reference implementation and optional isolated adapter candidate for engineering and academic visual reasoning; no code integration is approved by this roadmap entry.
- **2026-07-23 — PenEcho boundary:** visual reasoning is a provider-neutral QYBE domain capability. QYBE retains orchestration, policy, RAG, provenance, persistence, and model/runtime authority.
- **2026-07-23 — PenEcho licensing:** protocol study and value validation precede any embedding; AGPL obligations or an alternative commercial license require explicit approval before PenEcho code enters the QYBE product boundary.
- **2026-07-23 — Headroom:** useful enough to retain in the roadmap as a developer-efficiency pilot and future optional context-optimization adapter. It is not approved as a QYBE core runtime dependency or default proxy.
- **2026-07-23 — Integration boundary:** QYBE owns policy and the `ContextOptimizationPlan`; Headroom, QYBE-native compaction, and future alternatives are replaceable implementations.
- **2026-07-23 — Rollout:** telemetry off, audit/shadow first, deterministic structured-output optimization before ML compression, and mandatory baseline benchmarking.
