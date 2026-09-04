# Product Requirements Document — CyberHackerOS & Dataset Factory

**Version:** 0.2 (ColPali integrated as a first-class ingestion component)
**Status:** Draft

---

## 1. Product Overview

Build **CyberHackerOS**, a custom **AI Operating System** based on the latest **Kali Linux**, featuring a modified boot screen, minor UI/UX refinements, and native integration of agentic tool calls as core OS services. The system features agentic systems, tool calls, and pipelines created with LangGraph, LangChain, etc., integrated into the OS with strict guardrails.

To power the intelligence of this OS, the project includes a **fully local, automated cybersecurity knowledge and training-data factory** that ingests a large collection of cybersecurity, hacking, penetration-testing, networking, Linux, Windows, cloud-security, and related textbooks and transforms them into:

1. A **master multimodal knowledge corpus**.
2. A **model-agnostic cybersecurity decision dataset**.
3. A **Qwen2.5-ready fine-tuning dataset**.
4. A reusable **future-model adapter pipeline**.
5. A high-quality **evaluation/benchmark dataset**.
6. A **layout-aware visual retrieval index** (ColPali/ColQwen2), treated as core infrastructure rather than an optional add-on.
7. An **Adaptive Companion AI Identity**: The OS uses Reinforcement Learning (RL) to learn user preferences and grow with interactions over time. It maintains a persistent companion identity whose "brain" (the underlying LLM) can be swapped (via API or raw local weights) to scale raw intelligence, without losing its personalized understanding of the user.
   The system must preserve the relationship between:

> **Situation → Goal → Constraints → Evidence → Decision → Technique → Tool → Action → Observation → Interpretation → Next Decision**

The primary purpose of fine-tuning is **decision-making and tool/technique selection**, not simple memorization of commands.

Many source books encode meaning in the _spatial relationship_ between diagrams, tables, captions, and body text (e.g., a network topology diagram annotated with attack paths, a permissions table with footnoted exceptions, a multi-column layout where a screenshot is explained two columns away). Flattening pages to linear text loses this. The system is therefore designed so that **every page is treated as a visual object first, a text object second** — text extraction and visual (ColPali) indexing run as parallel, independent paths off the same page render, not a sequential fallback.

The system must be designed for **authorized cybersecurity education, CTFs, labs, defensive research, and systems the user has permission to test**.

---

## 2. Core Product Goal

The finished system should allow the user to place books into:

```text
/input/books/
```

and eventually produce:

```text
/output/
├── master/
├── visual_index/
├── canonical/
├── qwen25/
└── evaluation/
```

with minimal manual intervention.

The system should transform potentially hundreds of thousands of pages into structured knowledge, a layout-aware visual index, and high-quality training examples.

---

## 3. Core Design Principle

### Do NOT build:

```text
PDF
 ↓
chunks
 ↓
Q&A
 ↓
fine-tune
```

### Do NOT build (the "ColPali as afterthought" version either):

```text
Text pipeline (primary)
 ↓
...
 ↓
RAG index
 ↓
   (optionally) also embed pages with ColPali for retrieval
```

### Build:

```text
Books
 ↓
Page rendering (universal, always produced)
 ↓
   ┌───────────────┬────────────────────┐
   ▼                                    ▼
Visual path                        Text path
(ColPali/ColQwen2                  (Document understanding,
 multi-vector embed,                OCR, layout, table,
 layout-significance                equation, code detection)
 scoring)
   │                                    │
   └───────────────┬────────────────────┘
                    ▼
         Master knowledge representation
                    ↓
              Knowledge atoms
                    ↓
             Scenario generation
                    ↓
             Decision generation
                    ↓
           Branching trajectories
                    ↓
                Verification
        (incl. visual grounding check
         against ColPali page embedding)
                    ↓
               Deduplication
        (incl. visual near-duplicate
         detection via ColPali)
                    ↓
              Quality filtering
                    ↓
      Canonical model-independent dataset
                    ↓
             Model-specific formatter
                    ↓
                Qwen2.5 / other LLM
```

ColPali is not bolted onto the RAG step at the end — it is generated during ingestion for every page, and it feeds routing, retrieval, verification, and deduplication throughout the pipeline.

---

## 4. Target Hardware

Primary target:

- NVIDIA RTX 5060
- 8 GB VRAM
- Intel i7-14700HX
- Local Windows/Linux environment
- No mandatory cloud APIs
- Models should be locally downloadable/open-weight where licensing permits.

The system must gracefully fall back to CPU for tasks that cannot fit into VRAM.

**ColPali-specific hardware note:** ColPali (PaliGemma-3B backbone) or ColQwen2 (Qwen2-VL-2B backbone) in bf16 occupies roughly 5–7 GB of VRAM on its own. On an 8 GB card this model cannot be co-resident with generation, critic, or embedding models. It must run as an isolated, scheduled phase (see Section 40, GPU Scheduler) — loaded, run over a full batch of rendered pages, then unloaded before the next stage begins. Quantized (int8) weights should be the default configuration to leave headroom for the image preprocessor and reduce OOM risk during long batch runs.

---

## 5. Functional Requirements

### FR-01 — Book ingestion

The system shall accept:

- PDF
- EPUB where supported
- scanned PDFs
- image-heavy PDFs
- textbook chapters
- supplementary documents

Each document must receive a unique:

```text
book_id
document_id
```

The original files must never be modified.

### FR-02 — Universal page rendering

Every page of every ingested document — regardless of whether it has a selectable text layer — shall be rendered to a standardized image format (PNG or WebP) at a consistent DPI (recommended: 200 DPI baseline, configurable). This render is a mandatory artifact, not a fallback triggered by missing text. It is the input to the visual (ColPali) path and the OCR fallback path alike.

### FR-03 — Visual indexing

Every rendered page shall be embedded with a ColPali-family model immediately after rendering, independent of whether text/OCR extraction has completed or succeeded for that page.

### FR-04 — Layout-significance scoring

Every page shall receive a `layout_significance` score used to route it to either standard text-based knowledge-atom extraction or full-page VLM-based extraction (see Section 12).

---

## 6. Document Processing Pipeline

```text
PDF
 │
 ├── page rendering (image, always produced)
 ├── metadata extraction
 ├── ColPali/ColQwen2 embedding (visual path, parallel)
 ├── layout-significance scoring
 ├── text extraction
 ├── image extraction
 ├── table detection
 ├── equation detection
 └── code/command detection
```

For each page preserve:

```json
{
  "book_id": "...",
  "page_number": 123,
  "chapter": "...",
  "section": "...",
  "raw_text": "...",
  "page_image_path": "...",
  "colpali_embedding_id": "...",
  "layout_significance": 0.0,
  "images": [],
  "tables": [],
  "equations": [],
  "code_blocks": []
}
```

---

## 7. Layout-Aware Extraction

The system must understand that:

```text
heading
paragraph
paragraph
figure
caption
paragraph
table
paragraph
```

is different from a flat text stream.

It must preserve document relationships both structurally (via layout-detection metadata) and visually (via the ColPali embedding of the full page, which implicitly encodes spatial arrangement through its patch-grid representation). The two representations are complementary: layout detection gives you explicit, addressable structure; ColPali gives you a retrievable, holistic representation that survives cases where explicit layout parsing fails or is ambiguous (rotated tables, overlapping annotations, hand-drawn diagram callouts).

Recommended implementation:

- Docling
- PDF extraction libraries
- OCR fallback
- layout detection
- ColPali / ColQwen2 for holistic page representation
- local vision model (VLM) for pages flagged high-layout-significance

---

## 8. OCR Pipeline

OCR should operate only where required for the **text path**. It is never a prerequisite for the **visual path** — ColPali embeds the rendered page image directly and does not depend on OCR succeeding.

Priority (text path):

```text
Selectable PDF text
       ↓
Use original text
```

If text isn't available:

```text
Page image
 ↓
OCR
 ↓
Structured text
```

The system should record:

```json
{
  "ocr_used": true,
  "ocr_engine": "...",
  "confidence": 0.96
}
```

Low-confidence OCR should be flagged for reprocessing. Pages with low OCR confidence should additionally be flagged as candidates for full-page VLM extraction (Section 12), since the visual path can often recover meaning the text path lost.

---

## 9. Image Understanding Pipeline

Images must NOT be discarded.

Classify images into:

```text
diagram
flowchart
network architecture
screenshot
graph
table
equation
photograph
illustration
decorative
```

Only meaningful images should undergo expensive per-image vision processing (captioning, entity/relationship extraction). This is distinct from and in addition to the page-level ColPali embedding, which runs on every page unconditionally regardless of image classification — ColPali provides retrieval-time value even for pages whose individual images are later deemed low-value for deep captioning.

For useful images store:

```json
{
  "image_id": "...",
  "page": 123,
  "type": "network_diagram",
  "ocr": "...",
  "description": "...",
  "entities": [],
  "relationships": [],
  "source_bbox": []
}
```

The original image must also be retained.

---

## 10. Tables

Tables must be converted into structured data.

Example:

```text
table_001.json
```

containing:

```json
{
  "headers": [],
  "rows": [],
  "caption": "...",
  "page": 123
}
```

Tables should also receive searchable textual representations. Note: table structure that fails clean parsing (merged cells, footnoted exceptions, rotated headers) is exactly the case where the page-level ColPali embedding becomes the primary retrieval mechanism, since the visual path preserves the table's true layout even when structured extraction cannot.

---

## 11. Equations

Equations should retain:

1. Original image.
2. OCR representation.
3. LaTeX representation where possible.
4. Surrounding explanation.
5. Page reference.

---

## 12. Code and Command Extraction

Detect:

- shell commands
- PowerShell
- Python
- JavaScript
- SQL
- configuration snippets
- tool output
- command-line examples

Store separately:

```json
{
  "code_id": "...",
  "language": "bash",
  "content": "...",
  "purpose": "...",
  "surrounding_context": "...",
  "source": {}
}
```

For cybersecurity commands, also extract:

```text
tool
technique
purpose
prerequisites
expected output
interpretation
limitations
alternatives
```

---

## 13. Visual Complexity Routing (New — ColPali-Core Addition)

This stage decides, per page, whether knowledge-atom extraction should proceed via the **standard text path** or the **full-page VLM path**.

```text
Rendered page
      │
      ▼
Layout-significance scoring
(heuristics: image/table density, column count,
 OCR confidence, ColPali embedding entropy/
 dissimilarity from "plain text page" cluster)
      │
      ├── low significance → standard text-based
      │                       knowledge-atom extraction
      │                       (uses extracted text, tables, code blocks)
      │
      └── high significance → full-page VLM extraction
                                (VLM reads the rendered page image
                                 directly — e.g. Qwen2.5-VL — and
                                 produces knowledge atoms grounded
                                 in the actual visual layout, not
                                 a flattened text approximation)
```

Recommended heuristics for `layout_significance`:

- ratio of detected image/table bounding-box area to total page area
- presence of multi-column layout
- OCR confidence (low confidence → higher significance, since text extraction is less trustworthy)
- number of distinct layout blocks detected
- optionally, a cheap classifier trained on a small labeled sample of "text-heavy" vs "diagram/table-heavy" pages

High-significance pages are the ones where ColPali-based retrieval and VLM-based extraction matter most — this routing keeps the (expensive) VLM path reserved for pages that actually need it, protecting the 8 GB VRAM budget.

---

## 14. Master Knowledge Corpus

The master corpus is the **complete normalized representation of the books**.

It must be model-independent.

Structure:

```text
master/
├── books/
├── pages/
├── page_images/
├── sections/
├── chunks/
├── images/
├── tables/
├── equations/
├── code/
├── commands/
└── knowledge_atoms/
```

Nothing should be discarded merely because the current model cannot use it. Rendered page images are retained permanently — they are the input to the visual index and to any future, more capable VLM that may re-process the corpus without needing to re-render from source PDFs.

---

## 15. Visual Index (New — ColPali-Core Component)

A dedicated, first-class output of ingestion, not a downstream RAG artifact bolted on later.

```text
visual_index/
├── embeddings/          # multi-vector ColPali/ColQwen2 embeddings, one entry per page
├── qdrant_collection/    # Qdrant multi-vector collection (MaxSim scoring)
└── layout_significance/  # per-page routing scores
```

### 15.1 Model choice

**ColQwen2** (ColPali architecture on a Qwen2-VL backbone) is recommended over base ColPali (PaliGemma backbone) given that the downstream fine-tuning target is Qwen2.5 — sharing tokenizer/vision-encoder lineage reduces representational mismatch if any components are later reused or distilled.

### 15.2 Storage

ColPali-family models produce a **multi-vector** representation — one embedding vector per image patch (typically on the order of ~1000 patches × 128 dimensions per page), not a single pooled vector per page. At the scale of hundreds of thousands of pages this is storage-heavy. Requirements:

- Use **Qdrant's native multi-vector field type** with MaxSim (late-interaction) scoring as the comparator.
- Apply **binary quantization** to the patch vectors from day one — this is a well-supported Qdrant feature for ColPali-style embeddings and typically reduces storage by roughly an order of magnitude with acceptable recall loss. This should not be treated as a later optimization; budget for it in the initial schema.
- Retain a reference (`page_image_path`) alongside each embedding so retrieval results can be rendered back to the original page image for VLM re-reading or human review.

### 15.3 Indexing schedule

ColPali embedding is a scheduled, batched GPU phase (see Section 40) — it does not run inline, page-by-page, interleaved with other model calls. Typical flow: render a full book's pages → batch-embed with ColPali/ColQwen2 → unload the model → proceed to the next scheduled stage.

---

## 16. Knowledge Atom Extraction

The next pipeline converts source material into atomic concepts.

Examples:

```text
Technique
Tool
Vulnerability
Protocol
Attack concept
Defensive mechanism
Prerequisite
Indicator
Expected result
Failure condition
Mitigation
```

Each atom must retain source provenance, including a reference to its source page's visual embedding for later grounding checks.

Example:

```json
{
  "atom_id": "tech_000123",
  "type": "technique",
  "name": "...",
  "objective": "...",
  "prerequisites": [],
  "constraints": [],
  "tools": [],
  "expected_observations": [],
  "failure_conditions": [],
  "alternatives": [],
  "defensive_detection": [],
  "remediation": [],
  "sources": [],
  "source_page_image": "...",
  "extraction_path": "text | vlm"
}
```

The `extraction_path` field records whether this atom came from the standard text path or the full-page VLM path (Section 13), which is useful for later quality analysis (e.g., checking whether VLM-derived atoms have systematically different quality scores).

---

## 17. Canonical Dataset

This is the most important output.

It must **not be tied to Qwen, Llama, Gemma, etc.**

Directory:

```text
canonical/
├── knowledge/
├── decisions/
├── trajectories/
├── tool_usage/
├── multimodal/
├── negative_examples/
└── evaluations/
```

---

## 18. Decision Dataset Schema

Each decision example should contain:

```json
{
  "example_id": "...",

  "scenario": {
    "environment": "...",
    "objective": "...",
    "constraints": []
  },

  "state": {
    "known": [],
    "unknown": []
  },

  "evidence": [],

  "decision": {
    "technique": "...",
    "tool_category": "...",
    "selection_reason": []
  },

  "action": {
    "type": "tool_use",
    "tool": "...",
    "parameters": {}
  },

  "expected_observation": [],

  "interpretation": {},

  "alternatives": [],

  "next_actions": [],

  "sources": [],

  "visual_grounding": {
    "source_page_image": "...",
    "colpali_similarity_score": 0.0
  }
}
```

The `visual_grounding` block is new: it records the ColPali similarity between the generated example's embedded scenario text and its cited source page image, feeding directly into verification (Section 24).

---

## 19. Scenario Generation

A local LLM should generate scenarios from knowledge atoms.

For each technique generate different states:

```text
beginner
intermediate
advanced
ambiguous
insufficient information
failed attempt
unexpected result
alternative technique required
```

For atoms whose `extraction_path` is `vlm` (i.e., derived from a high-layout-significance page), the scenario generator should have access to the source page image, not just the extracted atom text, so it can reference visual details (e.g., "the diagram shows two subnets connected via a jump box") accurately rather than paraphrasing a possibly-lossy text description.

The generator must not simply create repetitive questions.

---

## 20. Positive Examples

Generate situations where the technique is appropriate.

```text
Situation
 ↓
Evidence
 ↓
Correct technique
 ↓
Reason
 ↓
Expected result
```

---

## 21. Negative Examples

Generate situations where a tempting technique is inappropriate.

Example structure:

```json
{
  "situation": "...",
  "candidate": "Technique A",
  "correct": false,
  "reason": "...",
  "better_choice": "Technique B"
}
```

This is critical for teaching tool selection.

---

## 22. Constraint-Aware Examples

Every scenario should optionally contain constraints such as:

```text
authorized lab
non-destructive
limited privileges
limited network access
specific operating system
specific objective
time constraint
no credential access
no persistence
no destructive actions
```

The model must learn that the same technique may be appropriate in one situation and inappropriate in another.

---

## 23. Branching Trajectories

Generate sequential decision examples.

```text
State 0
 ↓
Decision
 ↓
Action
 ↓
Observation
 ↓
State 1
 ├── Result A → Decision A
 ├── Result B → Decision B
 └── Result C → Decision C
```

Each branch becomes training data.

---

## 24. Verification (Including Visual Grounding)

Every generated example should be checked against source material.

Verification pipeline:

```text
Generated example
 ↓
Retrieve source passages (text path)
 ↓
Retrieve source page image via ColPali similarity search (visual path)
 ↓
Compare claims (text-level)
 ↓
Compare visual_grounding.colpali_similarity_score against threshold
 ↓
Technical critic
 ↓
Score
```

The visual grounding check is new: embed the generated example's scenario/decision text and compare it against the ColPali embedding of the page it claims as its source. A low similarity score is a signal that the LLM may have hallucinated structure that isn't actually present on the page (e.g., inventing a table relationship that doesn't exist), and the example is flagged for re-verification or quarantine.

Recommended scores:

```text
grounding
visual_grounding_score
technical_accuracy
decision_quality
scenario_quality
source_support
duplication_score
```

---

## 25. Deduplication (Including Visual Near-Duplicates)

Use:

- exact hashing
- normalized text comparison
- embedding similarity (text)
- semantic clustering
- **ColPali embedding similarity across pages** — catches near-identical page layouts across different editions, reprints, or duplicated appendices of the same book, which text-only deduplication can miss when OCR output differs slightly between copies

Do not allow hundreds of essentially identical questions, and do not allow the same underlying diagram/table (re-printed across editions) to generate redundant training examples under different surface text.

Prioritize **diversity of states and decisions**.

---

## 26. Dataset Quality Gates

An example should only reach the final training set if:

```text
source-supported = true
visual_grounding_score >= threshold (for vlm-path examples)
technical quality >= threshold
decision quality >= threshold
not duplicate
valid structure
valid source reference
```

Failed examples go to:

```text
quarantine/
```

rather than being immediately deleted.

---

## 27. Multimodal Dataset

For diagrams/screenshots:

```json
{
  "image": "...",
  "scenario": "...",
  "question": "...",
  "decision": "...",
  "interpretation": "...",
  "source": {},
  "colpali_embedding_id": "..."
}
```

Keep the original image. This dataset remains model-independent, and is the most direct downstream consumer of the visual index — the same page images and embeddings used for retrieval during ingestion become the multimodal training pairs here.

---

## 28. Synthetic Data Generation

Use local models to generate candidate examples.

Recommended architecture:

```text
Extraction model (text and/or VLM, per routing decision)
       ↓
Scenario generator
       ↓
Trajectory generator
       ↓
Critic model
       ↓
Verifier (incl. visual grounding via ColPali)
       ↓
Deduplicator (incl. visual near-dup detection via ColPali)
       ↓
Quality filter
```

Models can be swapped independently.

---

## 29. Tool Selection Dataset

Explicitly create:

```text
Situation
+
Evidence
+
Objective
+
Constraints
↓
Candidate tools
↓
Selected tool
↓
Why
↓
Expected result
```

The model should learn:

> Tool selection depends on state and objective.

Not:

> Tool X is always used for problem Y.

---

## 30. Command Selection

Commands should be secondary to technique selection.

Canonical structure:

```text
Objective
 ↓
Technique
 ↓
Tool
 ↓
Command/action
```

The system should preserve:

```text
command purpose
prerequisites
expected output
failure modes
safe/authorized context
```

---

## 31. Result Interpretation

Generate examples where the model receives output and must decide what it means.

```text
Tool output
 ↓
Interpretation
 ↓
Confidence
 ↓
Next action
```

Also create:

```text
misleading output
ambiguous output
incomplete output
unexpected output
```

This teaches the model not to blindly trust tool results.

---

## 32. Qwen2.5 Adapter

The canonical dataset must then be converted into Qwen2.5's chat format.

```text
canonical
   ↓
Qwen formatter
   ↓
messages[]
   ↓
train.jsonl
```

Example:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a cybersecurity assistant for authorized security research and education."
    },
    {
      "role": "user",
      "content": "Scenario: ...\nObjective: ...\nConstraints: ...\nEvidence: ..."
    },
    {
      "role": "assistant",
      "content": "Decision: ...\nReason: ...\nExpected observation: ...\nNext step: ..."
    }
  ]
}
```

The formatter must be configurable so another model can use the same canonical dataset. For multimodal examples derived from `vlm`-path atoms, the formatter should also support Qwen2.5-VL's image-message format so page images can be included directly in training turns where relevant.

---

## 33. Future Model Adapter System

Create:

```text
adapters/
├── qwen25/
├── llama/
├── gemma/
├── mistral/
└── custom/
```

Each adapter converts:

```text
canonical JSON
```

into the appropriate model's:

```text
chat template
SFT format
multimodal format
tool-use format
```

The canonical dataset — including the visual index references — never changes. A future adapter for a different VLM backbone can re-embed the same retained page images with a different visual encoder without reprocessing the source books.

---

## 34. Train/Validation/Test Split

Do NOT randomly split individual chunks.

Use **semantic/source-aware splitting**.

Example:

```text
80% training
10% validation
10% testing
```

But ensure related pages/scenarios from the same source don't leak across sets. This applies to visual near-duplicates as well — use ColPali similarity to confirm that visually near-identical pages (e.g., a diagram repeated in a summary chapter) don't end up split across train and test.

---

## 35. Evaluation Dataset

Create a dedicated benchmark:

```text
evaluation/
├── tool_selection/
├── technique_selection/
├── constraint_handling/
├── ambiguity/
├── result_interpretation/
├── branching/
├── multimodal/
├── visual_grounding/
└── cross_book/
```

Metrics should include:

- correct technique
- correct tool category
- constraint compliance
- correct rejection of inappropriate tools
- output interpretation
- next-action accuracy
- hallucination rate
- source grounding
- **visual grounding accuracy** — for multimodal/high-layout-significance examples, whether the model's stated reasoning is actually consistent with what's depicted in the source page image

---

## 36. RAG Integration (ColPali as Primary Retrieval Path)

The same master corpus and visual index populate the RAG system.

```text
Hybrid retrieval:

  ColPali/ColQwen2 multi-vector search (primary, layout-aware)
       +
  BM25 (secondary, lexical)
       +
  reranker (fuses both signals)
```

ColPali is the **primary** retrieval path for pages where structure matters — it retrieves the whole page as a visual unit, so a query can match content whose meaning depends on figure/table/text adjacency even when OCR degraded the underlying text. BM25/text-embedding retrieval remains valuable as a secondary signal, particularly for pages that are pure prose with no meaningful layout structure (where the overhead of visual retrieval adds little).

RAG provides exact source information. Fine-tuning teaches decision behavior. Therefore:

```text
Fine-tuning = HOW to reason/select

RAG = WHERE the authoritative information is
      (ColPali-first for layout-significant sources)
```

---

## 37. Data Versioning

Every dataset must have a version:

```text
dataset_v0.1
dataset_v0.2
dataset_v1.0
```

Each example gets:

```text
example_id
source_hash
generator_version
validator_version
dataset_version
colpali_model_version
```

`colpali_model_version` is tracked separately since the visual index may be re-embedded with a newer ColPali/ColQwen2 checkpoint without requiring the rest of the pipeline to re-run.

This allows reproducibility.

---

## 38. Recommended Project Architecture

```text
cyber-ai-data-factory/
│
├── input/
│   └── books/
│
├── pipeline/
│   ├── ingestion/
│   ├── rendering/            # universal page-image rendering
│   ├── visual_indexing/      # ColPali/ColQwen2 embedding
│   ├── layout_routing/       # layout-significance scoring & routing
│   ├── ocr/
│   ├── layout/
│   ├── image/
│   ├── table/
│   ├── equation/
│   ├── code/
│   ├── command/
│   ├── knowledge/
│   ├── scenario/
│   ├── trajectory/
│   ├── verification/         # incl. visual grounding checks
│   ├── deduplication/        # incl. visual near-dup detection
│   ├── evaluation/
│   └── formatters/
│
├── models/
│   ├── extraction/
│   ├── generation/
│   ├── vision/                # VLM for high-significance pages
│   ├── colpali/                # ColPali/ColQwen2 weights
│   └── critics/
│
├── data/
│   ├── master/
│   ├── visual_index/
│   ├── canonical/
│   ├── qwen25/
│   └── evaluation/
│
├── rag/
│   ├── qdrant/                # multi-vector collection for ColPali
│   └── bm25/
│
├── configs/
│
├── logs/
│
└── scripts/
```

---

## 39. Pipeline Orchestrator

The system should support:

```bash
ingest
render              # new: universal page-image rendering
index-visual         # new: ColPali/ColQwen2 batch embedding
route-layout          # new: layout-significance scoring & routing
extract
analyze
build-knowledge
generate-scenarios
generate-trajectories
verify               # incl. visual grounding
deduplicate           # incl. visual near-dup
build-dataset
build-qwen
evaluate
```

And ideally:

```bash
pipeline --book book.pdf
```

or:

```bash
pipeline --all
```

The pipeline should be resumable. If processing stops at 70%, restarting should continue from the last completed stage — including mid-way through a ColPali batch-embedding run, which should checkpoint per-page so a restart doesn't re-embed already-processed pages.

---

## 40. GPU Scheduler (Critical for 8GB VRAM)

Since you have 8 GB VRAM, the system must never assume that all models can stay loaded simultaneously — and ColPali/ColQwen2 makes this constraint tighter, not looser.

```text
load model
 ↓
process batch
 ↓
unload
 ↓
load next model
```

Recommended device/phase assignment:

```text
OCR              → CPU (or light GPU burst)
ColPali/ColQwen2 → GPU, isolated batch phase, int8 quantized
Embedding (text) → GPU
Generation       → GPU
VLM (routing)    → GPU, isolated batch phase
Verification     → GPU
```

Key rule: **ColPali indexing and VLM generation should not be co-resident.** Run the full-book visual indexing pass (render → embed → unload) as a discrete phase before any generation-stage models are loaded. This keeps peak VRAM usage bounded to one large vision model at a time.

Every expensive operation must be cached, keyed by page hash:

```text
page_hash
   ↓
already processed?
   ├── yes → reuse (including cached ColPali embedding)
   └── no  → process
```

This is essential when working with thousands of pages and local GPU inference — re-embedding a full library with ColPali is expensive enough that caching is not optional.

---

## 41. Caching

Every expensive operation must be cached, including:

- rendered page images (keyed by `page_hash`)
- ColPali/ColQwen2 embeddings (keyed by `page_hash` + `colpali_model_version`)
- OCR output
- knowledge atoms
- generated scenarios/trajectories

A change to the ColPali model version should invalidate only the visual-index cache, not the entire pipeline — text extraction, knowledge atoms, and generated examples remain valid and reusable.

---

## 42. Privacy / Local Operation

Default architecture:

```text
Internet
   X
   │
Local files
   ↓
Local models (incl. ColPali/ColQwen2)
   ↓
Local database (Qdrant, local instance)
```

No book content, page images, or embeddings should leave the machine unless the user explicitly enables an external service.

---

## 43. Expected Output

For each book:

```text
book_id/
├── pages/
├── page_images/
├── colpali_embeddings/
├── images/
├── tables/
├── equations/
├── commands/
├── knowledge_atoms/
└── metadata.json
```

Then globally:

```text
canonical/
├── knowledge.jsonl
├── decisions.jsonl
├── trajectories.jsonl
├── multimodal.jsonl
├── negative_examples.jsonl
└── evaluations.jsonl
```

And:

```text
qwen25/
├── train.jsonl
├── validation.jsonl
├── test.jsonl
└── images/
```

And:

```text
visual_index/
├── qdrant_collection/
└── layout_significance_scores.jsonl
```

---

## 44. Final End-to-End Architecture

```text
                         ┌───────────────────┐
                         │ CYBERSECURITY     │
                         │ BOOK COLLECTION    │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │ UNIVERSAL PAGE    │
                         │    RENDERING       │
                         └─────────┬─────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
         ┌───────────────────┐          ┌───────────────────┐
         │  VISUAL PATH       │          │   TEXT PATH        │
         │  ColPali/ColQwen2  │          │  OCR / layout /    │
         │  embedding +       │          │  tables / equations │
         │  layout-significance│         │  / code             │
         │  routing            │          │                     │
         └─────────┬─────────┘          └─────────┬─────────┘
                    │                              │
          high sig. │                              │
                    ▼                              │
         ┌───────────────────┐                     │
         │  FULL-PAGE VLM     │                     │
         │  EXTRACTION         │                     │
         └─────────┬─────────┘                     │
                    │                              │
                    └──────────────┬───────────────┘
                                   ▼
                         ┌───────────────────┐
                         │ MASTER KNOWLEDGE  │
                         │      CORPUS       │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │ KNOWLEDGE ATOMS   │
                         └─────────┬─────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
                SCENARIOS      DECISIONS      TRAJECTORIES
                    │              │              │
                    └──────────────┼──────────────┘
                                   ▼
                         ┌───────────────────┐
                         │ QUALITY / SOURCE  │
                         │ + VISUAL GROUNDING │
                         │    VERIFICATION   │
                         └─────────┬─────────┘
                                   ▼
                         ┌───────────────────┐
                         │ DEDUPLICATION &   │
                         │ (incl. visual)     │
                         │    DIVERSITY      │
                         └─────────┬─────────┘
                                   ▼
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
          ┌──────────────────┐          ┌──────────────────┐
          │ MODEL-AGNOSTIC   │          │   RAG CORPUS      │
          │ CANONICAL DATA   │          │  ColPali-first +  │
          │                  │          │  BM25 + reranker  │
          └────────┬─────────┘          └──────────────────┘
                   │
        ┌──────────┼───────────┐
        ▼          ▼           ▼
     Qwen2.5     Llama      Future LLM
     Adapter     Adapter      Adapter
        │          │           │
        ▼          ▼           ▼
       SFT        SFT         SFT
```

---

## 45. Most Important Design Rule

The **canonical dataset is the product**. The **visual index is core infrastructure, not an optional retrieval enhancement**.

Qwen2.5 is merely the first consumer of the canonical dataset. ColPali/ColQwen2 is the primary lens through which layout-significant pages are found, routed, and verified — not a feature added after the fact to improve search relevance.

Your long-term pipeline should therefore preserve the full relationship:

**Source → Page Render → Visual Embedding → Knowledge → Situation → Constraint → Evidence → Decision → Tool → Action → Observation → Interpretation → Next Decision**

That structure lets you later train:

- a standard SFT model,
- a tool-use model,
- an agent (where agentic systems, tool calls, and pipelines are built with LangGraph, LangChain, etc., and integrated into the OS with strict guardrails),
- a multimodal model,
- a preference/DPO model,
- or a completely different LLM,

without going back and reprocessing all your books — and without re-rendering pages or re-running OCR, since the visual index and page images are retained as permanent, model-independent artifacts.

And the RAG system remains alongside it so that the resulting model can make decisions **while still grounding technical details in the original books and page-level sources — including cases where that grounding depends on diagram, table, and layout structure that a text-only pipeline would have lost.**
