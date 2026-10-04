# Paperclip Agent Control Plane Evaluation Plan

**Status:** Directional architecture, reference implementation study, and staged evaluation only  
**Updated:** 2026-10-04  
**Base branch:** `dev`  
**Reference repository:** https://github.com/paperclipai/paperclip  
**License:** MIT for the main code repository  
**Decision:** High-value reference implementation for a future QYBE agent control plane. No Paperclip runtime, package, schema, service, dependency, or application code is approved for integration by this plan.

## 1. Executive assessment

Paperclip is highly relevant to QYBE because it addresses a layer that QYBE will need as complex tasks move from advisory routing toward governed execution: a control plane for tasks, agent runs, workspaces, approvals, budgets, tools, secrets, artifacts, and execution lifecycle.

The recommended use is selective architectural adoption and later code-level evaluation, not wholesale embedding and not replacement of QYBE's router, Onyx-derived platform foundation, knowledge stack, policy layer, or end-user experience.

| Dimension | Assessment |
|---|---|
| Strategic fit with QYBE | **9/10** — strongly aligned with governed agent execution |
| Agent lifecycle and task control | **10/10** — especially relevant to long-running Work-style tasks |
| Runtime adapter model | **10/10** — useful for Claude Code, Codex, local runtimes, and future agents |
| Workspace/artifact model | **9/10** — directly relevant to QYBE Work |
| Tool/MCP governance | **10/10** — valuable reference for permissions and approvals |
| Secrets and scoped credentials | **10/10** — important for enterprise execution |
| Budget and cost governance | **9/10** — complements QYBE model/runtime routing |
| Skills architecture | **9/10** — useful for evolving domain packs |
| Memory/RAG replacement value | **Low** — QYBE should retain its own knowledge architecture |
| Fit as wholesale core dependency | **Low-medium** — too much overlap and authority duplication |
| Recommended priority | **High as a design reference; implementation only after QYBE contracts are stable** |

## 2. Architectural role in QYBE

Paperclip should be treated as a reference implementation for a future **QYBE Agent Control Plane** positioned below QYBE's decision layers and above interchangeable execution runtimes.

```text
User / QYBE UI
  -> QYBE Intelligent Router
  -> CapabilityPlan / WorkflowPlan
  -> DataClassification / DataEgressDecision
  -> ToolPlan / ModelPlan / RuntimePlan
  -> ExecutionGraphPreview
  -> QYBE Agent Control Plane
       -> Task graph and execution locks
       -> Agent lifecycle
       -> Workspace lifecycle
       -> Plan/checkpoint/approval state
       -> Tool permission gateway
       -> Secret broker
       -> Cost/budget enforcement
       -> Artifact and run event management
       -> Runtime Adapter API
            -> QYBE native worker
            -> local EdgeXpert runtime
            -> Claude Code
            -> Codex
            -> Kimi / Gemini / other approved runtimes
            -> future sandbox/cloud providers
  -> QYBE Memory / Knowledge / RAG
```

The control plane executes decisions. It must not become the authority that decides privacy policy, business intent, model policy, data egress, or organization-level governance.

## 3. What QYBE should learn from Paperclip

### 3.1 Runtime adapter boundary

QYBE should define a provider-neutral agent runtime contract so task execution is independent of a specific coding agent, framework, model provider, or deployment target.

Directional interface:

```text
AgentRuntimeAdapter
  start(run_spec)
  resume(run_id, checkpoint)
  cancel(run_id)
  status(run_id)
  collect_usage(run_id)
  collect_artifacts(run_id)
  collect_events(run_id)
```

The adapter receives an already-approved run specification. It must not independently choose models, tools, secrets, or external providers.

### 3.2 Task ownership and atomic execution locks

QYBE needs explicit run ownership for durable multi-agent execution.

Directional concepts:

- one canonical task/run owner at a time;
- atomic checkout before execution;
- execution lease with expiry/renewal;
- idempotency key for retries;
- explicit blocked/waiting/approval states;
- orphaned-run recovery;
- parent/child task relationships;
- cancellation propagation.

This prevents duplicate agents from modifying the same workspace or performing the same side effect concurrently.

### 3.3 Event/heartbeat execution model

Long-running agents should not require permanent autonomous loops.

A future QYBE event-driven lifecycle may be:

```text
Task event / schedule / approval / user continuation
  -> wake eligible worker
  -> restore run context and workspace
  -> acquire execution lease
  -> resolve allowed skills/tools/secrets
  -> execute bounded step
  -> checkpoint state
  -> store artifacts/events/usage
  -> release or renew lease
  -> sleep / wait / complete
```

This is particularly appropriate for local-first operation on EdgeXpert because heavy local runtimes can remain serialized or resource-governed instead of being kept active for every logical agent.

### 3.4 Workspaces and artifacts

The Paperclip workspace model reinforces the planned QYBE Work direction.

A QYBE task workspace should remain a QYBE-owned abstraction and may eventually contain:

```text
workspace/
  input/
  sources/
  files/
  generated/
  browser/
  app_sessions/
  scratch/
  logs/
  artifacts/
  checkpoints/
  run_state.json
```

Workspace policy should define:

- ownership and ACL;
- retention and deletion;
- local vs remote storage;
- isolation level;
- mounted tools/apps;
- allowed network scope;
- artifact promotion rules;
- snapshot/restore semantics.

### 3.5 Tool/MCP permission gateway

Paperclip's permission concepts are relevant to QYBE's existing ToolPlan direction.

QYBE should eventually support policy such as:

```text
browser.search        allowed
files.read            allowed
github.read           allowed
github.commit         ask/approve
email.read            allowed
email.send            ask/approve
production.deploy     ask/approve
finance.refund        ask/approve
```

The QYBE-owned permission gateway should combine:

- organization policy;
- user role;
- project policy;
- data classification;
- tool risk;
- side-effect severity;
- argument-level constraints;
- runtime identity;
- approval state.

### 3.6 Scoped secrets

QYBE should avoid giving a runtime broad organization credentials.

Directional model:

```text
Organization secrets
  -> project-allowed subset
  -> task/run-allowed subset
  -> short-lived delivery to runtime
```

The control plane should issue only the credentials required for a run and record access in prompt-safe audit events.

### 3.7 Budgets and cost controls

Paperclip's budget model should inform, not replace, QYBE routing.

QYBE may eventually enforce:

- run monetary budget;
- token budget;
- wall-clock budget;
- tool-call budget;
- iteration budget;
- local GPU time budget;
- external-provider spend cap;
- concurrency limit.

The QYBE router can use the budget while selecting local vs external execution, but the control plane must enforce the resulting hard limits.

### 3.8 Skills and domain packs

Paperclip's skill model is relevant to the evolution of QYBE domain packs.

Directional QYBE structure:

```text
Domain Pack
  -> versioned skills
       -> instructions
       -> required capabilities
       -> allowed tools
       -> evaluation criteria
       -> test cases
       -> provenance
       -> version / rollback
```

Domain packs remain declarative recommendations and constraints. A skill cannot bypass organization policy or tool authorization.

### 3.9 Planning, revision, and approval

For complex tasks, QYBE should separate planning from execution.

Directional lifecycle:

```text
User task
  -> plan v1
  -> execution preview
  -> optional approval
  -> bounded execution
  -> checkpoint / evidence
  -> plan revision v2 if required
  -> approval when policy requires
  -> continue
```

Plan revisions must be versioned and explain why the previous plan changed.

### 3.10 Sandbox/execution provider abstraction

Paperclip's sandbox/provider approach is relevant to QYBE's deployment path from EdgeXpert to VPS/cloud.

QYBE should keep execution target provider-neutral:

```text
ExecutionTarget
  local_process
  local_container
  desktop_session
  remote_worker
  sandbox
  kubernetes
  cloud_worker
```

The same approved run contract should be portable across targets without changing the orchestration authority.

## 4. What QYBE must not copy directly

### 4.1 Do not expose an "AI company org chart" as QYBE's core UX

Paperclip's organization metaphor can be useful internally, but QYBE's end-user abstraction should remain task-centric.

Users should primarily express goals such as:

```text
"Prepare a market-entry report and an editable financial model."
```

QYBE may internally create temporary research, data, writing, verification, or coding roles, but those are implementation details unless the user explicitly wants to inspect them.

### 4.2 Do not replace the QYBE router

Paperclip-style execution management must sit below:

- intent/domain classification;
- capability planning;
- organization policy;
- data classification;
- data-egress decisions;
- model resolution;
- runtime resolution;
- tool planning.

The QYBE Router remains the decision layer.

### 4.3 Do not replace QYBE/Onyx knowledge and RAG

Paperclip is not the canonical knowledge subsystem for QYBE.

QYBE should continue to use its own Onyx-derived retrieval/connectors foundation and separately evaluated memory/knowledge components such as OpenViking where justified.

### 4.4 Do not introduce duplicate task, auth, persistence, or policy authorities

A wholesale Paperclip service embedded beside QYBE could create:

- duplicate task/run stores;
- duplicate identities and tenancy;
- duplicate permission systems;
- duplicate secrets handling;
- competing audit trails;
- competing model/tool policies.

Any future reuse must occur behind QYBE-owned contracts.

## 5. Proposed QYBE Agent Control Plane components

The future logical layer should be decomposed into replaceable components:

```text
QYBE Agent Control Plane
  TaskGraphManager
  ExecutionLeaseManager
  AgentLifecycleManager
  RuntimeAdapterRegistry
  WorkspaceManager
  ArtifactManager
  PlanRevisionManager
  ApprovalManager
  SkillRegistry
  ToolPolicyGateway
  SecretBroker
  BudgetController
  RunEventStore
  PromptSafeAudit
  SandboxProviderRegistry
```

These are target abstractions only. This document does not authorize implementation.

## 6. Relationship to existing QYBE architecture tracks

### 6.1 PraisonAI

PraisonAI remains a candidate **workflow execution runtime adapter**.

Paperclip contributes ideas for the **control plane around runtimes**.

The responsibilities are complementary:

```text
QYBE Router and Policy
  -> QYBE Agent Control Plane
       -> WorkflowRuntimeAdapter
            -> QYBE native
            -> PraisonAI
            -> future engines
       -> AgentRuntimeAdapter
            -> Claude Code
            -> Codex
            -> local worker
            -> future runtimes
```

### 6.2 OpenViking / knowledge memory

OpenViking or another approved knowledge/memory component belongs to the knowledge context layer, not the execution control plane.

### 6.3 DeepSeek Harness and agent harnesses

Harness technologies may improve how an individual agent reasons and executes. The control plane remains responsible for lifecycle, permissions, workspace, budget, state, and audit.

### 6.4 Headroom

Headroom remains a context-optimization candidate below policy and classification. It does not replace the control plane.

### 6.5 QYBE Work

QYBE Work is the primary product surface that benefits from this track:

- durable task workspace;
- long-running execution;
- files and artifacts;
- desktop/browser/app sessions;
- checkpoints;
- user approvals;
- progress/status;
- resumption after interruption.

## 7. Adoption phases

### Phase PC0 — Documentation-only retention

- Keep this plan as a design reference.
- Do not add Paperclip dependencies.
- Do not add Paperclip services or containers.
- Do not port database schema.
- Do not alter the current QYBE execution path.
- Track upstream architecture changes only when they affect a QYBE design decision.

**Exit:** QYBE's own control-plane contracts are sufficiently defined to compare implementation options.

### Phase PC1 — Code-level mapping study

After QYBE's own abstractions exist on paper, inspect Paperclip source in detail and classify relevant modules:

```text
USE AS-IS
PORT
REIMPLEMENT
REFERENCE ONLY
IGNORE
```

Map each candidate to QYBE-owned interfaces.

Required outputs:

- source/module map;
- dependency map;
- data model comparison;
- security boundary comparison;
- migration/porting cost;
- testability assessment;
- licensing notice requirements.

**Exit:** no ambiguity about which code could be reused without importing Paperclip as a second application control plane.

### Phase PC2 — QYBE contract design

Define, without Paperclip runtime dependency:

- `AgentRuntimeAdapter`;
- `ExecutionLease`;
- `TaskRun`;
- `WorkspaceSpec`;
- `ArtifactRef`;
- `RunBudget`;
- `ApprovalRequest`;
- `ScopedSecretGrant`;
- `SkillRef`;
- normalized run events.

Run architecture review before implementation.

**Exit:** contracts are provider-neutral and compatible with local, desktop, sandbox, and cloud execution.

### Phase PC3 — Shadow control-plane prototype

Implement only QYBE-native shadow state:

- proposed task graph;
- proposed workspace allocation;
- proposed runtime;
- proposed budgets;
- proposed permissions;
- proposed agent roles;
- proposed execution leases.

Do not execute tools or agents based on these records.

**Exit:** shadow output is stable and explainable on representative QYBE tasks.

### Phase PC4 — Single-run bounded execution pilot

Enable one controlled worker path behind feature flags.

Initial constraints:

- one workspace;
- one active execution lease;
- one agent runtime;
- read-only tools first;
- strict timeout and budget;
- no unrestricted credentials;
- full cancellation;
- prompt-safe events;
- manual approval for side effects.

**Exit:** durable start/resume/cancel/retry behavior passes failure-injection tests.

### Phase PC5 — Multi-agent/task graph pilot

Only after PC4 is stable:

- bounded child tasks;
- parallelism only where resources permit;
- explicit parent/child state;
- atomic assignment;
- dependency tracking;
- verifier roles;
- workspace conflict controls.

On EdgeXpert, local-model concurrency remains constrained by runtime policy even if logical tasks are parallel.

**Exit:** no duplicate side effects, workspace corruption, orphan execution, or policy bypass under fault testing.

### Phase PC6 — Portable execution providers

Add provider-neutral targets for:

- EdgeXpert/local containers;
- desktop/local application execution;
- remote workers;
- sandbox providers;
- Kubernetes/cloud workers.

The control plane contract must remain the same.

**Exit:** the same test workflow can move between approved targets without changing canonical task semantics.

## 8. Security and governance requirements

Any future implementation must satisfy all of the following:

1. Organization policy remains authoritative.
2. Raw prompts/private documents are not emitted to telemetry.
3. Runtime workers do not receive broad permanent credentials.
4. Side-effecting tools require explicit policy authorization or approval.
5. All external egress is classified and approved before use.
6. Every run has hard resource and budget limits.
7. Every workspace has an owner, retention policy, and isolation policy.
8. Execution leases are recoverable and expire safely.
9. Cancellation propagates to child tasks and runtime processes.
10. Retry is idempotent or explicitly guarded.
11. Artifacts preserve provenance.
12. Runtime adapters cannot silently select alternate providers.
13. Audit events identify decisions without storing prohibited content.
14. Feature flags provide one-step disable/fallback.
15. Paperclip upstream changes never automatically alter QYBE behavior.

## 9. Evaluation criteria for future code reuse

Before any Paperclip code is reused, evaluate:

| Area | Required check |
|---|---|
| License | exact file/repository license and notice obligations |
| Dependencies | minimized dependency graph and SBOM |
| Security | secrets, auth, tool, network, filesystem, and process boundaries |
| Data model | compatibility with QYBE canonical IDs, tenancy, and run state |
| Runtime | ARM64/Linux compatibility for EdgeXpert where relevant |
| Persistence | no competing source of truth |
| Observability | prompt-safe and compatible with QYBE telemetry |
| Failure semantics | cancel, retry, timeout, crash recovery, idempotency |
| Tests | adapter contract and failure-injection coverage |
| Upgrades | pinned versions and isolated compatibility surface |
| UX | QYBE task-centric experience remains authoritative |

## 10. Explicit non-goals

This roadmap entry does **not** authorize:

- cloning Paperclip into the QYBE source tree;
- adding Paperclip packages to Python/Node dependency files;
- adding Paperclip containers to deployment;
- migrating or duplicating Paperclip schemas;
- changing QYBE router behavior;
- changing current agents or workflows;
- changing MCP/tool permissions;
- enabling autonomous multi-agent execution;
- modifying the current QYBE UI;
- replacing Onyx-derived task, connector, RAG, auth, or persistence functionality.

## 11. Decision

**Retain Paperclip as a high-priority architectural reference for the future QYBE Agent Control Plane.**

The preferred strategy is:

```text
study architecture
  -> define QYBE-owned contracts
  -> code-level map Paperclip modules
  -> selectively port/reimplement only justified pieces
  -> shadow first
  -> bounded pilot
  -> multi-agent and portable execution only after measurable gates
```

Paperclip must remain replaceable and subordinate to QYBE's router, policy, knowledge, model/runtime resolution, tool governance, and user experience.

No current application code should change as a consequence of this plan.
