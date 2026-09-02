# 🛠️ Technology Stack

Based on the ColPali-Core Cybersecurity Dataset Factory PRD, the system leverages the following technologies to build a robust, privacy-first, multimodal knowledge extraction pipeline.

## 🧠 AI & Machine Learning Models

| Component                 | Technology                                  | Purpose                                                       |
| ------------------------- | ------------------------------------------- | ------------------------------------------------------------- |
| **Visual Indexing**       | **ColPali** / **ColQwen2**                  | Multi-vector visual embeddings preserving page layout.        |
| **Generation / LLM**      | **Qwen2.5** (Primary), **Llama**, **Gemma** | Scenario generation, trajectory building, and tool selection. |
| **Vision Language Model** | **Qwen2.5-VL**                              | Full-page VLM extraction for high-layout-significance pages.  |

## 🗄️ Database & Storage

| Component           | Technology              | Purpose                                                                            |
| ------------------- | ----------------------- | ---------------------------------------------------------------------------------- |
| **Vector Database** | **Qdrant**              | Native multi-vector storage, MaxSim late-interaction scoring, binary quantization. |
| **Data Format**     | **JSONL**, **PNG/WebP** | Canonical model-agnostic dataset and universal page render storage.                |

## ⚙️ Data Extraction & Processing

| Component            | Technology             | Purpose                                           |
| -------------------- | ---------------------- | ------------------------------------------------- |
| **Document Parsing** | **Docling**, local OCR | Text, table, equation, and code block extraction. |
| **Image Processing** | **Pillow**, **OpenCV** | Rendering PDFs/EPUBs to 200 DPI base images.      |

## 🖥️ Hardware & Execution

| Component | Specification              | Details                                                            |
| --------- | -------------------------- | ------------------------------------------------------------------ |
| **GPU**   | NVIDIA RTX 5060 (8GB VRAM) | Primary inference device. Strict model loading/unloading required. |
| **CPU**   | Intel i7-14700HX           | Used for fallback operations (OCR, preprocessing).                 |
| **OS**    | Windows / Linux            | Fully local environment with no cloud dependencies.                |

## 🛡️ Code Quality Pipeline

| Tool                  | Purpose                                                  |
| --------------------- | -------------------------------------------------------- |
| **Ruff**              | Lightning-fast Python linting and formatting.            |
| **Prettier / ESLint** | JavaScript, TypeScript, and Markdown formatting/linting. |
| **PMD**               | Java static analysis to prevent code bloat.              |
| **Pre-commit**        | Git hooks ensuring code quality before push.             |
