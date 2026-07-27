# PraisonAI Workflow Runtime Integration Plan

**Status:** Directional architecture, opportunity assessment, and staged evaluation  
**Updated:** 2026-07-27  
**Base branch:** `dev`  
**Decision:** High-opportunity workflow accelerator and adapter candidate; not approved as QYBE's core orchestration authority.

## 1. Executive assessment

PraisonAI is a strong match for QYBE's planned user-defined workflows because it already provides multi-agent execution, sequential and hierarchical processes, routing, parallel execution, loops, evaluator/optimizer patterns, YAML definitions, structured outputs, callbacks, hooks, approvals, sessions, persistence, MCP/tool integration, and local-model support.

The opportunity is significant, especially for long-running business and academic workflows that combine research, planning, iterative generation, validation, and artifact production.

| Dimension | Assessment |
|---|---|
| Product opportunity | **9/10** — directly supports reusable end-user workflows and domain templates |
| Strategic fit with QYBE | **9/10** — complements the planned capability, tool, model, runtime, and execution graph layers |
| Fit as a direct embedded core dependency | **5/10** — substantial overlap with QYBE/Onyx RAG, agents, tools, memory, persistence, and model routing |
| Fit as an isolated runtime adapter | **8/10** — strong if QYBE owns policy, workflow schema, execution state, and user experience |
| Delivery complexity | **Medium-high** — the first template is tractable, but durable pause/resume, provenance, approval, and failure recovery require QYBE-owned infrastructure |
| Recommended priority | **High after declarative workflow and policy contracts are stable** |

**Recommendation:** implement a QYBE-owned workflow control plane and user experience, then evaluate PraisonAI as one replaceable execution adapter behind that boundary. Start with an academic research-and-writing template rather than a fully open arbitrary workflow canvas.

## 2. Why PraisonAI is relevant

PraisonAI exposes several capabilities that map closely to the QYBE roadmap:

- sequential and manager-coordinated multi-agent execution;
- workflow routing, parallel branches, loops, and bounded iterative refinement;
- reusable YAML and programmatic workflow definitions;
- structured Pydantic/JSON outputs for step contracts;
- callbacks and hooks for execution events, tool calls, errors, and task completion;
- human approval for higher-risk tool operations;
- sessions, persistence, and resume-oriented APIs;
- MCP and custom tool integration;
- support for local Ollama-compatible endpoints and external model providers;
- active development under the MIT license.

These features can reduce the time needed to prototype workflow execution semantics, especially the orchestration patterns that would otherwise require substantial custom code.

## 3. Why QYBE must not adopt it wholesale

PraisonAI overlaps with multiple capabilities already present or planned in QYBE/Onyx:

- agents and multi-step research;
- RAG, knowledge, and citations;
- model selection and provider routing;
- MCP and tool execution;
- memory, sessions, and persistence;
- observability and callbacks;
- API serving and workflow storage.

Embedding the complete framework as QYBE's primary control plane would create two competing authorities for identity, policy, secrets, model selection, tools, persistence, telemetry, and workflow state. It could also allow workflow-level configuration to bypass QYBE organization policy.

Therefore:

- QYBE owns the canonical workflow definition and versioning;
- QYBE owns identity, tenancy, RBAC, secrets, policy, data classification, egress, model and runtime decisions;
- QYBE owns connectors, tool authorization, side-effect approval, citations, provenance, artifacts, run state, and audit logs;
- PraisonAI receives only an already-authorized execution graph and scoped broker interfaces;
- PraisonAI remains replaceable by a QYBE-native runtime or another workflow engine.

## 4. Target architecture

```text
Workflow Builder / Template UI
  -> WorkflowDefinition
  -> WorkflowValidator
  -> CapabilityPlan enrichment
  -> DataClassification and DataEgressDecision
  -> ToolPlan / ModelPlan / RuntimePlan per step
  -> ExecutionGraphPreview
  -> user or policy approval
  -> WorkflowRuntimeAdapter
       -> QYBE Native Runtime
       -> PraisonAI Isolated Adapter
       -> future runtime adapters
  -> WorkflowEvent stream
  -> QYBE WorkflowRun store, provenance graph, and artifacts
```

The adapter boundary must prevent the runtime from becoming the policy authority.

## 5. QYBE-owned workflow model

The canonical `WorkflowDefinition` should be provider-neutral and versioned. At minimum it should include:

- workflow ID, version, owner, organization, status, and domain pack;
- input schema and required user parameters;
- graph nodes and dependencies;
- step type: `agent`, `tool`, `human_approval`, `branch`, `parallel`, `loop`, `validator`, or `artifact`;
- input references and typed output schema;
- required capabilities rather than hardcoded model names;
- allowed tools and side-effect level;
- data classification and egress constraints;
- timeout, retry, iteration, token, cost, and concurrency budgets;
- checkpoint, pause, resume, cancel, and rollback behavior;
- acceptance criteria and verifier configuration;
- evidence and citation requirements;
- artifact destination and final approval requirement.

A separate `WorkflowRun` should record immutable definition version, resolved plans, step states, attempts, approvals, model/tool decisions, evidence links, costs, timings, errors, and final artifacts.

## 6. First template: Academic Research and Writing

The first workflow should be a governed template that users configure through a form and optional graph view.

### 6.1 User inputs

- topic and academic field;
- main research question and optional sub-questions;
- target document type and language;
- required structure, chapter count, and word limits;
- date range and source-quality requirements;
- citation style;
- user-provided files and approved knowledge sources;
- local-only, mixed, or organization-approved external execution preference;
- checkpoints requiring user approval.

### 6.2 Directional workflow

```text
1. Requirements normalizer
2. Research-question and search-strategy planner
3. Human approval of scope and search strategy
4. Parallel source discovery through QYBE-approved research tools/connectors
5. Deduplication, screening, metadata normalization, and source-quality checks
6. Evidence matrix and annotated bibliography
7. Paper/chapter outline generation with evidence allocation
8. Human approval of the outline
9. Loop over chapters:
     a. create chapter brief and evidence boundary
     b. retrieve only approved evidence for the chapter
     c. generate structured draft
     d. validate citation coverage and unsupported claims
     e. validate consistency with research questions and other chapters
     f. perform a bounded revision loop
10. Global coherence, terminology, duplication, and reference checks
11. Assemble editable document artifact
12. Final human review and explicit export/publication approval
```

The research stage must produce a reusable evidence corpus before chapter drafting. Chapter agents must not perform unrestricted ad hoc research unless the workflow explicitly returns to the research stage and records the new evidence.

## 7. PraisonAI adapter responsibilities

A `PraisonAIWorkflowRuntimeAdapter` may:

- translate approved QYBE graph nodes into PraisonAI agents, tasks, routes, parallel groups, and loops;
- execute structured step contracts;
- emit normalized start, progress, tool, output, retry, error, and completion events;
- invoke QYBE model and tool brokers rather than selecting providers independently;
- respect QYBE-supplied budgets, cancellation, and approval pauses;
- return typed outputs and runtime diagnostics.

It must not:

- read organization secrets or connector credentials directly;
- select an external model or tool outside the resolved QYBE plans;
- create an independent user or organization memory store;
- persist raw prompts, private content, or unrestricted tool output outside QYBE retention policy;
- publish artifacts or perform material side effects without QYBE approval;
- silently change workflow definitions or increase iteration limits;
- become the source of truth for workflow run state.

## 8. Isolation and deployment boundary

The preferred evaluation deployment is a separate Python worker/service with a pinned PraisonAI dependency set.

```text
QYBE API / background jobs
  -> signed, scoped workflow execution request
  -> PraisonAI adapter worker
  -> QYBE ModelBroker and ToolBroker
  -> normalized event stream
  -> QYBE run and artifact stores
```

Required controls:

- no direct public network exposure;
- short-lived scoped execution credentials;
- outbound network denied by default except through approved QYBE brokers;
- dependency lock, SBOM, vulnerability scan, and version pinning;
- resource, timeout, process, and concurrency limits;
- health checks and automatic worker replacement;
- complete cancellation propagation;
- prompt-safe logs and telemetry;
- adapter feature flag and one-step disable/fallback.

## 9. Main risks and mitigations

1. **Duplicate orchestration authority.** Mitigate with a QYBE-owned workflow schema and one-way compilation into the adapter.
2. **Upstream API churn.** The project is developing rapidly. Pin exact versions, add adapter contract tests, and upgrade only through compatibility branches.
3. **Unbounded agent loops and cost.** Enforce QYBE iteration, token, time, tool-call, and cost budgets outside the runtime.
4. **Policy bypass through YAML or agent configuration.** Do not execute user-supplied PraisonAI YAML directly. Parse a restricted QYBE schema and generate runtime configuration server-side.
5. **Citation and provenance loss.** Require typed evidence references in every research and writing step; validate that claims map to retained source records.
6. **Persistence mismatch.** QYBE remains the run-state authority. Runtime-local state is disposable and reconstructable from QYBE checkpoints.
7. **Local-model limitations.** Benchmark tool calling, structured output, long-context behavior, and evaluator reliability on the actual EdgeXpert model catalog.
8. **Prompt injection across sources.** Treat retrieved documents as untrusted data, isolate instructions from evidence, and validate tool requests through QYBE policy.
9. **Sensitive observability.** Use QYBE prompt-safe events. Disable or strictly configure any upstream tracing that captures raw content.
10. **False confidence from multi-agent complexity.** Compare against simpler single-agent and deterministic pipelines; promote multi-agent patterns only when they improve measurable quality or reliability.

## 10. Adoption phases

### Phase P0 — Source, license, security, and compatibility review

- Pin an exact PraisonAI and `praisonaiagents` version.
- Review workflow, tool, callback, approval, session, persistence, telemetry, and model-provider code paths.
- Produce an SBOM and minimized dependency set.
- Create a threat model for prompt injection, tool abuse, secret exposure, data retention, and runaway execution.
- Verify Python and architecture compatibility with QYBE deployment targets.

**Exit:** approved threat model, dependency policy, and stable adapter surface selected.

### Phase P1 — QYBE workflow contracts and preview

- Implement `WorkflowDefinition`, `WorkflowRun`, step schemas, versioning, and validation.
- Add `WorkflowRuntimeAdapter` protocol without a production runtime dependency.
- Generate `ExecutionGraphPreview` with resolved capabilities, tools, model/runtime requirements, data movement, budgets, and approvals.
- Add a mock/dry-run adapter for UI and contract tests.

**Exit:** a workflow can be defined, validated, previewed, versioned, and audited without execution.

### Phase P2 — Isolated PraisonAI adapter spike

- Create the isolated adapter worker.
- Support only sequential agent steps, typed outputs, QYBE tool/model brokers, events, cancellation, and hard budgets.
- Implement a minimal three-stage academic workflow: research evidence, generate outline, draft one chapter.
- Run in developer/internal evaluation only.

**Exit:** the adapter completes controlled runs without bypassing QYBE model, tool, data-egress, logging, or persistence boundaries.

### Phase P3 — Template-first academic workflow MVP

- Add the Academic Research and Writing template UI.
- Add research strategy and outline approval checkpoints.
- Add evidence matrix, citation-bound chapter drafting, and editable artifact assembly.
- Add run timeline, step status, retry, cancel, and downloadable diagnostics.
- Keep advanced routing and parallelism disabled until the sequential baseline is reliable.

**Exit:** a non-technical user can configure and complete a traceable academic workflow with preserved evidence and explicit approvals.

### Phase P4 — Durable execution and recovery

- Add checkpoints, pause/resume, worker restart recovery, idempotency, and bounded retries.
- Add failure policies at step and workflow level.
- Add per-step model fallback through QYBE's resolver.
- Add organization quotas and concurrency controls.

**Exit:** runs survive process restarts and recover without duplicated tool side effects or lost approvals.

### Phase P5 — Advanced workflow patterns

- Enable conditional routing, parallel research, loops over chapters/items, and bounded evaluator-optimizer cycles.
- Add reusable sub-workflows and domain-pack templates.
- Add verifier roles only where benchmarked benefit exceeds added latency and cost.
- Compare PraisonAI execution against a QYBE-native reference runtime.

**Exit:** advanced patterns pass correctness, provenance, cancellation, budget, and concurrency tests.

### Phase P6 — General user workflow builder

- Add a constrained visual builder with form and graph editing.
- Provide approved node types, templates, validation, simulation, and version diff.
- Add organization sharing, role-based editing, publishing, and template governance.
- Consider a template marketplace only after security and lifecycle governance are mature.

**Exit:** users can safely create reusable workflows without writing framework-specific code or bypassing organization policy.

## 11. Evaluation matrix

| Dimension | Required measure |
|---|---|
| Workflow correctness | completed steps, dependency order, branch/loop correctness, deterministic validation |
| Research quality | relevant source coverage, duplicate rate, source-quality score, evidence matrix completeness |
| Writing quality | research-question coverage, chapter coherence, unsupported claim rate, revision effectiveness |
| Provenance | citation validity, claim-to-source linkage, source retention, artifact traceability |
| Reliability | retry rate, cancellation latency, restart recovery, duplicate side effects, stuck-run rate |
| Policy | model/tool/egress compliance, approval enforcement, secret isolation, tenant isolation |
| Local execution | success with approved Ollama models, structured-output validity, tool-call accuracy |
| Efficiency | total tokens, tool calls, runtime, p50/p95 latency, local compute load, provider cost |
| Operability | dependency upgrades, worker health, diagnostics, rollback, compatibility-test effort |
| User value | workflow completion without code, approval clarity, editability, reuse, time saved |

Minimum pilot gates:

- no direct execution of arbitrary PraisonAI YAML or Python from end users;
- no model, tool, connector, or egress decision outside QYBE policy;
- no raw prompt or private-content telemetry outside approved QYBE stores;
- citations and evidence references survive every workflow transition;
- every loop, retry, and parallel group has explicit hard limits;
- cancel, pause, resume, and worker-failure recovery are testable;
- local execution remains the default when it meets quality requirements;
- QYBE can disable the adapter and retain workflow definitions and run history.

## 12. Decision

**Decision: retain PraisonAI in the QYBE roadmap as a high-priority, isolated workflow runtime adapter candidate and reference implementation.**

The first product deliverable is not a generic autonomous-agent platform. It is a QYBE-governed Academic Research and Writing workflow that demonstrates reusable user configuration, evidence-first research, outline approval, bounded chapter generation, citation validation, durable execution, and editable artifact output.

QYBE must first own the declarative workflow model, execution preview, policy enrichment, brokers, run state, provenance, and user experience. PraisonAI may accelerate execution semantics behind that boundary, but it must remain replaceable and disabled by default until the staged gates pass.
