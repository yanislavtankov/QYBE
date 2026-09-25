# QYBE — Data Analyst Cookbook extraction and integration plan

Status: reference design / implementation backlog (not deployed)
Reviewed: 2026-09-25
Source: https://github.com/openai/openai-cookbook/tree/main/examples/agents_api/apps/data_analyst
Source README: https://github.com/openai/openai-cookbook/blob/main/examples/agents_api/apps/data_analyst/README.md
License: MIT, Copyright (c) 2025 OpenAI; preserve original attribution/license in any substantial copied code.

## Architectural decision
Preserve QYBE's local-first, model-agnostic router, runtime policy, domain packs, tool contracts, orchestrator, RAG and task workspace. Do not install the standalone example as an additional production server, replace routing with OpenAI Agents API, or hardcode its model. Treat the cookbook as design/reference code and implement its portable functionality behind QYBE's existing tool registry and authorization/runtime policies. Use an OpenAI-specific session adapter only as an optional cloud execution backend.

## Extracted source mapping
| Cookbook source | Relevant extraction | QYBE adaptation |
| --- | --- | --- |
| agent.py / define_tool, TOOLS | JSON Schema function contracts; optional deferred save_memory; handler dispatch; follow-up conversation mapping; streamed events and tool call dedupe | Register four versioned QYBE tools in BI domain; keep all calls under central orchestrator, audit and model-neutral tool dispatch |
| warehouse.py / table_names, inspect_table, search_tables | Live discovery of actual schema, types, nullability + owner/freshness descriptions | Metadata discovery adapter per data source with per-tenant table/column allowlist, semantic index of large schemas and freshness tracking |
| warehouse.py / search_context and context.example.json | Metric definitions, reviewed SQL templates, company documents, query history | Business semantic layer + RAG + versioned, reviewed KPI definitions scoped by tenant |
| warehouse.py / query | Read-only SQL, PostgreSQL read-only transaction option, 30s statement timeout, 100 returned rows | Isolated read-only DB principal, SQL AST validation, database-side controls, row/byte/time budgets, result sampling and provenance |
| memory.py / list, search, save, delete | Personal/team corrections saved across sessions | Tenant-scoped durable Postgres/pgvector store; approval workflow for team-wide rules; source, author, version, revocation and audit |
| main.py / Question, ask, memories routes | API shape, conversation continuation, memory management | Integrate into QYBE API and UI; never ship example's unauthenticated single-user routes directly |
| index.html | Investigative chat and query transparency UI | Task workspace panel showing SQL, tables, assumptions, metrics, evidence, charts and exports |

### Exact upstream files checked
- agent.py: https://github.com/openai/openai-cookbook/blob/main/examples/agents_api/apps/data_analyst/agent.py
- warehouse.py: https://github.com/openai/openai-cookbook/blob/main/examples/agents_api/apps/data_analyst/warehouse.py
- memory.py: https://github.com/openai/openai-cookbook/blob/main/examples/agents_api/apps/data_analyst/memory.py
- main.py: https://github.com/openai/openai-cookbook/blob/main/examples/agents_api/apps/data_analyst/main.py
- context.example.json: https://github.com/openai/openai-cookbook/blob/main/examples/agents_api/apps/data_analyst/context.example.json

## Proposed domain contract (QYBE-specific design; not copied production code)

```yaml
id: business_intelligence
version: 0.1.0
description: Analyze governed business data and produce traceable decisions support.
execution:
  mode: local_first
  preferred_model: auto
  allow_cloud_fallback: policy_controlled
  uses_existing_router: true
  uses_existing_orchestrator: true
tools:
  - bi.search_tables
  - bi.search_context
  - bi.query_warehouse
  - bi.save_correction
optional_tools:
  - workspace.create_chart
  - workspace.export_report
policies:
  query_access: read_only
  database_identity: authenticated_tenant_scoped
  memory_write: explicit_user_request
  team_memory: review_required
  max_returned_rows_default: 100
  statement_timeout_ms_default: 30000
  provenance_required: true
```

Tool contract example (QYBE-native illustrative, not a copy of the upstream handler):
```python
BI_TOOLS = {
    "bi.search_tables": {"query": "string"},
    "bi.search_context": {"query": "string"},
    "bi.query_warehouse": {"sql": "string"},
    "bi.save_correction": {"note": "string", "scope": ["personal", "team"]},
}

async def execute_bi_tool(call, principal, policy, registry):
    policy.authorize(principal=principal, tool=call.name, args=call.arguments)
    return await registry.execute(call.name, call.arguments, principal=principal)
```

Do not execute this illustrative code without binding actual QYBE interfaces and tests.

## Important production gaps in upstream demo
1. SQL regex checks only SELECT/WITH prefix and semicolons; not robust SQL authorization. Writable CTEs, dangerous functions, expensive queries or data exfiltration can require AST validation and DB-side privileges. Read-only account is non-negotiable. A 100-row fetch is not an actual database LIMIT or resource cap.
2. PostgreSQL uses default_transaction_read_only and statement_timeout=30000; the database account must independently lack write, unsafe functions and unapproved table access.
3. `main.py` is a single-user demo with no production authentication; default analyst identity is not a tenant boundary. Never use user-supplied IDs to authorize sessions or memories.
4. `memory.py` stores data in a shared JSON file. Team visibility is broad; delete should enforce tenant, author/admin and scope authorization; records need concurrence and source/version.
5. `relevant()` uses simple English/alphanumeric matching and weak any-term retrieval; replace with QYBE hybrid RAG / embeddings and schema-aware ranking, including Bulgarian.
6. `DataAnalyst.sessions` and `owners` live in process RAM. Persist QYBE task/session mappings and recovery state before multi-worker deployment.
7. Example's OpenAI-specific sessions, streamed event names, `tool_search` and `programmatic_tool_calling` are not portable to Ollama/local models. Reuse the behavior, not those API bindings.
8. Keep query outcomes, errors, executed SQL, row counts and timestamps as structured audit evidence; the narrative must not be treated as proof.

## Incremental plan
P0: adopt tool contracts and warehouse metadata discovery behind existing router; single read-only PostgreSQL connector with user/tenant authorization.
P1: add governed KPI glossary, reviewed query templates, QYBE RAG retrieval, provenance and query trace UI.
P2: add explicit personal corrections and reviewed team corrections in durable tenant-aware storage.
P3: extend analysis output to workspace CSV/XLSX/charts/report exports, isolated code interpreter if needed.
P4: optional cloud Agents API adapter, only if runtime policy selects cloud and information governance permits it.

## Acceptance tests
- Existing chat, router and local models still function when BI domain is disabled.
- User cannot read other tenants' schemas, rows, sessions or memories.
- SQL DDL/DML, writable CTE, multi-statement and excessive queries are denied by layered controls.
- Every reported quantitative result is traceable to SQL, source table(s), filters and metric definition.
- Follow-up questions retain task scope but do not bypass authorization.
- Correction persistence requires explicit request; team-wide correction requires approval; delete and revision are audited.
- BI analysis works without OpenAI API credentials in local-first mode.
