<div align="center">

# ☠️ CyberHacker Suite

**An AI-Native Extension Suite for Kali Linux, Integrated with LLMs & Strict Guardrails**

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Base OS](https://img.shields.io/badge/Base%20OS-Kali%20Linux%20Rolling-557C94?logo=kalilinux&logoColor=white)](https://www.kali.org/)
[![LLMs](https://img.shields.io/badge/LLM-Qwen2.5%20%7C%20ColQwen2-blueviolet)](techstack.md)
[![Privacy](https://img.shields.io/badge/Execution-100%25%20Local-success)](constraints.md)
[![VRAM](https://img.shields.io/badge/VRAM-8GB%20Optimized-orange)](constraints.md)
[![Guardrails](https://img.shields.io/badge/Guardrails-Strict%20%E2%9C%94-critical)](constraints.md)

</div>

---

## 📖 What is the CyberHacker Suite?

**CyberHacker** is a custom AI-native extension suite that integrates directly into any existing **Kali Linux** environment. It is not a custom OS image or a standalone distribution. Instead, it is a deeply integrated platform where **Large Language Models (LLMs)** and **agentic AI pipelines** act as first-class citizens alongside your existing Kali tools.

LLMs and vision-language models are integrated into the Kali Linux core and exposed as native OS services. Every AI agent that has access to OS-level capabilities operates under **strict, non-negotiable guardrails** — preventing unauthorized actions, data exfiltration, and destructive commands unless explicitly permitted in a controlled, authorized lab environment.

> **Designed for:** Authorized cybersecurity research, penetration testing labs, CTF practice, defensive tooling, and AI-augmented red/blue team operations.

---

## 🧠 LLM & AI Integration

CyberHacker embeds AI into your system through the following stack:

| Layer                 | Technology               | Role                                                   |
| :-------------------- | :----------------------- | :----------------------------------------------------- |
| **Primary Text LLM**  | `Qwen2.5-7B-Instruct`    | Decision-making, scenario reasoning, knowledge Q&A     |
| **Primary VLM**       | `Qwen2.5-VL-7B-Instruct` | Full-page visual extraction, diagram understanding     |
| **Visual Indexer**    | `ColQwen2 / ColPali`     | Layout-aware multi-vector page embeddings              |
| **Visual Base Model** | `Qwen2-VL-2B-Instruct`   | Required by ColQwen2 backbone                          |
| **OCR Engine**        | `Unlimited-OCR (Baidu)`  | Infinite-length document parsing                       |
| **Vector Store**      | `Qdrant`                 | Multi-vector MaxSim retrieval with binary quantization |
| **Agentic Framework** | `LangGraph + LangChain`  | Tool-calling pipelines integrated as OS services       |

All models run **100% locally** — zero cloud APIs required. Optimized for an NVIDIA RTX 5060 (8 GB VRAM) with phase-scheduled GPU loading to avoid OOM errors.

---

## 🤝 Adaptive Companion AI

The CyberHacker suite is designed to be more than just a tool—it acts as a **personalized cybersecurity companion**.

- **Reinforcement Learning (RL) & Adaptation:** The system actively uses RL to learn from your interactions, adapt to your specific preferences, and grow alongside your workflows. It builds an understanding of your methodology over time.
- **Persistent Identity:** Users can associate with the suite as a consistent companion. Your preferences, historical context, and customized workflows are retained as part of the companion's core memory.
- **Decoupled Intelligence:** The "brain" is interchangeable. When you swap the underlying LLM (whether switching to a different local raw model or connecting to an external API), you are simply upgrading the companion's _raw intelligence and extent of capabilities_. The companion's identity and understanding of you remain intact, allowing it to leverage the new model's power without losing its personalized context.

---

## 🛡️ Guardrails — Built Into the Core

Every AI agent in the CyberHacker suite operates with **strictly enforced guardrails** baked into the service layer:

- **Authorization checks** — Agents cannot execute against targets outside an explicitly declared scope.
- **Non-destructive defaults** — Destructive actions (file deletion, payload deployment, privilege escalation) require explicit human confirmation even with root access.
- **Audit logging** — Every agentic action is logged to a tamper-evident local audit trail.
- **Scope-limited tool calls** — LangGraph pipelines run inside sandboxed execution contexts that enforce network, filesystem, and process constraints.
- **Ethical use enforcement** — The system is architecturally designed for authorized environments: CTF labs, personal test machines, and systems the user has legal permission to operate against.

---

## ⚙️ The Knowledge Engine — CyberX Dataset Factory

The AI intelligence powering the CyberHacker suite is trained on knowledge produced by the **CyberX Dataset Factory** — a fully local, automated pipeline that ingests cybersecurity textbooks and produces structured training data.

### How it works

```mermaid
graph TD;
    A[📚 Cybersecurity Books / PDFs] -->|Render Pages| B[Universal Page Renderer];
    B --> C[👁️ Visual Path: ColQwen2 Embeddings];
    B --> D[📝 Text Path: OCR / Docling / Layout Detection];
    C --> E[Master Knowledge Corpus];
    D --> E;
    E --> F[Knowledge Atoms: Techniques, Tools, Vulnerabilities];
    F --> G[Scenario & Decision Generation via Qwen2.5];
    G --> H[Verification + Visual Grounding Check];
    H --> I[(Canonical Dataset)];
    I --> J[Qwen2.5 Fine-Tune Adapter];
    I --> K[Future LLM Adapter];
    J --> L[🤖 CyberHacker AI Core];
```

Unlike standard RAG pipelines that flatten PDFs into linear text, the factory treats **every page as a visual object first**. This preserves the spatial relationships between diagrams, tables, callouts, and code blocks that plain text extraction destroys.

### Key pipeline features

| Feature                              | Description                                                                                                      |
| :----------------------------------- | :--------------------------------------------------------------------------------------------------------------- |
| 👁️ **Visual-First Ingestion**        | Every page rendered at 200 DPI. ColQwen2 embeddings run unconditionally, independent of OCR.                     |
| 🔀 **Layout-Significance Routing**   | Pages are dynamically routed to standard OCR or full-page VLM extraction based on visual complexity.             |
| 🧠 **Decision-Making Datasets**      | Generates branching trajectories, constraint-aware scenarios, and negative examples — not Q&A memorization.      |
| 🤖 **Model-Agnostic Output**         | Canonical dataset format adapts to Qwen2.5, Llama, Gemma, or any future architecture.                            |
| ✅ **Visual Grounding Verification** | Generated training examples are verified against their source page's ColQwen2 embedding to catch hallucinations. |

---

## 🖥️ System Integration

The CyberHacker suite integrates seamlessly with your Kali Linux base:

- **Native agentic services** — LangGraph pipelines registered as `systemd` services, available from the first shell session.
- **Workflow Enhancements** — Integrates with your desktop environment for a focused security-research workflow.
- **Tool Interoperability** — Works alongside and augments all standard Kali tools out-of-the-box.

---

## 📂 Documentation

- 📋 [**PRD**](prd.md) — Full product requirements for the dataset factory & OS integration.
- 🛠️ [**Tech Stack**](techstack.md) — Models, databases, and pipelines in detail.
- ⚠️ [**Constraints & Design Rules**](constraints.md) — VRAM limits, privacy mandates, and architectural guardrails.

---

## 🔒 Code Quality & Security

All commits are gated by a strict pre-push pipeline:

- `Ruff` — Python linting & formatting
- `Prettier / ESLint` — Web asset formatting
- `PMD` — Java anti-bloat checks
- `repo-secret-scan` — Full repo secret detection before every push

Run `setup-git2.ps1` to initialize local Git hooks after cloning.

---

<div align="center">

_Built for authorized cybersecurity education, research, and AI-augmented operations._
_Not for unauthorized use._

</div>
