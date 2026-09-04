# ⚠️ CyberHackerOS Constraints & Guardrails

CyberHackerOS and its integrated Dataset Factory engine must strictly adhere to the following constraints to ensure secure local execution, strict AI guardrails, and optimal performance.

## 🖥️ 1. Strict Hardware Limitations (8GB VRAM Budget)

- **No Model Co-residency**: Because ColPali/ColQwen2 in bf16 occupies 5–7 GB of VRAM, models _cannot_ stay loaded simultaneously.
- **GPU Scheduler Required**: The system must load a model, process a batch, unload it, and load the next model (e.g., ColPali phase → unload → Generation phase).
- **Quantization**: Int8 quantized weights should be the default configuration to leave headroom for image preprocessing.
- **CPU Fallback**: The system must gracefully fall back to CPU for tasks that cannot fit into VRAM (e.g., OCR).

## 🔒 2. Privacy & Local Operation

- **Zero Cloud APIs**: No book content, page images, or embeddings should leave the machine. The system must operate fully offline.
- **Open-Weights**: Models should be locally downloadable and open-weight where licensing permits.

## 🏗️ 3. Architectural Directives

- **Visual Path is First-Class**: Do NOT build a linear text pipeline that simply chunks PDFs. Every page is treated as a visual object first. ColPali is core infrastructure, not an optional RAG add-on.
- **Canonical Dataset Independence**: The canonical dataset must be _model-agnostic_. It must not be intrinsically tied to Qwen, Llama, or Gemma. Adapters will translate the canonical data to specific model formats.
- **Aggressive Caching**: Every expensive operation (page images, embeddings, OCR) must be cached and keyed by `page_hash`. Restarting a pipeline must resume from the exact last completed stage.

## 📊 4. Dataset Quality & Verification

- **Visual Grounding**: Examples generated from layout-heavy pages must be verified by comparing the LLM's claims against the ColPali embedding of the source page.
- **Deduplication**: Must prevent redundant training examples across editions/reprints. Deduplication requires exact hashing, semantic clustering, AND ColPali visual embeddings to catch layout near-duplicates.
- **Decision Over Memorization**: The pipeline focuses on _decision-making and tool/technique selection_, not simple memorization of shell commands.

## 👑 5. Agent Permissions & Guardrails

- **Strict OS-Level Guardrails**: While the integrated AI agent runs natively within the custom **Kali Linux** base OS and can be granted root access, it operates under strict, non-negotiable guardrails.
- **Sandboxed Tool Calling**: Agentic tool calls (via LangGraph/LangChain) execute inside sandboxed contexts that enforce network and filesystem boundaries.
- **Human-in-the-Loop for Destructive Actions**: Destructive actions (e.g., file deletion, payload deployment) require explicit human confirmation. The system is designed strictly for authorized CTF labs, research, and systems the user has legal permission to test.
