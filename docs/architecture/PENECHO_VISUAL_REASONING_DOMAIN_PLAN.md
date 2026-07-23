# PenEcho Visual Reasoning Integration Plan for QYBE Domains

**Status:** Directional architecture and evaluation plan  
**Updated:** 2026-07-23  
**Base branch:** `dev`  
**Implementation state:** Documentation only; no QYBE or PenEcho runtime integration is enabled by this plan.

## 1. Purpose

QYBE should support an optional visual reasoning workspace for domains in which spatial relationships are part of the problem, especially engineering and academic work. The workspace should let a user combine handwriting, equations, diagrams, annotations, and referenced evidence without translating every intermediate step into a linear chat message.

[PenEcho](https://github.com/penecho/penecho) is a relevant reference implementation and possible replaceable integration candidate. It uses a large sparse canvas, sends a bounded visual atlas and geometry to a model executor, receives structured drawing or text commands, and keeps AI output in an editable draft layer until the user accepts or rejects it.

The objective is not to replace QYBE chat, RAG, documents, or orchestration. The objective is to add a domain-selectable reasoning surface that remains governed by QYBE.

## 2. Architectural decision

**Decision: model visual reasoning as a provider-neutral QYBE capability, with PenEcho treated first as a reference protocol and optional external adapter—not as a mandatory QYBE dependency.**

QYBE must retain authority over:

- organization and user authentication;
- domain and task classification;
- data classification and data-egress decisions;
- RAG retrieval, source permissions, citations, and provenance;
- model and runtime resolution;
- tool authorization and side-effect policy;
- storage, retention, audit, and telemetry policy;
- final artifact publication or external action.

The visual workspace owns only the bounded interaction surface: ink, typed equations, spatial layout, local canvas editing, and presentation of unconfirmed AI drafts.

## 3. Domain-pack capability model

Engineering and academic domain packs may recommend the following optional capabilities:

| Capability | Purpose |
|---|---|
| `visual_reasoning_canvas` | Shared spatial workspace for mixed ink, text, equations, and diagrams |
| `handwriting_input` | Pen, touch, or mouse input with pressure-aware strokes where supported |
| `equation_reasoning` | Recognition, derivation, typesetting, and validation of mathematical expressions |
| `diagram_reasoning` | Interpretation and generation of bounded structured diagrams |
| `spatial_context` | Preserve relative position, grouping, arrows, regions, and annotations as model input |
| `visual_draft_review` | Keep model output unconfirmed until explicit accept, reject, or edit |
| `canvas_evidence_binding` | Bind a canvas object or region to QYBE sources, citations, files, or retrieved facts |
| `visual_artifact_export` | Export an approved workspace into QYBE documents or other governed artifacts |

These capabilities are recommendations emitted by the domain pack and represented in `CapabilityPlan`. They must not bypass privacy, licensing, model, tool, or data-egress policy.

## 4. Initial domain profiles

### 4.1 Engineering domain

The engineering profile should prioritize:

- control-system block diagrams and signal-flow reasoning;
- electrical and electronic circuits;
- network and infrastructure diagrams;
- mechanical sketches, dimensions, and free-body diagrams;
- process-flow, P&ID-like, and manufacturing layouts;
- equations linked to diagram elements;
- iterative design review with accepted and rejected alternatives;
- export of approved reasoning into technical documentation.

The initial scope should remain explanatory and analytical. Safety-critical design approval, certified calculations, and autonomous control changes remain outside the visual workspace unless a later governed workflow explicitly supports them.

### 4.2 Academic domain

The academic profile should prioritize:

- mathematical derivations and proof sketches;
- annotated figures, charts, and conceptual models;
- research-method diagrams and variable relationships;
- literature evidence attached to claims or canvas regions;
- thesis and paper planning through spatial outlines;
- reviewer-style comments and revision layers;
- conversion of approved content into QYBE document workflows with citations preserved.

The canvas must distinguish user-authored material, retrieved evidence, and AI-generated drafts so academic provenance remains auditable.

## 5. User experience

The visual workspace should be an optional task surface, not a forced replacement for chat.

### Entry paths

1. The user explicitly selects **Visual reasoning** from the chat or document workspace.
2. A domain pack recommends the capability and QYBE offers **Open visual workspace**.
3. A document, image, equation, or diagram selection is sent to a new or existing workspace.
4. A prior workspace is reopened from the related chat, project, or artifact.

### Interaction rules

- The user may continue using normal QYBE chat while the workspace is open.
- AI suggestions appear as unconfirmed drafts with clear accept, reject, edit, move, and resize operations.
- Accepting a draft must record its origin, model/runtime decision, source bindings, and user confirmation event.
- Rejecting a draft must not alter confirmed canvas content.
- Canvas regions can be sent back to chat as selected visual context rather than sending the entire workspace.
- QYBE should show when the visual request may leave the local environment and require policy approval before transmission.

## 6. Target integration architecture

```text
QYBE chat / document / project
  -> DomainPack recommendation
  -> CapabilityPlan: visual_reasoning_canvas
  -> user opens governed workspace
  -> canvas client captures selected visual atlas + geometry
  -> QYBE VisualReasoningAdapter
  -> DataClassification + DataEgressDecision
  -> RAG/evidence attachment selection
  -> ModelPlan + RuntimePlan
  -> multimodal model execution
  -> normalized VisualReasoningDraft commands
  -> client-side draft validation and preview
  -> user accept / reject / edit
  -> QYBE workspace persistence + provenance
  -> optional document/artifact export
```

PenEcho-specific request and response formats should terminate at the adapter boundary. The rest of QYBE should consume provider-neutral visual request and draft objects.

## 7. Responsibility boundary

| Concern | QYBE responsibility | Canvas/PenEcho-compatible responsibility |
|---|---|---|
| Identity and tenancy | Authenticate user, organization, roles, and workspace access | Consume an authorized scoped session |
| Domain selection | Select engineering, academic, or other domain packs | Display domain-specific tools and hints supplied by QYBE |
| Model selection | Resolve approved local or external multimodal model | Never choose an unapproved provider independently |
| Retrieval | Retrieve permitted sources and preserve ACL/citations | Display source references and bind them to regions |
| Data egress | Decide whether images, geometry, and text may leave the deployment | Send only the approved bounded payload |
| Draft validation | Validate normalized command schema and policy | Validate again before rendering or committing |
| Persistence | Store governed workspace state, provenance, and retention metadata | Maintain local editing state and unconfirmed drafts |
| Artifacts | Generate governed reports, figures, or document content | Export selected confirmed visual content to QYBE |
| Audit | Record prompt-safe decisions, timings, IDs, and approvals | Avoid independent sensitive telemetry |

## 8. Data and persistence model

The directional QYBE workspace record should separate:

- confirmed user-authored canvas objects;
- confirmed AI-assisted objects;
- unconfirmed drafts;
- source/evidence bindings;
- domain and task metadata;
- model, runtime, tool, and policy decision identifiers;
- user confirmation and rejection events;
- snapshot and export versions;
- retention, sensitivity, and access-control metadata.

A screenshot alone is not an adequate canonical record. Where possible, QYBE should retain structured object data and use rendered images as derived artifacts. Raw visual atlases, request traces, and temporary crops should follow explicit retention rules and remain disabled by default outside diagnostics.

## 9. Integration options

### Option A — Reference architecture and protocol study

Use PenEcho to study the interaction model, visual atlas construction, structured command protocol, draft confirmation semantics, sparse canvas behavior, and multimodal model requirements.

This option introduces no runtime dependency and is the required first step.

### Option B — Isolated sidecar or separately deployed workspace

Run an unmodified or minimally configured PenEcho instance as an isolated service or trusted-LAN component. QYBE launches it through a scoped workspace session and a QYBE-owned adapter mediates model access and persistence.

Advantages:

- fastest way to validate user value;
- strong isolation from QYBE core;
- straightforward removal or replacement;
- preserves upstream upgradeability.

Constraints:

- authentication and session bridging must be explicit;
- QYBE must not expose unrestricted model credentials to the browser or sidecar;
- public exposure of local CLI execution modes is prohibited;
- network, origin, rate-limit, request-size, and retention controls are required;
- licensing obligations must be satisfied before deployment to users.

**Preferred first executable architecture after evaluation.**

### Option C — QYBE-owned visual client using a compatible adapter contract

Implement a QYBE-native client that follows the validated visual request and structured draft concepts without depending on PenEcho internals. PenEcho can remain a test oracle or optional adapter.

Advantages:

- native QYBE authentication, design system, projects, documents, and citations;
- tighter control over persistence and accessibility;
- simpler organization policy enforcement.

Trade-off:

- materially higher implementation and maintenance cost;
- risk of rebuilding mature canvas behavior prematurely.

This option should be considered only after the sidecar pilot proves sustained domain value.

### Option D — Fork or embed PenEcho code

Do not select this option until architecture, security, product value, and licensing have been reviewed. PenEcho is distributed under GNU AGPL v3.0 only, with an alternative commercial license offered upstream. Incorporating or modifying its code in a networked QYBE product can create source-disclosure obligations that are incompatible with some proprietary distribution goals.

Any fork or direct embedding therefore requires one of:

- confirmed full AGPL compliance for the combined deployment boundary;
- a suitable commercial license from the PenEcho rights holder;
- a legal conclusion that the chosen process and communication boundary does not create an incompatible combined work.

No PenEcho source code should be copied into QYBE during the documentation, protocol-study, or value-validation phases.

## 10. Staged adoption plan

### Phase P0 — Static evaluation

- Review PenEcho architecture, request protocol, command schema, plugin boundaries, security controls, persistence, and tests.
- Record the exact upstream commit or release evaluated.
- Produce a license and dependency assessment.
- Identify the minimum multimodal model capabilities required for handwriting, equations, and diagrams.

**Exit:** written architecture, security, and licensing assessment with no unresolved blocker for an isolated prototype.

### Phase P1 — Domain workflow design

- Define engineering and academic golden workflows.
- Define the provider-neutral `VisualReasoningRequest` and `VisualReasoningDraft` contracts.
- Define how citations and QYBE source ACLs attach to canvas regions.
- Define user confirmation, versioning, retention, and export behavior.
- Add the capability only to domain-pack planning and execution preview; do not invoke a canvas runtime.

**Exit:** domain-pack recommendations and execution previews are understandable and policy-complete.

### Phase P2 — Isolated local pilot

- Run PenEcho or a compatible workspace only on localhost or a trusted LAN.
- Use approved local multimodal inference where quality is sufficient.
- Disable request recording and nonessential telemetry.
- Use synthetic or non-sensitive engineering and academic tasks.
- Keep the pilot outside normal QYBE production sessions.

**Exit:** users complete representative tasks more effectively than with chat-only workflows, with acceptable latency and no security incident.

### Phase P3 — QYBE adapter and shadow integration

- Add a QYBE-owned adapter behind a feature flag.
- Generate policy, model, runtime, and evidence plans without changing the canvas request in shadow mode.
- Compare QYBE decisions with the pilot's actual execution.
- Record prompt-safe metrics only.

**Exit:** decision consistency, eligible workload, and operational value justify controlled integration.

### Phase P4 — Controlled domain beta

- Enable the workspace for selected engineering and academic tenants or projects.
- Require QYBE authentication, workspace authorization, data classification, and egress enforcement.
- Persist confirmed content and provenance in QYBE; keep drafts and temporary atlases retention-limited.
- Export only through governed document or artifact workflows.

**Exit:** quality, privacy, provenance, usability, and rollback gates pass under production-like use.

### Phase P5 — Native or licensed product integration decision

Compare:

- continuing the isolated sidecar;
- building a QYBE-native visual client;
- adopting an upstream commercial license;
- maintaining a compliant AGPL deployment;
- selecting another visual reasoning component.

**Exit:** explicit product, legal, security, and maintenance decision. No default rollout occurs automatically.

## 11. Security and privacy requirements

- Treat canvas images, handwriting, equations, diagrams, and annotations as potentially sensitive business or research data.
- Apply `DataClassification` before model execution or external plugin/network access.
- Require a positive `DataEgressDecision` for every external model or external data call.
- Prefer local multimodal models when they meet defined quality and latency gates.
- Do not send the complete workspace when a bounded crop or selected region is sufficient.
- Keep provider credentials server-side and scoped; never expose them to browser code.
- Disable request recording by default; diagnostic capture requires explicit administrative activation and bounded retention.
- Validate structured draft commands on both server and client before rendering or persistence.
- Reject executable JavaScript or unrestricted active content in model-generated visual output.
- Sandbox interactive widgets and allow network access only to declared approved origins.
- Apply organization ACLs to workspace access, source bindings, snapshots, and exports.
- Provide one-step disablement and a chat-only fallback.

## 12. Evaluation matrix

| Dimension | Required measure |
|---|---|
| Domain value | task completion improvement over chat-only baseline |
| Recognition | handwriting, symbol, equation, and diagram interpretation accuracy |
| Reasoning quality | correctness of derivations, relationships, and generated structures |
| Spatial fidelity | preservation of grouping, arrows, labels, regions, and relative layout |
| Draft control | acceptance, rejection, edit, undo, and accidental-commit rates |
| Evidence | source ACL preservation, citation correctness, and region binding |
| Model/runtime | local-model quality, throughput, latency, memory use, and fallback behavior |
| Language | Bulgarian and English handwriting/text performance |
| Usability | stylus, mouse, touch, zoom, accessibility, and learning curve |
| Privacy | transmitted fields, stored traces, retention, and deletion verification |
| Security | command validation, origin/session controls, sandbox escape tests, credential isolation |
| Operability | health checks, upgrades, rollback, version compatibility, and support burden |
| Licensing | verified AGPL/commercial-license obligations for the chosen deployment model |

Minimum beta gates:

- no bypass of QYBE authentication, ACL, model, tool, or egress policy;
- no model-generated command becomes confirmed without explicit user action;
- citations and evidence remain structured rather than flattened only into pixels;
- local or external execution choice is visible and auditable;
- a chat-only fallback and one-step feature disablement are available;
- representative engineering and academic golden tasks show measurable benefit;
- licensing approval exists for the exact integration and distribution model.

## 13. Non-goals

This plan does not approve:

- replacing QYBE chat or Documents/Univer with PenEcho;
- making PenEcho the model router, RAG engine, policy authority, or system of record;
- copying PenEcho code into QYBE before licensing review;
- exposing Codex CLI, Claude CLI, or provider credentials through a public canvas endpoint;
- using visual output as unreviewed engineering certification or academic evidence;
- storing unrestricted visual request traces by default;
- enabling generated active code without sandbox and policy controls.

## 14. Decision log

- **2026-07-23 — Domain relevance:** PenEcho is retained as a strong reference and optional integration candidate for engineering and academic visual reasoning.
- **2026-07-23 — Integration boundary:** QYBE owns orchestration, policy, RAG, provenance, persistence, and model/runtime selection; the canvas remains a replaceable interaction adapter.
- **2026-07-23 — Preferred path:** protocol study, domain capability contract, and isolated sidecar pilot before any native implementation.
- **2026-07-23 — Licensing:** no PenEcho code is copied or embedded until AGPL obligations or an alternative commercial license are explicitly approved.
