# Xiaomi MiMo model family — QYBE integration evaluation

**Status:** approved for reference/benchmark backlog; not integrated or enabled  
**Reviewed:** 2026-09-25  
**QYBE branch:** `dev`  
**Scope:** model/provider/runtime candidates, not a replacement for QYBE orchestration  
**Input article:** https://digital.bg/xiaomi-predstavi-naj-mosthniya-model-s-otvoren-kod-v-sveta-i-izprevari-deepseek-i-google/  
**Verification basis:** Xiaomi's September 22, 2026 release/docs and official model cards. The news site returned HTTP 403 during review; the claims below are grounded in primary sources rather than inaccessible article text.

## 1. Decision

Retain **MiMo-V2.6-Pro**, **MiMo-V2.6-Flash**, and **MiMo-V2.6-Distill-Qwen-9B** as distinct candidate configurations. The immediate, low-cost experiment is **the distilled 9B model locally**. Test **Flash via official hosted API** on policy-approved requests and **Pro via official hosted API** only for tasks requiring deeper reasoning/long-horizon agent execution; do not promote either based solely on launch benchmarks.

QYBE remains **local-first, model-agnostic and provider-neutral**. MiMo is a replaceable model/provider choice selected through existing and planned capability/model/runtime resolution, not a new router, agent framework, domain pack, or mandatory server. This document authorizes documentation and a later isolated pilot only; no credentials, cloud egress, model download, production flag, or endpoint change is performed here.

## 2. Model facts and deployment feasibility (as of review)

| Variant | Published properties | Plausible QYBE role | DGX Spark / EdgeXpert constraint |
| --- | --- | --- | --- |
| `MiMo-V2.6-Distill-Qwen-9B` | SFT/distillation of Qwen3.5-9B; official MIT-labelled model card; text+image model card; agent/code research checkpoint | local planner/worker/tool-use candidate; benchmark against existing fast models | Full checkpoint ~18.8 GB according to HF repository; community Ollama Q4 packaging ~5–7 GB. Quantized tool/parser compatibility is not guaranteed; benchmark exact tag/digest. |
| `mimo-v2.6-flash` / `MiMo-V2.6-Flash-RL` | 309B *total*, ~15B active MoE parameters; advertised 1M context; multimodal *input*, text output; open weights | budget cloud worker, multimodal document/image understanding, subagent calls | 15B active does **not** mean 15B weights to store. An Ollama community Q4 listing is ~178 GB, over Spark's entire 128 GB unified memory before KV cache and QYBE services; standard local residency is not a viable default. |
| `mimo-v2.6-pro` / `MiMo-V2.6-Pro-RL` | approximately 1.02T total / 42B active MoE; advertised 1M context; multimodal *input*, text output; open weights | exceptional cloud specialist for complex plans, code, research, and verification | Not a sensible single-Spark local deployment target; requires a larger/multi-node or highly experimental offloaded runtime and separate feasibility work. |

The published 1M-token window is an API/model capability ceiling, **not** a promise that QYBE can economically send that context or execute it locally. Always measure effective context, limits, latency, reasoning-token billing and citation accuracy for the exact deployment.

Model weights are described by Xiaomi as MIT-licensed, including commercial inference/fine-tuning. Before redistribution, pin and inspect the exact model-card licence, any upstream base-model terms, code licences, and relevant notices; model weights and runtime code may have separate licensing.

**Official overseas API price, USD per 1M tokens, 2026-09-22:** Flash $0.14 uncached input / $0.28 output; Pro $0.435 uncached input / $0.87 output; cached-input rates Flash $0.0028 and Pro $0.0036. Official Batch API lists half the standard input/output rates. Extra tools (e.g. provider web search), retries, reasoning output and multimodal token accounting can add cost. Re-check pricing before activation.

## 3. Architecture fit

```text
User request
  -> QYBE existing chat / shadow routing
  -> organization policy + DataClassification + DataEgressDecision
  -> CapabilityPlan -> ModelPlan -> RuntimePlan
  -> existing LLM provider abstraction / LiteLLM or OpenAI-compatible adapter
     -> Local: discovered Ollama or SGLang 9B checkpoint
     -> Approved cloud: Xiaomi MiMo OpenAI-compatible API (Flash / Pro)
  -> QYBE-controlled tools, MCP, RAG, workspace, verifier and provenance
```

- Existing QYBE/Onyx code surfaces to examine in any implementation PR: `backend/onyx/llm/factory.py`, `backend/onyx/llm/model_capabilities.py`, `backend/onyx/llm/well_known_providers/llm_provider_options.py`, and current provider administration/configuration. Use existing OpenAI-compatible-provider or LiteLLM mechanisms before proposing a dedicated provider implementation.
- The official MiMo API supports OpenAI-style chat completion at `https://api.xiaomimimo.com/v1`, using `mimo-v2.6-flash` and `mimo-v2.6-pro` in lowercase. It also advertises Anthropic protocol compatibility. Obtain the API key explicitly from an administrator; use QYBE credential storage, per-tenant permissions, egress approvals, rate limits and per-task hard budgets.
- Prefer QYBE-owned web search/tools and provenance. The provider's web-search plugin is a distinct billable optional capability, not automatically equivalent to QYBE SearchProvider/BrowserProvider.
- Discover local model tags at runtime. Record model family, exact checkpoint/quantization, runtime version, usable context, tool parser, vision status, reasoning format, memory estimate, latency, availability, and observed benchmark profile. **Do not hardcode MiMo into the global routing default or infer capability solely from the model name.**
- Separate model's internal MoE router from QYBE's orchestration router. The former selects neural experts; the latter selects workflow, tools, provider and runtime.
- Tool calling, streamed partial tool-call assembly, JSON schema validation, reasoning/content separation and multimodal transport require integration tests. JSON-object mode alone is not JSON-schema conformance.
- Keep the existing shadow-only routing rule; any live model/provider selection requires reviewed flags and explicit organization permissions.

## 4. Proposed adoption stages

**M0 — catalogue / static review.** Keep the three candidates in documentation, record official source revisions, model digests/licensing, announced API prices and compatible runtimes. No download or production change.

**M1 — isolated 9B feasibility.** After confirming DGX Spark/Ollama GPU operation, test an exact community Ollama quantization against the official HF checkpoint/SGLang reference when feasible. First measure Ollama tool-call parsing and thinking-content boundaries; use a separate SGLang OpenAI-compatible endpoint if the community Ollama build is incompatible. Reuse existing local runtime profile and no new QYBE daemon by default.

**M2 — provider API pilot.** Add MiMo as a configurable approved external OpenAI-compatible endpoint via the existing provider management UI, with secrets stored securely. Compare Flash and Pro only on synthetic or expressly cleared data. Start with explicit manual selection; no invisible cloud fallback. Disable vendor web search until QYBE provenance/cost policy is verified.

**M3 — QYBE task-level benchmark.** Compare against QYBE's currently installed local fast/reasoning models and at least one approved cloud control with matched prompts, tools, budgets and comparable context. Test Bulgarian/English chat, academic source-grounded writing, BI SQL planning (no privileged execution), code changes with tests, multi-step subagents, structured JSON, RAG citation preservation, diagram/image understanding, cancellation and prompt-injection containment.

**M4 — optional runtime resolution.** Only if M1–M3 pass, expose validated candidates in the existing Auto (local/global/mixed) and explicit model UI, preserving organization policy, user choice, provenance, predictable fallback, and per-task cost and latency ceilings. Model-specific tuning belongs to optional metadata/configuration, never a fork of the orchestrator.

## 5. Acceptance gates / test plan

- **Correctness:** QYBE golden business tasks, code test success, Bulgarian terminology, RAG answer grounding/citation retention, document and image extraction accuracy; no material regression against task-matched baseline.
- **Agent compatibility:** single/multiple tool calls, valid JSON arguments, tool-result continuation, streaming, partial calls, structured outputs, stable reasoning parsing, supported multimodal inputs; failure reported rather than silently fabricated.
- **Privacy and security:** permissioned external calls only; tenant isolation, prompt-safe telemetry, no leaked credentials, prompt-injection and tool authorization tests, no implicit vendor web search, auditable side effects.
- **Hardware:** 9B peak shared RAM with the full QYBE stack, GPU offload verified, token throughput, time-to-first-token, warm/cold loads, context 1k/8k/16k/32k as supported, concurrency and OOM recovery.
- **Economics:** model+tool+retry+reasoning tokens per *successfully completed task*, cached/uncached pricing and Batch API when asynchronous completion is acceptable; evaluate quality per cost, not promotional rankings.
- **Operations:** exact version/digest and licence reviewed, health/circuit breaking, quotas, deterministic rollback to previous model configuration, provider outages, API change/deprecation handling.

## 6. Research opportunity separate from inference

MiMo-V2.6 release also includes 7,000+ RL agent task environments, training framework materials and lightweight/composable harness concepts, plus the 9B SFT checkpoint. Treat these as a **separate future QYBE evaluation/research track**, useful for tool-use regression corpora, agent trajectories, verifier design and small-model training experiments. Do not conflate published self-improvement training procedures with automatic learning in the deployed QYBE product, and do not adopt their harness as QYBE's orchestration authority.

## 7. Primary sources

- Release and research resources: https://mimo.mi.com/docs/en-US/news/latest/v2-6
- Official pricing: https://mimo.mi.com/docs/en-US/pricing
- Flash API: https://mimo.mi.com/models/en-US/mimo-v2.6-flash
- Pro API: https://mimo.mi.com/models/en-US/mimo-v2.6-pro
- OpenAI-compatible API: https://mimo.mi.com/docs/en-US/quick-start/summary/first-api-call
- Official 9B checkpoint: https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Distill-Qwen-9B
- Official Flash checkpoint: https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Flash-RL
- DGX Spark memory specification: https://docs.nvidia.com/dgx/dgx-spark/hardware.html
- Community Ollama 9B example (not an official Xiaomi release): https://ollama.com/maternion/mimo-v2.6
- Community Ollama Flash example (not an official Xiaomi release): https://ollama.com/frob/mimo-v2.6-flash
