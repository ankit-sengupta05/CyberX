<div align="center">
  <img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/master/svgs/solid/shield-halved.svg" width="100" height="100" alt="CyberX Logo">

# CyberX Dataset Factory

**Fully Local, Automated Cybersecurity Knowledge & Training-Data Factory**

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Local Execution](https://img.shields.io/badge/Privacy-100%25%20Local-success)](constraints.md)
[![Hardware](https://img.shields.io/badge/VRAM-8GB%20Optimized-orange)](constraints.md)
[![Models](https://img.shields.io/badge/ColPali%20%7C%20Qwen2.5-Supported-purple)](techstack.md)
</div>

---

## 📖 Overview

The **CyberX Dataset Factory** (ColPali-Core Edition) ingests a massive collection of cybersecurity, hacking, and networking textbooks to automatically produce a **master multimodal knowledge corpus**, **canonical training datasets**, and a **layout-aware visual retrieval index**.

Unlike standard RAG systems that flatten PDFs into linear text, CyberX treats every page as a **visual object first**. It preserves the crucial spatial relationships between diagrams, tables, and text using **ColPali/ColQwen2** embeddings and full-page VLM extraction.

## ✨ Core Features

| Feature                      | Description                                                                                                    |
| :--------------------------- | :------------------------------------------------------------------------------------------------------------- |
| 👁️ **Visual-First Pipeline** | Parses every page natively as an image. Uses ColPali to generate layout-aware multi-vector embeddings.         |
| 🤖 **Model-Agnostic Output** | Generates a canonical dataset. Adapters translate this to specific formats (Qwen2.5, Llama, Gemma).            |
| 🔀 **Decision-Making Focus** | Generates branching trajectories, constraint-aware scenarios, and negative examples for tool selection.        |
| 🧠 **Intelligent Routing**   | Dynamically routes pages to standard OCR or full-page VLM extraction based on layout significance.             |
| 🛡️ **Fully Local & Private** | Requires zero cloud APIs. Optimized to run locally on consumer hardware (e.g., RTX 5060 8GB VRAM).             |
| 👑 **Super User Agent**      | The integrated AI agent operates with OS-level super user (root) access for unconstrained pipeline management. |

## 🏗️ Architecture

```mermaid
graph TD;
    A[📚 Books / PDFs] -->|Render| B[Universal Page Render];
    B --> C[Visual Path: ColPali/ColQwen2];
    B --> D[Text Path: OCR/Docling];
    C --> E[Master Knowledge Corpus];
    D --> E;
    E --> F[Knowledge Atoms];
    F --> G[Scenario/Decision Generation];
    G --> H[Verification & Deduplication];
    H --> I[(Canonical Dataset)];
    I --> J[Qwen2.5 Adapter];
    I --> K[Future LLM Adapter];
```

## 📂 Documentation

- 🛠️ [**Tech Stack**](techstack.md) - The specific models, databases, and pipelines powering the factory.
- ⚠️ [**Constraints & Design**](constraints.md) - Crucial VRAM limitations, privacy mandates, and architectural rules.
- 📋 [**Product Requirements Document (PRD)**](prd.md) - The full specification for the dataset factory.

## 🚀 Getting Started

_Coming soon: Instructions for initializing the GPU scheduler and running the ingestion pipeline._

## 🔒 Security & Code Quality

This repository enforces strict code quality and anti-bloat pipelines on all commits using `Ruff` (Python), `Prettier/ESLint` (Web), and `PMD` (Java). Ensure you run `setup-git2.ps1` to initialize the local Git hooks.
