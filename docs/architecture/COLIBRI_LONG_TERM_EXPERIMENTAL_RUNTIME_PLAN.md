# Colibri Long-Term Experimental Runtime Plan

**Status:** Long-term experimental research only  
**Updated:** 2026-07-25  
**Base branch:** `dev`  
**Implementation status:** Not approved for implementation or production use  
**Evaluated project:** [JustVugg/colibri](https://github.com/JustVugg/colibri)

## 1. Decision

Colibri is relevant enough to retain in the QYBE roadmap as a **long-term experimental local inference runtime candidate**.

It is not approved as:

- a replacement for Ollama;
- a default QYBE inference runtime;
- a QYBE core dependency;
- embedded or forked source code;
- a production multi-user inference service;
- an immediate implementation priority.

Any future evaluation must integrate Colibri only through a QYBE-owned, provider-neutral runtime adapter and its OpenAI-compatible API.

## 2. Why Colibri is relevant to QYBE

Colibri explores a useful local-first inference direction for very large sparse Mixture-of-Experts models. It treats VRAM, system memory, and NVMe storage as a managed hierarchy and streams routed experts when the complete model cannot remain resident in fast memory.

This is relevant to QYBE because it may eventually provide:

- access to frontier-scale open MoE models on EdgeXpert/DGX Spark-class hardware;
- local processing for privacy-sensitive business tasks;
- an OpenAI-compatible runtime surface that can remain replaceable;
- persistent KV contexts and prefix reuse across stateless API requests;
- explicit runtime queueing and health metrics;
- a research path for workload-aware expert placement and local inference optimization.

Colibri is especially interesting as an EdgeXpert experiment because upstream community work already targets NVIDIA DGX Spark/GB10, ARM64, CUDA, unified memory, and local NVMe storage.

## 3. Required architecture boundary

The intended future boundary is:

```text
QYBE request
  -> CapabilityPlan
  -> ModelPlan
  -> RuntimePlan
  -> QYBE RuntimeResolver
  -> optional ColibriRuntimeAdapter
  -> isolated Colibri OpenAI-compatible API
  -> Colibri engine
  -> compatible local MoE model
```

QYBE remains responsible for:

- model and runtime selection;
- organization privacy and data-egress policy;
- authentication and authorization;
- prompt construction and context budgeting;
- RAG, connectors, tools, and MCP orchestration;
- tool-call validation;
- telemetry policy and audit records;
- retries, fallbacks, cancellation, and timeout handling;
- user-visible model/runtime controls;
- evaluation and production-readiness decisions.

Colibri must remain an isolated inference implementation behind the QYBE runtime contract.

## 4. Integration principles

1. **Ollama remains the default local runtime.** Colibri may only be added as an optional experimental provider.
2. **No fork-first strategy.** QYBE should not carry a private Colibri fork unless a later decision explicitly justifies the maintenance burden.
3. **No direct engine coupling.** QYBE should use the OpenAI-compatible API rather than Colibri internal C interfaces or storage formats.
4. **Feature flag required.** Discovery, selection, and execution must remain disabled by default.
5. **Provider-neutral metadata.** Colibri-specific configuration must be mapped into generic `LocalModelRuntimeProfile` and `RuntimePlan` fields where possible.
6. **No silent fallback.** Unsupported tools, content types, context sizes, or runtime failures must produce explicit decisions and observable fallback behavior.
7. **Upstream baseline first.** Performance claims must be reproduced with an unmodified tagged upstream release before experimental patches are considered.
8. **Quality before throughput.** Routing or cache optimizations that change selected experts or output semantics must not be enabled by default.

## 5. Current reasons to defer implementation

Colibri is promising but too early and specialized for current QYBE runtime adoption.

### 5.1 Project maturity

The project is young and evolving rapidly. Runtime behavior, supported APIs, model formats, CUDA paths, tool handling, and performance tuning are still changing frequently.

### 5.2 Model footprint

The primary documented GLM-5.2 int4 package is approximately 372 GB. This is feasible on EdgeXpert storage but creates substantial operational requirements for:

- download and conversion time;
- model verification and checksums;
- disk capacity planning;
- backup and recovery policy;
- SSD endurance and sustained read performance;
- upgrade and rollback procedures.

### 5.3 Limited model coverage

Current practical support is concentrated on a small number of model families. QYBE must not introduce a generic runtime option that appears broadly compatible while only a narrow set of models is actually validated.

### 5.4 Concurrency

The documented server intentionally serializes generation and queues concurrent requests. This may be acceptable for a specialist experimental backend but is not sufficient as QYBE's only inference service in a multi-user deployment.

### 5.5 Long-context prefill

QYBE RAG, tool, coding, and business-document workflows can produce large system prompts and retrieved contexts. Disk-streaming MoE inference may have acceptable decode throughput while still producing unacceptable time to first token for large prompts.

### 5.6 Tool and structured-output compatibility

OpenAI- and Anthropic-compatible tool surfaces are available, but QYBE must independently verify:

- exact tool schema handling;
- streamed tool-call assembly;
- multiple tool calls;
- tool-result continuation;
- malformed or partial tool-call recovery;
- JSON schema compliance;
- grammar-constrained outputs;
- cancellation and retry behavior.

### 5.7 Unified-memory contention

EdgeXpert/DGX Spark uses shared unified memory. Colibri model residency, QYBE containers, databases, search services, indexing workers, code execution, and other local models may compete for the same memory capacity. Isolated inference benchmarks are therefore insufficient.

## 6. Long-term experimental phases

No phase below authorizes implementation by itself.

### Phase C0 — Upstream watch and static review

- Track tagged Colibri releases and supported model families.
- Review API compatibility, security fixes, model validation, CUDA/ARM64 support, and queue semantics.
- Record license and model-weight license changes.
- Avoid maintaining QYBE patches or deployment files.

**Exit:** stable upstream release line and a clear supported configuration for EdgeXpert/DGX Spark.

### Phase C1 — Isolated EdgeXpert feasibility benchmark

Run Colibri outside the QYBE stack using a tagged upstream release.

Measure:

- installation and model preparation;
- cold and warm startup time;
- time to first token;
- prefill throughput;
- decode throughput;
- RAM/unified-memory consumption;
- NVMe read rate and temperature;
- persistent KV behavior;
- crash and restart recovery;
- output quality against a reference runtime.

Test context sizes of at least:

- 1k tokens;
- 8k tokens;
- 16k tokens;
- 32k tokens.

**Exit:** useful quality and acceptable latency for at least one clearly defined QYBE workload.

### Phase C2 — QYBE compatibility harness

Use a temporary external harness, not product integration, to test representative QYBE requests through the OpenAI-compatible API.

Required scenarios:

- normal multi-turn chat;
- Bulgarian and English business tasks;
- RAG with citations and retrieved context;
- structured JSON generation;
- single and multiple tool calls;
- tool-result continuation;
- long-document synthesis;
- cancellation, timeout, and queue saturation;
- context-length rejection and recovery.

**Exit:** protocol compatibility is demonstrated without QYBE-specific engine modifications.

### Phase C3 — Shadow runtime adapter

Only after the generic `RuntimeResolver`, `RuntimePlan`, and `LocalModelRuntimeProfile` are stable:

- implement a QYBE-owned Colibri adapter behind a disabled feature flag;
- discover health and model metadata without sending production prompts;
- produce shadow runtime recommendations;
- compare projected selection with Ollama and other local runtimes;
- record prompt-safe timing and capability metadata only.

The adapter must not alter live routing during this phase.

**Exit:** stable shadow operation, correct capability matching, and no sensitive telemetry leakage.

### Phase C4 — Restricted experimental execution

Allow execution only for an administrative evaluation tenant or explicit internal test profile.

Required safeguards:

- explicit model/runtime selection;
- one-request-at-a-time capacity awareness;
- strict timeout and cancellation handling;
- Ollama or approved runtime fallback;
- bounded queueing;
- health-based circuit breaker;
- feature-flag rollback;
- no experimental routing-semantic modifications;
- clear user indication that the runtime is experimental.

**Exit:** sustained reliability and measurable task-level benefit over existing QYBE local runtime options.

## 7. EdgeXpert benchmark matrix

| Dimension | Required measurement |
|---|---|
| Model quality | QYBE task score, factuality, Bulgarian quality, code and tool accuracy |
| Prefill | tokens/s and TTFT at 1k, 8k, 16k, and 32k prompt sizes |
| Decode | cold, warm, and sustained tokens/s |
| Memory | peak unified memory, steady-state residency, impact on QYBE services |
| Storage | model size, read bandwidth, read amplification, SSD temperature |
| Concurrency | queue delay, rejection behavior, cancellation, fairness |
| Tools | schema validity, streamed calls, tool-result continuation, recovery |
| Structured output | valid JSON rate, schema compliance, constrained generation |
| RAG | citation preservation, context use, long-context answer quality |
| Reliability | startup, shutdown, crash recovery, corrupted/incomplete model behavior |
| Operations | health checks, logs, metrics, upgrade, rollback, checksum verification |
| Security | authentication, bind address, CORS, input limits, dependency and binary provenance |

Benchmarks must run both:

1. with Colibri isolated; and
2. with the complete QYBE Docker stack active.

## 8. Minimum acceptance gates

Colibri must not become selectable in normal QYBE operation unless all of the following are satisfied:

- a tagged upstream version is pinned and reproducibly built or verified;
- the exact model and quantization are pinned and checksummed;
- long-context TTFT is acceptable for the selected workload;
- tool calls and structured outputs meet QYBE validity thresholds;
- RAG evidence and citations are preserved;
- unified-memory pressure does not destabilize QYBE services;
- queue saturation and cancellation are handled correctly;
- runtime failures automatically fall back or fail clearly;
- no raw prompts or private content enter unapproved telemetry;
- output quality provides a material advantage over the existing Ollama option;
- one-step disable and rollback are tested;
- no required local Colibri patch remains outside an upstream release.

## 9. Experimental optimizations boundary

Colibri research includes expert caching, prefetching, tier placement, speculative decoding, and experimental cache-aware routing.

QYBE must distinguish between:

- optimizations that preserve model precision and routing semantics; and
- optimizations that substitute experts or otherwise change model behavior.

Any optimization that changes selected experts, routing semantics, or deterministic output must be treated as a separate model variant with separate quality evaluation. It must never be silently enabled as a performance configuration.

## 10. Non-goals

This plan does not propose:

- replacing QYBE's orchestration router with the model's MoE router;
- using Colibri expert affinity as a QYBE business-domain classifier;
- coupling QYBE domain packs to Colibri internals;
- shipping a 372 GB model with every QYBE installation;
- exposing Colibri directly to untrusted networks;
- replacing general-purpose local runtimes;
- prioritizing Colibri ahead of current orchestration, policy, document, and runtime-resolution work.

## 11. Long-term roadmap placement

Colibri should be revisited only after:

1. the fresh QYBE/Onyx foundation is stable;
2. `CapabilityPlan`, `ModelPlan`, and `RuntimePlan` are established;
3. runtime discovery is provider-neutral;
4. Ollama runtime behavior is reliably profiled;
5. data classification and egress policy are enforced;
6. execution-plan preview and controlled live execution are available;
7. EdgeXpert resource scheduling and observability are mature.

Until then, Colibri remains a documented research candidate rather than an active development task.

## 12. Decision log

- **2026-07-25 — Relevance:** Colibri is sufficiently relevant to QYBE's local-first and EdgeXpert direction to retain as a long-term experimental runtime candidate.
- **2026-07-25 — Boundary:** integration, if later approved, must use a QYBE-owned provider-neutral adapter over the OpenAI-compatible API.
- **2026-07-25 — Default runtime:** Ollama remains the default local runtime; Colibri is disabled and non-production.
- **2026-07-25 — Implementation:** no code, container, dependency, model download, or runtime configuration is authorized by this document.
- **2026-07-25 — Evaluation:** only tagged upstream releases and reproducible EdgeXpert benchmarks count as evidence for future adoption.
