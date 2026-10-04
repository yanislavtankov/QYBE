# OpenDots Persistent Agent Workspace Integration Plan

**Status:** Directional architecture, reference implementation review, and staged adoption plan  
**Updated:** 2026-10-04  
**Base branch:** `dev`  
**Evaluated repository:** [CopilotKit/OpenDots](https://github.com/CopilotKit/OpenDots)  
**Decision:** High-value reference architecture and selective component source; not approved as QYBE's orchestration, identity, memory, or policy authority.

## 1. Executive assessment

OpenDots is unusually relevant to QYBE because it implements a product pattern that closely matches the planned QYBE Work experience: persistent specialist agents, durable workspaces, editable documents, background work, human approvals, live computer control, per-agent persistent browser/files/shell, chat/voice/channel surfaces, and learning/skill delivery.

It is not primarily a multi-agent orchestration framework. It is a self-hostable application template that demonstrates how a persistent AI coworker can be represented in the UI and connected to a governed execution environment.

As evaluated on 2026-10-04, the repository is very new and explicitly marked alpha. It was created on 2026-09-29, uses the MIT license, and has attracted rapid interest. Upstream documentation also states important current limits: single-owner starting point, no automatic multi-Dot delegation, no multi-Dot group conversations, no complete event-trigger/responsibility system, and additional multi-user security work required.

| Dimension | Assessment |
|---|---|
| Product/UX fit with QYBE Work | **10/10** |
| Persistent agent-computer pattern | **9/10** |
| Human-in-the-loop and permission pattern | **9/10** |
| Fit as QYBE core orchestrator | **4/10** |
| Fit as reference implementation / selective donor | **9/10** |
| Fit for local Windows/macOS application control | **5/10** — useful security pattern, but its containers intentionally do not control the host desktop |
| Production maturity today | **Low-medium** — alpha and only days old at evaluation time |
| Recommended priority | **High architecture study; medium implementation priority after QYBE workflow/run contracts stabilize** |

**Recommendation:** do not fork OpenDots into QYBE or replace the Onyx/QYBE application foundation. Extract and adapt the strongest architectural patterns behind QYBE-owned interfaces.

## 2. Capabilities worth reusing conceptually

### 2.1 Persistent specialist identity

OpenDots models a persistent specialist ("Dot") with a name, role instructions, allowed workspaces, research/memory permissions, computer permissions, and optional learning configuration.

QYBE should adapt this into a provider-neutral `WorkerProfile` / `AgentProfile` that can be:
- created dynamically for one task;
- retained as a reusable specialist when useful;
- bound to domain packs, skills, tools, models and runtime requirements;
- governed by organization policy rather than by the agent definition itself.

A QYBE agent profile must describe requested capabilities, not bypass the router, model resolver, runtime resolver, or tool policy.

### 2.2 Spaces and persistent task workspaces

OpenDots Spaces combine documents, page hierarchy, saved conversations, specialist access, and editable artifacts.

This maps directly to the planned QYBE Work concept. QYBE should define a first-class `TaskWorkspace` / `ProjectSpace` containing:
- task brief and normalized requirements;
- files, generated artifacts and intermediate outputs;
- evidence and source references;
- workflow/run state;
- agent assignments;
- approvals and checkpoints;
- user/project preferences;
- logs and prompt-safe execution events;
- provenance and artifact versions.

The workspace must not be coupled to one editor. Univer, document generation, code work, CAD/DFX integration, browser output and future artifact editors should all bind to the same QYBE workspace abstraction.

### 2.3 Per-agent persistent computer

OpenDots uses OpenBot-derived services to give each Dot a separate persistent computer container with:
- a browser profile;
- persistent workspace files;
- optional shell;
- live snapshot/control;
- user takeover and handback;
- per-capability permissions;
- action records;
- separate credentials per agent.

This is one of the strongest patterns for QYBE.

QYBE should define an `AgentComputerProvider` contract with at least:
- lifecycle: create/start/stop/status;
- browser: snapshot, navigate, inspect, click, type, upload/download under policy;
- workspace files: list/read/write with scoped paths;
- shell/code execution: bounded commands inside the execution environment;
- human takeover;
- permission revocation and cancellation;
- action/audit event stream;
- persistent profile and workspace volumes when policy allows.

Providers may include:
1. isolated Docker computer on EdgeXpert/VPS/AWS;
2. hardened browser-only sandbox;
3. QYBE Desktop bridge for explicitly authorized local Windows/macOS applications;
4. future cloud-computer providers.

### 2.4 Human-in-the-loop approval cards

OpenDots demonstrates an important interaction pattern: tool execution can pause and render a structured approval card in the conversation before a state-changing operation continues.

QYBE should standardize this as `ApprovalGate` events in the execution graph:
- reason for approval;
- proposed action and affected resources;
- data leaving the organization, if any;
- side-effect level;
- resolved model/tool/runtime where relevant;
- approve / decline / edit / take control;
- immutable audit record.

The same approval mechanism should work for document publication, connector writes, email/send actions, purchases, deployment, local desktop actions, and high-risk tool calls.

### 2.5 AG-UI-style execution event stream

OpenDots uses AG-UI to stream messages, tool calls, state and computer activity between runtime and UI.

QYBE should evaluate AG-UI as a protocol/reference for a provider-neutral `ExecutionEvent` stream, but should not make CopilotKit Runtime a mandatory control plane.

The QYBE event contract should cover:
- message/token streaming;
- run/step lifecycle;
- tool request/result;
- computer snapshot/activity;
- approval requested/resolved;
- artifact created/updated;
- progress/status;
- model/runtime/tool resolution;
- pause/resume/cancel/retry;
- error and recovery;
- provenance/evidence references.

If AG-UI satisfies the requirements, QYBE may expose an AG-UI adapter while retaining a canonical internal event model.

### 2.6 Background work and durable conversations

OpenDots includes server-side recurring/background turns associated with their original conversations. This validates the user experience but is not yet a complete durable business-process engine.

QYBE should keep `WorkflowRun` / `TaskRun` as the source of truth and add:
- durable checkpoints;
- leases and worker ownership;
- idempotency;
- pause/resume/cancel;
- retries and backoff;
- deadlines and budgets;
- event/condition triggers;
- recovery after process/node restart;
- long-running tasks measured in minutes, hours or days rather than a short interactive-agent timeout.

OpenDots' lightweight runner is useful as a reference, not as the required QYBE scheduler.

### 2.7 Multi-surface continuity

OpenDots demonstrates continuity across web chat, Slack and realtime voice while retaining conversation context and tool permissions.

QYBE should define `InteractionSurfaceAdapter` interfaces so the same governed task/workspace can be reached through:
- QYBE web;
- QYBE mobile;
- QYBE Desktop;
- email;
- Slack / Microsoft Teams;
- voice;
- future messaging systems.

Identity mapping and authorization must remain QYBE-owned.

### 2.8 Learning and skill delivery

OpenDots' CopilotKit Automatic Learning integration routes selected conversations into learning containers and later delivers reviewed/published skills back to agents.

This is relevant to QYBE's knowledge-to-skill and preference-learning tracks, but QYBE must own the lifecycle:
- collect only policy-approved evidence;
- derive candidate preferences/rules/skills;
- separate user/project/organization scope;
- review and validate before promotion;
- version, evaluate and roll back;
- retain provenance;
- never allow learned content to override system or organization policy.

CopilotKit Intelligence Learning may be evaluated as an optional adapter, not the canonical QYBE memory/skill store.

## 3. What QYBE should not adopt wholesale

### 3.1 Do not replace the Onyx/QYBE foundation

OpenDots is a compact template. QYBE already inherits mature RAG, connectors, administration, access control, search, document ingestion, deployment and enterprise application foundations from Onyx. Replacing that base would destroy more value than it adds.

### 3.2 Do not create a second orchestration authority

OpenDots' Dot agent currently assembles tools, an OpenAI-compatible model adapter and runtime behavior inside its own server path. In QYBE these decisions belong to:
`CapabilityPlan -> DataEgressDecision -> ToolPlan -> ModelPlan -> RuntimePlan -> ExecutionGraph`.

An OpenDots-inspired worker may consume resolved QYBE decisions; it must not select unrestricted providers or tools independently.

### 3.3 Do not make CopilotKit Intelligence the QYBE source of truth

OpenDots separates local SQLite application metadata from CopilotKit Intelligence Threads and Learning.

QYBE requires provider-neutral persistence for:
- identity and tenancy;
- workflow/task state;
- project memory and preferences;
- provenance;
- artifacts;
- audit;
- long-running responsibility state.

CopilotKit services can be optional adapters where justified, but QYBE must remain operable without them.

### 3.4 Do not reuse the single-owner security model

OpenDots explicitly describes itself as a single-owner starting point and requires additional enforcement for multi-user Space membership, Slack identity mapping and voice delegation.

QYBE must start from organization/tenant/RBAC boundaries inherited from Onyx and apply authorization server-side to every workspace, run, artifact, computer, connector and channel action.

### 3.5 Do not confuse container computers with local desktop control

OpenDots intentionally prevents agent computer tools from falling back to host shell/files. This is correct for isolation but does not satisfy QYBE's requirement to work with explicitly authorized locally installed applications such as Word, Excel, FreeCAD or other CAD/DFX tools.

QYBE therefore needs two distinct execution classes:

```text
A. Isolated Agent Computer
   Docker / sandbox / cloud computer
   -> browser, files, shell, code, safe automation

B. Trusted QYBE Desktop Bridge
   Windows/macOS installed application
   -> explicit per-application/user permissions
   -> visible actions / takeover
   -> OS-native automation adapters
   -> strict local audit and revocation
```

The two classes must share the same QYBE `ToolPlan`, `ApprovalGate` and event model but have different trust policies.

## 4. Target QYBE architecture

```text
User / Channel / Voice / Desktop
  -> QYBE Interaction Surface
  -> Task Intent + Workspace Resolver
  -> Shadow/Live RouteDecision
  -> WorkflowDefinition / CapabilityPlan
  -> DataClassification + DataEgressDecision
  -> ToolPlan + ModelPlan + RuntimePlan
  -> ExecutionGraphPreview
  -> ApprovalGate where required
  -> QYBE WorkflowRun / TaskRun
       -> WorkerProfile(s)
       -> AgentComputerProvider
            -> isolated Docker computer
            -> browser-only sandbox
            -> cloud computer
       -> DesktopBridgeProvider
            -> Windows/macOS local applications
       -> WorkflowRuntimeAdapter
            -> QYBE native
            -> PraisonAI
            -> future runtimes
       -> Artifact / Evidence / Provenance stores
  -> ExecutionEvent stream
  -> Web / Mobile / Desktop / Slack / Teams / Voice UI
```

OpenDots is a reference for the UX and execution boundary inside this architecture, not a layer above the QYBE control plane.

## 5. Proposed QYBE contracts

### 5.1 `TaskWorkspace`

Minimum fields:
- workspace ID, owner, organization, project/domain;
- task brief and normalized intent;
- authorized users/groups;
- attached sources and files;
- artifact index and version metadata;
- active/completed runs;
- worker assignments;
- memory/preference scope;
- evidence/provenance index;
- approval state;
- retention and data-classification policy.

### 5.2 `WorkerProfile`

Minimum fields:
- role and instructions;
- required capabilities;
- allowed workspace scopes;
- requested tools;
- memory scope;
- model/runtime requirements;
- computer requirements;
- maximum autonomy/side-effect class;
- lifecycle: ephemeral, task-persistent, project-persistent.

### 5.3 `AgentComputerProvider`

Minimum operations:
- ensure/start/stop/status;
- snapshot and human takeover;
- browser actions;
- scoped file actions;
- bounded shell/code actions;
- activity stream;
- revoke/cancel;
- persistent volume policy;
- destroy/retention handling.

### 5.4 `ExecutionEvent`

Normalize events independent of UI framework:
- `run.started`, `run.progress`, `run.completed`, `run.failed`;
- `step.*`;
- `tool.requested`, `tool.completed`, `tool.failed`;
- `approval.requested`, `approval.resolved`;
- `computer.snapshot`, `computer.activity`, `computer.takeover`;
- `artifact.created`, `artifact.updated`;
- `evidence.added`;
- `model.resolved`, `runtime.resolved`;
- `run.paused`, `run.resumed`, `run.cancelled`.

## 6. Security and deployment requirements

1. Agent computers must not inherit host filesystem, Docker socket, host credentials or unrestricted private-network access.
2. Separate credentials must be derived/scoped per computer or worker.
3. Browser profiles and workspace volumes must be isolated between tenants and workers.
4. Shell access is disabled by default and enabled only by explicit capability policy.
5. Human takeover must suspend conflicting agent browser input until handback.
6. Revocation must cancel active requests where possible and block subsequent requests.
7. Completed side effects are not assumed reversible; higher-risk actions require pre-execution approval.
8. Computer activity logs should record action metadata without indiscriminately storing typed secrets, file contents or full commands.
9. Prompt injection from pages/files/messages must not modify authorization, tool policy or system instructions.
10. Remote deployment requires authentication, TLS, tenant-aware authorization, secrets management, network policy and auditable service identity.
11. For stronger sandboxing, evaluate gVisor/Kata/microVM providers separately; ordinary Docker isolation is not a universal security boundary.
12. Desktop Bridge actions require a stricter trust model because they can affect the user's real machine and local applications.

## 7. Adoption phases

### Phase O0 — Source and architecture review

- Pin the evaluated OpenDots commit/release.
- Review OpenDots, OpenBot computer services, AG-UI integration, approval flow, persistence boundaries, scheduler, channel mapping and learning path.
- Create a mapping from OpenDots concepts to QYBE-owned contracts.
- Produce a focused threat model.

**Exit:** no QYBE authority is delegated accidentally to CopilotKit/OpenDots-specific state.

### Phase O1 — QYBE Work contract layer

Implement or formalize:
- `TaskWorkspace`;
- `WorkerProfile`;
- `ExecutionEvent`;
- `ApprovalGate`;
- `AgentComputerProvider`;
- interaction-surface identity mapping.

Use mock providers first.

**Exit:** UI and workflow layers can operate against provider-neutral contracts.

### Phase O2 — Isolated computer PoC on EdgeXpert

- Reproduce the per-agent persistent computer pattern on EdgeXpert.
- Compare OpenBot-derived implementation with a minimal QYBE-native Playwright/container worker.
- Validate two-agent isolation, persistent browser sessions, scoped workspace files, shell permission, takeover/handback, revocation and restart recovery.
- Add prompt-safe audit events.

**Exit:** isolation and persistence tests pass and no host fallback exists.

### Phase O3 — QYBE Work UX pilot

Implement a narrow workflow:
1. user creates a business task;
2. QYBE creates a workspace;
3. router/planner assigns one specialist;
4. specialist researches/browses in an isolated computer;
5. generates an editable artifact;
6. requests approval before a material save/export/action;
7. user can inspect progress and take over the browser.

Use an existing QYBE document artifact path rather than OpenDots page storage.

**Exit:** end-to-end task survives UI refresh/restart and retains evidence, run state and artifact history.

### Phase O4 — Durable background work and multiple workers

- Connect `TaskWorkspace` to QYBE `WorkflowRun`.
- Add durable queue/checkpoint semantics, bounded parallel workers and verifier roles.
- Support agent creation from workflow/capability requirements.
- Keep automatic delegation behind feature flags until traceable and testable.

**Exit:** restart-safe multi-step run with deterministic budgets, approvals and cancellation.

### Phase O5 — Desktop and channel expansion

- Add QYBE Desktop Bridge for explicitly authorized local applications.
- Add Slack/Teams/email/voice adapters through QYBE identity/policy.
- Evaluate AG-UI compatibility adapter if it improves interoperability.
- Evaluate optional CopilotKit Learning/Channels only where they do not create a required control-plane dependency.

**Exit:** same task/workspace can continue across approved surfaces without weakening identity, policy or provenance.

## 8. Evaluation matrix

| Dimension | Required evaluation |
|---|---|
| Task durability | restart/reconnect survival, idempotency, checkpoint recovery |
| Isolation | cross-agent/tenant file, browser profile, secret and network separation |
| Governance | permission revocation, approval enforcement, policy precedence |
| Tool safety | bounded shell/browser/file operations and side-effect classification |
| UX | progress visibility, computer view, takeover, approval clarity |
| Model neutrality | local Ollama/SGLang and external OpenAI-compatible providers through QYBE resolver |
| Runtime neutrality | native and workflow-adapter workers consume same contracts |
| Provenance | source -> step -> artifact traceability |
| Cost/latency | persistent-computer overhead, cold start, resource usage |
| Scalability | EdgeXpert single-node -> VPS -> AWS/Kubernetes/microVM provider path |
| Desktop safety | explicit app permissions, visible control, cancellation, local audit |
| Dependency risk | ability to remove CopilotKit/OpenDots without rewriting QYBE core state |

## 9. Decision

**Adopt the OpenDots architecture selectively.**

Approved direction:
- use it as a primary reference for QYBE Work UX;
- adopt the conceptual pattern of persistent specialists and task workspaces;
- implement a QYBE-owned per-agent computer abstraction;
- standardize structured approval and live execution events;
- evaluate AG-UI compatibility;
- study OpenBot's supervisor/computer isolation and credential design;
- study Automatic Learning as an optional adapter/reference for QYBE skill learning.

Not approved:
- replacing Onyx/QYBE with OpenDots;
- making CopilotKit Intelligence mandatory;
- making TanStack AI/OpenDots model execution the QYBE router;
- using OpenDots SQLite/Threads as QYBE's canonical persistence;
- importing its single-owner authorization model;
- treating its current scheduler as a production long-running workflow engine;
- allowing isolated computers to become an implicit bridge to host resources.

## 10. Strategic significance

OpenDots provides strong external validation for the QYBE product direction: an AI system becomes substantially more useful when a conversation is attached to a persistent work area, a durable specialist identity, a real execution computer, visible progress, editable artifacts and explicit human control.

The main QYBE opportunity is to combine that interaction model with capabilities OpenDots does not currently provide as its core purpose: enterprise RAG/connectors, policy-aware local-first model routing, domain packs, durable workflow orchestration, data classification/egress governance, provenance, multi-tenant administration, and a controlled local desktop bridge.

That combination should remain a QYBE-native architecture, with OpenDots/OpenBot/CopilotKit treated as replaceable reference implementations or optional adapters.
