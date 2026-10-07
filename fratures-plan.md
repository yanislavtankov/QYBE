# QYBE Academic Research & Long-Form Writing Domain — Feature Plan

**Status:** Product and architecture proposal  
**Target project:** QYBE  
**Reference project reviewed:** [`Bklieger/infinite-bookshelf`](https://github.com/Bklieger/infinite-bookshelf)  
**Reference revision:** `400b272175945d35eaefa68aefe9106fa9d7e467` (`main`, reviewed 2026-07-23)  
**QYBE base branch:** `dev`  
**Purpose of this document:** Capture reusable ideas from Infinite Bookshelf and translate them into a QYBE-native, local-first, evidence-grounded domain for thesis, dissertation, academic report, and other long-form research work.

> This is not a proposal to embed or fork Infinite Bookshelf into QYBE. It is a design study. QYBE should reuse the useful product patterns while implementing its own provider-neutral, privacy-governed, source-grounded architecture.

---

## 1. Executive decision

Infinite Bookshelf demonstrates a simple but effective long-form generation pattern:

1. accept a topic and instructions;
2. generate a structured outline as JSON;
3. generate each section from the outline;
4. stream content to the UI;
5. allow role-specific model selection;
6. incorporate optional seed content;
7. export the complete result.

This pattern is useful for QYBE, but the reference implementation is optimized for rapid book generation rather than academic reliability. Its own README warns that generated content may be inaccurate or contain placeholders, and the current section writer receives primarily the section title/description instead of a complete evidence and project context.

For QYBE, the correct adaptation is an **Academic Research & Writing Domain Pack** with a governed project state machine:

`Project brief → requirements → research questions → source corpus → evidence map → outline → section drafts → verification → review/revision → final synthesis → export`

The essential difference is that QYBE must treat a thesis or dissertation as an evolving, traceable research project, not as one large text-generation request.

---

## 2. What Infinite Bookshelf contains

### 2.1 Product pattern

The reference application is a Streamlit application that scaffolds a long-form book from a short topic. It separates the work into title, structure, and section-generation agents.

Relevant files:

- `main.py`
- `pages/advanced.py`
- `infinite_bookshelf/agents/title_writer.py`
- `infinite_bookshelf/agents/structure_writer.py`
- `infinite_bookshelf/agents/section_writer.py`
- `infinite_bookshelf/ui/book.py`
- `infinite_bookshelf/ui/components/advanced_form.py`
- `infinite_bookshelf/ui/components/download.py`

### 2.2 Useful implementation ideas

#### A. Structure-first generation

`structure_writer.py` requests a JSON object describing sections and nested subsections before prose is generated. This is significantly better than asking one model call to write a complete long document because it creates an explicit intermediate representation.

**QYBE adaptation:** introduce a versioned `AcademicOutline` model with stable node IDs, section intent, research-question coverage, source requirements, target word count, dependencies, and review status.

#### B. Separate roles for title, structure, and content

The application separates title generation, outline generation, and section writing. The advanced UI allows different models to be chosen for these roles.

**QYBE adaptation:** preserve role separation, but use QYBE's provider-neutral tiers and policy controls:

- `fast` for classification, metadata extraction, formatting, and low-risk transformations;
- `balanced` for outline refinement, source synthesis, and section drafting;
- `deep` for methodology review, contradiction analysis, findings/discussion alignment, and final academic synthesis.

The organization privacy policy and data-egress policy must override all model preferences.

#### C. Advanced controls

The advanced form supports:

- additional instructions;
- writing style;
- complexity level;
- seed content;
- uploaded text;
- model selection by role.

**QYBE adaptation:** replace generic controls with an academic project profile:

- academic level: coursework / bachelor / master / doctoral;
- language and locale;
- discipline and subdiscipline;
- institution and formatting rules;
- methodology type;
- citation style;
- target word count;
- chapter structure;
- research questions and hypotheses;
- required and excluded sources;
- supervisor/examiner instructions;
- permitted use of web/cloud models;
- preferred model tier per task.

#### D. Streaming section generation

The reference app streams section tokens into placeholders and updates basic inference statistics.

**QYBE adaptation:** stream drafts into an editable document surface, but persist checkpoints and provenance. A partially generated section must remain recoverable after interruption. Statistics should remain prompt-safe and may include:

- task ID;
- role;
- model/runtime;
- token counts;
- elapsed time;
- local/cloud classification;
- source IDs used;
- quality-gate outcomes;
- prompt template version;
- no raw business or academic text in telemetry.

#### E. Hierarchical document object

The `Book` class flattens the structure, keeps per-section content, renders a table of contents, and reconstructs Markdown.

**QYBE adaptation:** create an `AcademicDocumentGraph`, not only a flat document. Each node should retain:

- stable UUID;
- parent and ordering;
- heading level;
- section purpose;
- draft body;
- source/evidence links;
- RQ/hypothesis links;
- word budget;
- status;
- revision history;
- quality findings;
- unresolved supervisor comments;
- dependencies on tables, figures, appendices, or datasets.

#### F. Export

The reference application exports text and styled PDF.

**QYBE adaptation:** support academic deliverables:

- editable document workspace;
- DOCX;
- PDF;
- Markdown;
- optional LaTeX;
- BibTeX;
- Word bibliography XML where required;
- citation report;
- evidence/claim audit report;
- appendix package;
- anonymized review copy.

### 2.3 Limitations that QYBE must not copy

1. **No reliable source-grounding contract.** The reference app generates prose without requiring every material claim to be supported by an ingested source.
2. **Insufficient cross-section context.** The README states that section generation currently relies on section-level context rather than the fuller book context.
3. **No academic project state model.** There is no first-class representation of RQs, hypotheses, methodology, findings, discussion, limitations, or examiner comments.
4. **No claim-to-citation traceability.**
5. **No citation verification or bibliographic deduplication.**
6. **No structured review/rework loop.**
7. **No persistence model suitable for multi-week or multi-month work.**
8. **Hardcoded provider and model assumptions.**
9. **Prompt-only quality control.**
10. **No institutional template validation.**
11. **No explicit privacy/data-egress decision.**
12. **No protection against untrusted instructions embedded in uploaded documents.**
13. **No distinction between source facts, user assertions, model inferences, and generated connective prose.**
14. **No research ethics, plagiarism, or authorship workflow.**
15. **Whole-document generation encourages high regeneration cost and a large error blast radius.**

---

## 3. QYBE product scope

### 3.1 Domain name

Proposed domain pack identifier:

`academic_research_writing`

User-facing labels may include:

- Thesis Workspace
- Dissertation Workspace
- Academic Research Project
- Research & Long-Form Writing

### 3.2 Supported project types

Initial scope:

- bachelor thesis;
- master thesis;
- doctoral dissertation;
- academic report;
- literature review;
- research proposal;
- case-study report;
- technical or engineering graduation project.

Later scope:

- journal article;
- conference paper;
- systematic/scoping review;
- grant proposal;
- habilitation work;
- multi-author research project.

### 3.3 Core user promise

QYBE should help the user plan, research, draft, verify, revise, and export a long academic work while maintaining:

- a stable project structure;
- traceability from claims to sources;
- alignment between research questions, methodology, findings, discussion, and conclusion;
- institution-specific requirements;
- local-first privacy;
- controlled model and tool use;
- explicit human approval at consequential steps.

QYBE must not market the feature as autonomous thesis generation. The system is a research and writing workbench with accountable assistance.

---

## 4. Primary user journeys

### 4.1 Start from a topic

The user provides:

- working title/topic;
- academic level;
- discipline;
- language;
- word/page target;
- deadline;
- institution requirements;
- available sources or notes.

QYBE generates a proposed project brief, research objective, main RQ, subquestions, candidate hypotheses where appropriate, chapter structure, and work plan. Nothing becomes final until accepted or edited.

### 4.2 Start from an existing document

The user uploads a partial thesis/dissertation and optionally examiner or supervisor notes.

QYBE:

1. parses the document structure;
2. identifies RQs, hypotheses, chapter purposes, references, figures, and tables;
3. maps comments to affected sections;
4. detects missing or inconsistent components;
5. proposes a revision backlog;
6. preserves original wording and revisions as separate versions.

### 4.3 Build a source corpus

The user adds PDFs, DOCX files, web pages, datasets, notes, or connector documents.

QYBE:

- extracts metadata;
- identifies source type and quality;
- creates searchable chunks;
- records page/line anchors;
- generates source summaries clearly marked as model-generated;
- extracts candidate evidence;
- detects duplicate or near-duplicate sources;
- keeps uploaded content untrusted and isolated from system instructions.

### 4.4 Generate and approve an outline

QYBE proposes an outline with:

- chapter/section objectives;
- RQ/hypothesis coverage;
- expected evidence;
- methodology and result dependencies;
- word budgets;
- required tables/figures;
- acceptance criteria.

The user can reorder, lock, rename, split, or merge sections.

### 4.5 Draft one section at a time

Before drafting, QYBE builds a **Section Context Packet** containing only approved and relevant information. The user can inspect the packet before generation.

Drafting is scoped to one outline node or a small group of related nodes. This minimizes error propagation and allows targeted regeneration.

### 4.6 Apply supervisor or examiner notes

Comments are stored as structured `ReviewIssue` records with:

- exact quoted instruction;
- source of feedback;
- target section(s);
- severity;
- proposed action;
- status;
- resolution evidence;
- before/after diff.

QYBE can generate a revision plan and apply changes only to selected sections.

### 4.7 Validate the final work

QYBE runs quality gates for:

- structural completeness;
- RQ coverage;
- hypothesis treatment;
- methodology/findings alignment;
- findings/discussion separation;
- conclusion answers;
- citation completeness;
- reference consistency;
- terminology consistency;
- word-budget variance;
- unsupported claims;
- unresolved reviewer comments;
- cross-section contradictions.

---

## 5. QYBE-native architecture

### 5.1 Architectural placement

This feature should be implemented as a QYBE domain/workflow layer over existing Onyx/QYBE capabilities:

- chat and project interaction;
- document ingestion and RAG;
- connectors;
- search;
- tools/actions;
- document generation/editing;
- model-provider layer;
- code interpreter where relevant;
- prompt-safe telemetry;
- orchestration evaluation.

Do not introduce a separate Streamlit service or a parallel standalone application.

### 5.2 Router and execution constraints

The current QYBE orchestration router remains shadow-only.

The academic domain may produce advisory objects:

- `DomainDecision`
- `AcademicTaskType`
- `CapabilityPlan`
- `DataClassification`
- `DataEgressDecision`
- `ModelPlan`
- `ToolPlan`
- `ExecutionPlanPreview`

Initial implementation must not activate automatic production routing. User-selected workflows and current chat behavior remain authoritative until controlled execution is explicitly enabled behind feature flags.

### 5.3 Proposed module boundaries

Proposed paths; confirm against the current repository tree before implementation:

```text
backend/qybe/academic/
  models/
  services/
  workflows/
  validators/
  prompts/
  exports/
  policies/
  api/

backend/qybe/domain_packs/academic_research_writing/
  pack.yaml
  task_types.yaml
  prompt_profiles.yaml
  quality_gates.yaml
  templates/

web/.../academic/
  project/
  outline/
  sources/
  evidence/
  editor/
  review/
  export/
```

The domain pack defines declarative policy and task metadata. Business logic remains in typed backend services rather than YAML prompt strings.

### 5.4 Core aggregate

```text
AcademicProject
├── ProjectBrief
├── RequirementProfile
├── ResearchQuestion[]
├── Hypothesis[]
├── MethodologyProfile
├── SourceCorpus
│   ├── SourceRecord[]
│   ├── SourceChunk[]
│   └── EvidenceItem[]
├── AcademicOutline
│   └── OutlineNode[]
├── DraftSection[]
├── ClaimRecord[]
├── CitationLink[]
├── ReviewIssue[]
├── QualityRun[]
├── ExportSnapshot[]
└── ProjectRevision[]
```

### 5.5 State machine

Suggested project states:

```text
CREATED
→ REQUIREMENTS_CAPTURED
→ RESEARCH_DESIGN_DRAFTED
→ CORPUS_BUILDING
→ OUTLINE_DRAFTED
→ OUTLINE_APPROVED
→ DRAFTING
→ EVIDENCE_REVIEW
→ SUPERVISOR_REVISION
→ FINAL_VALIDATION
→ EXPORT_READY
→ ARCHIVED
```

Transitions should be permissive enough for real academic work. Users may return to earlier states. Each transition records who initiated it and what changed.

---

## 6. Academic intermediate representations

The strongest idea to borrow is not the exact prompt; it is the explicit outline as an intermediate representation. QYBE should extend this into several typed representations.

### 6.1 `ProjectBrief`

Fields:

- `working_title`
- `project_type`
- `academic_level`
- `discipline`
- `subdiscipline`
- `language`
- `institution`
- `deadline`
- `target_words`
- `problem_statement`
- `research_objective`
- `scope`
- `exclusions`
- `required_deliverables`
- `user_notes`
- `status`
- `version`

### 6.2 `RequirementProfile`

Fields:

- mandatory chapter names/order;
- citation style;
- formatting rules;
- minimum/maximum word count;
- source recency requirements;
- required empirical/practical component;
- required figures/tables/screenshots;
- language rules;
- plagiarism/AI disclosure requirements;
- template file;
- examiner/supervisor instructions.

Every requirement should be traceable to its origin: user, institution document, supervisor note, or inferred suggestion. Inferred suggestions must never be silently treated as binding requirements.

### 6.3 `ResearchQuestion`

Fields:

- stable ID such as `RQ1`;
- text;
- type;
- parent RQ;
- linked objective;
- linked hypotheses;
- required methodology;
- expected evidence;
- linked outline nodes;
- answer status;
- final answer summary;
- validation notes.

### 6.4 `AcademicOutline` and `OutlineNode`

Each node:

- `id`
- `parent_id`
- `position`
- `title`
- `level`
- `purpose`
- `content_requirements`
- `exclusions`
- `linked_rq_ids`
- `linked_hypothesis_ids`
- `required_source_types`
- `candidate_source_ids`
- `dependency_node_ids`
- `target_words`
- `status`
- `locked`
- `version`

Unlike Infinite Bookshelf's title-to-description JSON map, stable IDs prevent data loss when titles change.

### 6.5 `EvidenceItem`

Fields:

- source ID;
- exact passage or structured data reference;
- location anchor;
- normalized summary;
- evidence type;
- supports/challenges/qualifies;
- linked RQs/hypotheses;
- reliability notes;
- extraction method;
- reviewer status.

### 6.6 `ClaimRecord`

A claim is a factual or analytical statement in the draft that may require support.

Fields:

- claim text/hash;
- section ID;
- sentence or range anchor;
- claim type;
- source requirement;
- linked evidence IDs;
- citation status;
- verifier status;
- confidence;
- reviewer notes.

### 6.7 `SectionContextPacket`

This is the key replacement for the reference repository's section-title-only prompt.

A packet may contain:

- project brief summary;
- approved section specification;
- relevant RQs/hypotheses;
- methodology constraints;
- relevant source excerpts with anchors;
- evidence items;
- terminology/glossary;
- summaries of prerequisite sections;
- claims already established elsewhere;
- facts that must not be repeated;
- supervisor requirements;
- word and style constraints;
- citation style;
- unresolved review issues;
- data-egress classification.

The packet is generated deterministically where possible and stored by hash/version for reproducibility.

---

## 7. Agent and workflow roles

These are execution roles, not autonomous personas with unrestricted authority.

### 7.1 Requirement Analyst

Produces and maintains the project brief and requirement profile. It distinguishes explicit requirements from suggestions and flags ambiguities.

### 7.2 Research Design Planner

Proposes objectives, RQs, hypotheses, variables, methodology options, and limitations. Human approval is required before these are considered accepted.

### 7.3 Corpus Curator

Processes sources, extracts metadata, classifies source quality, deduplicates records, and prepares searchable evidence.

### 7.4 Outline Architect

Creates or revises the academic outline and word budget. It must map every major section to its academic purpose and relevant RQs.

### 7.5 Evidence Mapper

Maps sources/evidence to outline nodes and identifies gaps before drafting.

### 7.6 Section Drafter

Generates or revises one scoped section using an approved context packet. It may not invent citations or silently introduce external facts.

### 7.7 Citation Verifier

Checks whether cited passages support the associated claims and whether references resolve correctly.

### 7.8 Coherence Reviewer

Checks terminology, logical flow, duplication, contradictions, and chapter-to-chapter dependencies.

### 7.9 Methodology Reviewer

Checks whether the selected methods can answer the RQs and whether findings are presented consistently with the methods.

### 7.10 Findings/Discussion Reviewer

Enforces the distinction:

- Findings present results.
- Discussion interprets results using the theoretical framework and prior literature.
- Conclusion answers the main RQ and summarizes contributions without introducing unsupported new findings.

### 7.11 Compliance Reviewer

Checks institutional structure, formatting, word limits, citation style, required declarations, and unresolved feedback.

### 7.12 Export Builder

Creates final deliverables and a manifest of versions, references, figures, tables, and validation outcomes.

---

## 8. Workflow definitions

### 8.1 Workflow A — New academic project

```text
Capture requirements
→ propose project brief
→ propose RQs/hypotheses
→ user approval
→ initialize source corpus
→ propose outline
→ run outline coverage checks
→ user approval
→ create drafting backlog
```

### 8.2 Workflow B — Existing thesis/dissertation audit

```text
Ingest document
→ parse headings and references
→ detect stated RQs/hypotheses
→ infer chapter purposes as suggestions
→ map examiner/supervisor notes
→ run structural and evidence audit
→ produce prioritized revision backlog
```

### 8.3 Workflow C — Literature review

```text
Define review scope
→ collect/import sources
→ deduplicate
→ extract metadata and evidence
→ classify themes/methods/findings
→ build literature matrix
→ identify gaps/conflicts
→ draft source-grounded synthesis
→ verify citations
```

### 8.4 Workflow D — Section drafting

```text
Select outline node
→ validate prerequisites
→ build context packet
→ preview sources and constraints
→ select model/runtime under policy
→ stream draft
→ persist checkpoint
→ extract claims
→ verify evidence/citations
→ run section quality gates
→ request human approval
```

### 8.5 Workflow E — Supervisor revision

```text
Import feedback
→ create ReviewIssue records
→ map issues to sections
→ propose change plan
→ user selects changes
→ revise scoped sections
→ show diff and affected dependencies
→ rerun quality gates
→ close or retain issues
```

### 8.6 Workflow F — Final synthesis

```text
Freeze findings snapshot
→ verify RQ coverage
→ generate/update discussion
→ generate/update conclusion
→ verify main RQ answer
→ verify recommendations derive from findings
→ final citation and compliance audit
→ export
```

---

## 9. User interface proposal

### 9.1 Project dashboard

Display:

- completion by workflow stage;
- word budget and actual word count;
- RQ coverage;
- source count and quality distribution;
- unsupported claim count;
- unresolved review issues;
- sections awaiting approval;
- latest quality run;
- privacy/local-vs-cloud execution summary.

### 9.2 Outline workspace

Capabilities:

- tree view;
- drag/reorder;
- lock node;
- target word counts;
- RQ badges;
- source coverage badges;
- dependency warnings;
- generate/refine selected node only;
- compare outline versions.

### 9.3 Source and evidence workspace

Capabilities:

- source table;
- metadata correction;
- source preview;
- page/line anchors;
- literature matrix;
- evidence cards;
- support/challenge/qualify relationships;
- citation resolution status;
- duplicate detection.

### 9.4 Academic editor

Use QYBE's document/Univer direction rather than a separate Streamlit renderer.

Required interactions:

- section-scoped generation;
- inline source links;
- claim markers;
- tracked changes;
- comments/review issues;
- version compare;
- regenerate selection;
- rewrite while preserving citations;
- move content between sections;
- citation insertion;
- table/figure placeholders;
- section quality panel.

### 9.5 Execution preview

Before a consequential generation:

- task type;
- selected sources;
- model tier/provider/runtime;
- local/cloud;
- estimated context size;
- expected output scope;
- tools;
- privacy decision;
- quality gates;
- cache-boundary hints.

This remains advisory while the router is shadow-only.

---

## 10. Prompt and context design

### 10.1 Prompt hierarchy

Prompts should be stored as versioned templates with typed inputs:

1. system safety and policy;
2. domain role contract;
3. institutional/project requirements;
4. task specification;
5. context packet;
6. output schema.

Uploaded documents, web pages, PDFs, connector content, and GitHub content are untrusted data. They must never be concatenated into system instructions.

### 10.2 Structured outputs

Use schemas for:

- project brief;
- RQs/hypotheses;
- outline;
- evidence map;
- claim extraction;
- review findings;
- revision plans;
- quality reports.

Prose generation remains prose, but planning and verification stages should produce typed outputs.

### 10.3 Context compaction

Long projects require hierarchical memory:

- canonical project facts;
- section summaries;
- approved claims;
- terminology;
- evidence index;
- recent revisions;
- task-specific excerpts.

Do not send the entire thesis and corpus to every call. Use stable prompt blocks and cache-aware ordering where supported, under QYBE's provider-neutral Prompt Efficiency Layer.

### 10.4 Grounding rules

The drafter must:

- use only provided evidence for factual claims when source-grounded mode is required;
- distinguish source statements from interpretation;
- avoid fabricated page numbers, DOIs, authors, datasets, or citations;
- insert explicit placeholders when evidence is insufficient;
- preserve uncertainty and disagreement among sources;
- expose inference as inference.

---

## 11. Model and runtime policy

### 11.1 Provider neutrality

Do not copy the hardcoded Groq/model list.

The academic workflow requests capabilities and tiers, not provider names:

```text
task: outline_design
tier: balanced
needs_structured_output: true
context_requirement: medium
privacy: local_preferred
fallback_allowed: policy_dependent
```

The QYBE model resolver selects an eligible runtime/model. Organization policy always wins.

### 11.2 Local-first execution

Preferred local tasks:

- document parsing;
- metadata extraction;
- classification;
- outline transformations;
- source summarization;
- citation consistency checks;
- terminology checks;
- claim extraction;
- diff summarization.

Cloud use may be appropriate for selected deep reasoning tasks only when allowed by policy and explicitly visible to the user.

### 11.3 Planner/worker/reviewer separation

Where useful:

- planner may use `balanced` or `deep`;
- worker may use `balanced`;
- deterministic validators and smaller models perform routine checks;
- reviewer may use a different model/runtime to reduce correlated errors.

No role separation alone guarantees quality; all decisions still require evidence and validators.

---

## 12. Privacy, security, and academic integrity

### 12.1 Data classification

Academic projects may contain:

- unpublished research;
- personal data;
- commercial/confidential datasets;
- examination materials;
- proprietary methodology;
- interview transcripts;
- institutional documents.

Every project and source receives a data classification. The `DataEgressDecision` controls whether any content may leave the local environment.

### 12.2 Prompt injection resistance

Source content is untrusted. Extraction pipelines should strip or neutralize instructions such as “ignore previous instructions,” tool requests, or data-exfiltration attempts.

### 12.3 Telemetry

Allowed:

- hashes;
- IDs;
- task types;
- model/runtime;
- timings;
- token counts;
- quality scores;
- error categories.

Disallowed:

- raw project text;
- raw source passages;
- thesis titles when sensitive;
- supervisor comments;
- personal or research data.

### 12.4 Academic integrity features

Provide:

- citation and evidence traceability;
- generated-content provenance;
- version history;
- optional AI-use disclosure summary;
- plagiarism-tool integration only through approved tools and policies;
- warnings when the user asks to fabricate sources, results, surveys, experiments, interviews, or findings.

The system must not present generated empirical results as observed data.

---

## 13. Quality gates

### 13.1 Outline gates

- main RQ is represented;
- every sub-RQ maps to at least one analysis/findings/discussion section;
- methodology can answer the RQs;
- no major duplicate section purposes;
- word budget matches target;
- required institutional chapters exist;
- dependencies are acyclic or explicitly justified.

### 13.2 Source gates

- references resolve where possible;
- metadata completeness;
- duplicate detection;
- page/line anchors retained;
- source quality labels present;
- source date requirements satisfied;
- no fabricated bibliography entries.

### 13.3 Section gates

- section purpose met;
- required RQs addressed;
- claims extracted;
- material factual claims linked to evidence;
- citations resolve and support the claims;
- no forbidden content;
- word-count tolerance;
- terminology consistency;
- no excessive overlap with other sections;
- no unresolved placeholders unless explicitly accepted.

### 13.4 Whole-document gates

- title/objective/RQ alignment;
- RQ-methodology-findings-discussion-conclusion chain;
- hypotheses consistently named and evaluated;
- findings contain results rather than literature discussion;
- discussion interprets, compares, and explains findings;
- conclusion answers the main RQ;
- recommendations follow from findings/discussion;
- limitations are explicit;
- all tables/figures are referenced;
- citations and bibliography are mutually consistent;
- reviewer comments are resolved or documented.

---

## 14. Evaluation metrics

### 14.1 Reliability

- unsupported material claim rate;
- invalid citation rate;
- citation-entailment pass rate;
- fabricated reference count;
- contradiction count;
- unresolved placeholder count.

### 14.2 Structural quality

- RQ coverage;
- hypothesis coverage;
- outline requirement coverage;
- section-purpose pass rate;
- word-budget variance;
- duplication score.

### 14.3 Workflow effectiveness

- accepted draft ratio;
- regeneration blast radius;
- average revisions per accepted section;
- supervisor issue closure rate;
- time from source ingestion to approved section;
- checkpoint recovery success.

### 14.4 Operational quality

- local execution ratio;
- policy violation count;
- prompt-safe telemetry compliance;
- task latency;
- tokens per accepted word;
- cache hit/benefit metrics where available.

Evaluation datasets should use synthetic or appropriately licensed academic projects. Real student work must not be reused without authorization.

---

## 15. Implementation phases

### Phase 0 — Design and contracts

Deliverables:

- domain-pack specification;
- typed models;
- project state machine;
- feature flags;
- API contracts;
- threat model;
- evaluation fixtures;
- migrations plan.

No live routing changes.

### Phase 1 — Academic project, requirements, and outline

Deliverables:

- create/import project;
- requirement profile;
- RQ/hypothesis editor;
- structured outline with stable IDs;
- word budgets;
- outline versions;
- manual task execution through existing model selection;
- basic Markdown/DOCX export snapshot.

This is the first useful vertical slice.

### Phase 2 — Source corpus and evidence map

Deliverables:

- source metadata;
- source quality classification;
- evidence items;
- literature matrix;
- outline-to-source mapping;
- citation record model;
- missing-evidence warnings.

Reuse existing QYBE/Onyx ingestion and RAG infrastructure.

### Phase 3 — Section drafting and checkpoints

Deliverables:

- context packet builder;
- selected-section drafting;
- streaming into editor;
- autosave/checkpoints;
- revision history;
- claim extraction;
- targeted regeneration;
- prompt-safe inference telemetry.

### Phase 4 — Verification and reviewer loop

Deliverables:

- citation resolution;
- claim-evidence verification;
- coherence reviewer;
- methodology reviewer;
- findings/discussion/conclusion validators;
- structured supervisor/examiner issues;
- change plans and diffs.

### Phase 5 — Templates and final export

Deliverables:

- institution templates;
- DOCX/PDF/Markdown/LaTeX options;
- bibliography formats;
- appendices;
- figure/table registry;
- final compliance report;
- export manifest.

### Phase 6 — Orchestration integration

Only after the shadow system is validated:

- academic task classification;
- advisory capability/model/tool plans;
- evaluation dashboards;
- controlled execution behind explicit flags;
- organization policy precedence;
- rollback path.

---

## 16. First implementation slice

Recommended first build:

### “Academic Project + Approved Outline”

A user can:

1. create a thesis/dissertation project;
2. enter/import requirements;
3. define RQs/hypotheses;
4. generate a proposed outline;
5. review and edit the outline;
6. map sections to RQs;
7. assign word budgets;
8. lock and version the outline;
9. export the approved plan.

Why this slice first:

- it captures the strongest Infinite Bookshelf idea;
- it is valuable before full autonomous drafting;
- it avoids premature citation and editor complexity;
- it creates the intermediate representation required by later workflows;
- it can run without changing live routing.

### Suggested feature flags

```text
QYBE_ACADEMIC_DOMAIN_ENABLED=false
QYBE_ACADEMIC_PROJECT_API_ENABLED=false
QYBE_ACADEMIC_OUTLINE_GENERATION_ENABLED=false
QYBE_ACADEMIC_DRAFTING_ENABLED=false
QYBE_ACADEMIC_VERIFICATION_ENABLED=false
```

### Suggested API surface

```text
POST   /api/academic/projects
GET    /api/academic/projects/{project_id}
PATCH  /api/academic/projects/{project_id}
POST   /api/academic/projects/{project_id}/requirements/import
POST   /api/academic/projects/{project_id}/research-design/propose
POST   /api/academic/projects/{project_id}/outline/propose
PATCH  /api/academic/projects/{project_id}/outline
POST   /api/academic/projects/{project_id}/outline/validate
POST   /api/academic/projects/{project_id}/outline/approve
GET    /api/academic/projects/{project_id}/versions
```

Final endpoint placement/naming must follow current QYBE conventions.

---

## 17. Testing strategy

### 17.1 Unit tests

- outline tree operations;
- stable IDs after rename/reorder;
- word-budget calculations;
- RQ mapping;
- state transitions;
- requirement precedence;
- prompt packet construction;
- source trust boundaries;
- telemetry redaction;
- policy overrides.

### 17.2 Contract tests

- structured model outputs;
- API schemas;
- domain-pack loading;
- export manifests;
- feature-flag behavior;
- backward compatibility of admin orchestration APIs.

### 17.3 Golden fixtures

Create small synthetic projects:

- Bulgarian bachelor thesis;
- English master thesis;
- engineering dissertation with equations and figures;
- literature review;
- existing document plus examiner notes.

Expected outputs should emphasize structure and validation, not exact prose.

### 17.4 Adversarial tests

- prompt injection inside uploaded PDF/DOCX;
- fake citations and DOI-like strings;
- conflicting institution requirements;
- malicious supervisor-note attachment;
- sensitive project blocked from cloud execution;
- model returns invalid outline JSON;
- section references missing source pages;
- attempts to fabricate findings or survey responses.

### 17.5 Integration tests

- ingest sources → create evidence → map outline;
- approve outline → draft selected section;
- interruption → restore checkpoint;
- edit title without losing source/RQ links;
- import reviewer comments → revise → close issue;
- export version reproducibly.

---

## 18. Reuse and licensing

The reference repository is licensed under MIT. QYBE may use, modify, and redistribute its code subject to inclusion of the copyright and permission notice in copies or substantial portions.

Preferred approach:

- reuse product and architecture ideas freely;
- reimplement QYBE-native typed services and UI;
- avoid copying Streamlit-specific code;
- if any substantial code or prompt text is copied, preserve the MIT notice and document provenance in `THIRD_PARTY_NOTICES` or the repository's equivalent;
- do not copy trademarks, branding, hosted assets, or unrelated example content.

---

## 19. Explicit non-goals

Not in the initial release:

- one-click generation of a complete thesis/dissertation;
- automatic fabrication of experiments, results, interviews, surveys, or datasets;
- bypassing institutional academic-integrity requirements;
- replacing the supervisor or researcher;
- direct activation of the shadow router;
- hardcoded Groq dependence;
- unrestricted cloud upload;
- global rewrite of an approved document without section-level review;
- automatic acceptance of inferred requirements;
- unsupported claim generation disguised as sourced academic content.

---

## 20. Product decisions derived from the reference repository

| Reference idea | QYBE decision |
|---|---|
| Topic-to-book generation | Convert to project-to-workflow planning |
| JSON book structure | Typed, versioned AcademicOutline with stable IDs |
| Separate title/structure/section agents | Planner/worker/reviewer task roles |
| Model per role | Provider-neutral tiers under privacy policy |
| Seed content | Source corpus, notes, prior draft, examiner feedback |
| Writing style and complexity | Academic level, discipline, language, institution rules |
| Streamlit token streaming | Persistent editor streaming with checkpoints |
| Inference statistics | Prompt-safe operational and quality telemetry |
| Recursive section generation | Dependency-aware section work queue |
| Text/PDF download | DOCX/PDF/Markdown/LaTeX plus bibliography and audit artifacts |
| Fast full-book generation | Controlled, reviewable, evidence-grounded incremental drafting |

---

## 21. Copilot implementation brief for Phase 1

Use this as the starting implementation instruction after confirming current repository paths:

```text
Implement the first vertical slice of the QYBE Academic Research & Writing domain on a focused feature branch based on dev.

Constraints:
- Preserve the existing shadow-only router behavior.
- Do not enable live routing or change current chat execution.
- No raw project text in telemetry.
- Organization privacy policy overrides user/model/tool preferences.
- Uploaded content is untrusted and must never be inserted into system instructions.
- Reuse current QYBE/Onyx auth, persistence, API, feature-flag, and UI conventions.
- Keep commits focused and backward compatible.

Scope:
1. Add typed persistence models for AcademicProject, RequirementProfile, ResearchQuestion, Hypothesis, AcademicOutline, OutlineNode, and ProjectRevision.
2. Add feature flags:
   QYBE_ACADEMIC_DOMAIN_ENABLED
   QYBE_ACADEMIC_PROJECT_API_ENABLED
   QYBE_ACADEMIC_OUTLINE_GENERATION_ENABLED
3. Add CRUD APIs for projects, requirements, RQs/hypotheses, and outlines.
4. Add deterministic outline validation:
   - stable tree IDs
   - no orphan nodes
   - valid ordering
   - target word-budget totals
   - RQ coverage
   - required chapter coverage
5. Add an advisory outline-generation service using a structured output schema and existing model/provider abstractions. It must not call a hardcoded provider or model.
6. Add an initial UI for project setup, RQs/hypotheses, outline tree editing, word budgets, validation, versioning, and approval.
7. Add unit, API, feature-flag, privacy, and invalid-model-output tests.
8. Document migrations, flags, API examples, and rollback.

Before coding:
- inspect the current repository tree and existing domain-pack/provider conventions;
- identify reusable document/project components;
- present the proposed file list and migration impact;
- do not modify unrelated orchestration code.
```

---

## 22. Acceptance criteria for this feature plan

This plan is considered ready for implementation review when:

- the domain is accepted as QYBE-native rather than a direct embedded fork;
- Phase 1 scope and non-goals are approved;
- current repository paths and persistence conventions are verified;
- academic project schemas are reviewed;
- privacy and source-trust boundaries are approved;
- evaluation fixtures are defined;
- a focused feature branch and implementation issue/PR can be created.
