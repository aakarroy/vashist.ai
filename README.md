<div align="center">

# Vashist AI

### *Your Personal AI Study Companion — Powered by Local LLMs*

[![Python](https://img.shields.io/badge/Python-3.14+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20DB-FF6B35?style=for-the-badge)](https://www.trychroma.com)
[![LangChain](https://img.shields.io/badge/LangChain-Orchestration-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

> **Vashist AI** is a fully local, privacy-first Retrieval-Augmented Generation (RAG) study assistant. Upload your PDFs, PowerPoint slides, and web URLs — then chat with a locally running LLM that has been grounded in *your* study material. No cloud. No data leakage. Just intelligence.

</div>

---

## Features

- **Multi-format Ingestion** — Load study material from PDFs, PowerPoint (`.pptx`), and live web URLs simultaneously
- **Multimodal Understanding** — Automatically extracts and captions images from all source types (PDFs, PPTs, and web pages)
- **Semantic Search** — Uses `nomic-embed-text` via Ollama to embed and retrieve the most relevant text chunks and image captions
- **Smart Chunking** — Splits documents using Qwen 2.5 tokenizer-aware chunking (1000-token chunks with 300-token overlap) for optimal context windows
- **Dynamic Expert Persona** — The LLM dynamically adopts the most appropriate expert role (e.g., "Professor in Computer Vision") based on your query and the uploaded material
- **Persistent Vector Store** — ChromaDB stores embeddings on disk so ingestion only happens once; subsequent runs load directly from the persisted store
- **URL Ingestion via Jina Reader** — Cleanly parses web articles into markdown, including image extraction from pages
- **100% Local & Private** — LLM inference runs entirely through Ollama; your documents never leave your machine

---

## Architecture Overview

```
                        ┌──────────────────────────────────────────────┐
                        │              DATA SOURCES                    │
                        │    PDFs  |  PPTXs  |  URLs                   │
                        └──────────────────┬───────────────────────────┘
                                           │
                                           ▼
                        ┌──────────────────────────────────────────────┐
                        │           DOCUMENT LOADER (Loaders)          │
                        │  PyMuPDF · UnstructuredPPT · Jina Reader     │
                        │  + Image Extraction from all source types    │
                        └──────────┬───────────────────┬───────────────┘
                                   │                   │
                          Text Docs│            Images │
                                   ▼                   ▼
                   ┌───────────────────┐   ┌──────────────────────┐
                   │  CHUNKING         │   │  CAPTIONER           │
                   │  Qwen 2.5 Tokens  │   │  microsoft/git-base  │
                   │  1000 tok chunks  │   │  HuggingFace model   │
                   └────────┬──────────┘   └──────────┬───────────┘
                            │                         │
                            ▼                         ▼
                   ┌─────────────────────────────────────────────┐
                   │          EMBEDDINGS (nomic-embed-text)      │
                   │          via Ollama — Text & Caption        │
                   └──────────────────────┬──────────────────────┘
                                          │
                                          ▼
                   ┌─────────────────────────────────────────────┐
                   │        VECTOR STORE (ChromaDB)              │
                   │   Persistent on disk · Cosine Similarity    │
                   │   Unified collection for text + images      │
                   └──────────────────────┬──────────────────────┘
                                          │
                              ┌───────────┘
                              │     At Query Time
                              ▼
                   ┌─────────────────────────────────────────────┐
                   │             RETRIEVER                       │
                   │  Embed query → Top-K search → Score filter  │
                   │  Returns: relevant text chunks + image refs │
                   └──────────────────────┬──────────────────────┘
                                          │
                                          ▼
                   ┌─────────────────────────────────────────────┐
                   │          GENERATION (Qwen2.5:3b)            │
                   │  1. Meta-Prompt: determine expert persona   │
                   │  2. Answer grounded in retrieved context    │
                   │  3. Fallback to LLM knowledge if no context │
                   └─────────────────────────────────────────────┘
```

---

## Project Structure

```
vashist/
├── src/
│   ├── main.py              # Entry point — orchestrates the full pipeline
│   ├── document_loader.py   # Multi-format loader (PDF, PPTX, URL + images)
│   ├── captioner.py         # Image captioning using microsoft/git-base
│   ├── chunking.py          # Token-aware text splitter (Qwen2.5 tokenizer)
│   ├── embedding.py         # Text & caption embeddings via Ollama
│   ├── vector_storage.py    # ChromaDB persistent vector store wrapper
│   ├── retriever.py         # Semantic retrieval with similarity scoring
│   ├── generation.py        # LLM interaction & dynamic persona prompting
│   └── __init__.py
│
├── data/                    # Place your study materials here (gitignored)
│   ├── your_paper.pdf
│   ├── your_lecture.pptx
│   └── ...
│
├── vector_store/            # Auto-generated ChromaDB store (gitignored)
├── temp-images/             # Temporarily extracted images (gitignored)
├── .env                     # API keys (gitignored)
├── .env.example             # Template for environment variables
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Project metadata
└── .python-version          # Required Python version (3.14)
```

---

## How It Works — Step by Step

### Phase 1: Ingestion (runs once)

1. **Source Classification** — All sources in the `data/` directory plus any hardcoded URLs are classified by type (PDF, PPTX, or URL).
2. **Document Loading**
   - **PDFs**: Loaded with `PyMuPDFLoader`. All embedded images are extracted page-by-page.
   - **PowerPoints**: Loaded with `UnstructuredPowerPointLoader`. Images are extracted from each slide's shapes.
   - **Web URLs**: Fetched via [Jina Reader AI](https://jina.ai/reader/) which converts pages to clean markdown. Images referenced in the markdown are downloaded locally.
   - **SVG Handling**: Any SVG images from web pages are automatically converted to PNG using PyMuPDF before captioning.

3. **Image Captioning** — Valid images (>5 KB and larger than 500×500px) are captioned using `microsoft/git-base` loaded locally via HuggingFace Transformers. CUDA is used automatically if available.

4. **Text Chunking** — All documents are split using LangChain's `RecursiveCharacterTextSplitter` calibrated to the **Qwen 2.5** tokenizer (1000 tokens per chunk, 300-token overlap) to respect the LLM's context expectations.

5. **Embedding Generation** — Text chunks and image captions are embedded in batches of 16 using the `nomic-embed-text` model running locally via Ollama.

6. **Vector Store Persistence** — All embeddings, documents, and image paths are stored in a local ChromaDB database (`vector_store/`) using cosine similarity. The store is reused on subsequent runs.

### Phase 2: Q&A Loop (interactive)

1. **Query Embedding** — The user's question is embedded with the same `nomic-embed-text` model.
2. **Retrieval** — Top-5 most similar chunks/images are fetched from ChromaDB. Results with cosine similarity below 0.5 are filtered out. Retrieved items are split into `texts` and `images`.
3. **Dynamic Expert Persona** — The LLM (`Qwen2.5:3b`) is first asked to act as a *Meta-Prompt Engine* and determine the ideal expert role for answering the question given the context.
4. **Grounded Answer Generation** — The LLM then answers the user's question while staying in the expert persona, using the retrieved text and image captions as context.
5. **Fallback** — If no context is retrieved, the LLM answers from its own training knowledge while still adopting the most appropriate expert persona.
6. **Image References** — Paths to any retrieved visual assets are printed alongside the answer.
7. **Docs Reference** — The answer includes references to the original documents (PDF/PPT/URL) from which the context was retrieved.
8. **Repeat** — The user can ask follow-up questions, and the loop continues until the user types `quit`.

---

## Getting Started

### Prerequisites

| Requirement | Details |
|---|---|
| **Python** | 3.12+ (see `.python-version`) |
| **Ollama** | Must be installed and running locally |
| **CUDA GPU** (optional) | Required for fast image captioning; CPU fallback available |
| **Jina API Key** | For URL ingestion — [get one free here](https://jina.ai) |

### 1. Install Ollama & Pull Models

```bash
# Install Ollama from https://ollama.com/download
# Then pull the required models:

ollama pull nomic-embed-text   # For embeddings
ollama pull qwen2.5:3b         # For answer generation
```

### 2. Clone & Set Up Environment

```bash
git clone https://github.com/your-username/vashist.git
cd vashist

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys

```bash
# Copy the template
copy .env.example .env

# Edit .env and add your keys
JINA_API_KEY="your_jina_api_key_here"
# These keys are required to just load data from URLs. If you only use local PDFs/PPTs, you can leave it blank. This is the only place where internet access is used. Except for this, all processing is local.
```

### 4. Add Your Study Materials

Place your study resources into the `data/` folder:

```
data/
├── lecture1.pdf
├── research_paper.pdf
├── slides.pptx
└── ...
```

You can also add web URLs directly in `src/main.py` by appending to the `sources` list:

```python
sources.append(r"https://example.com/your-study-page")
```

### 5. Run Vashist AI

```bash
cd src
python main.py
```

On the **first run**, the full ingestion pipeline (loading → captioning → chunking → embedding → storing) executes automatically. This may take several minutes depending on the size of your materials and whether a GPU is available.

On **subsequent runs**, the pipeline skips ingestion and loads directly from the persisted `vector_store/`.

```
Enter your Question: What is contrastive learning in CLIP?
Acting as Principal Computer Vision Researcher specializing in multimodal representation learning
...
```

Type `quit` to exit.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `JINA_API_KEY` | **Yes** (for URL ingestion) | API key for [Jina Reader AI](https://jina.ai/reader/) used to convert web pages to clean markdown |

---

## Configuration Reference

Key parameters you can tune directly in the source files:

| File | Parameter | Default | Description |
|---|---|---|---|
| `chunking.py` | `chunk_size` | `1000` | Tokens per chunk |
| `chunking.py` | `chunk_overlap` | `300` | Overlap between chunks |
| `retriever.py` | `top_k` | `5` | Number of results to retrieve |
| `retriever.py` | `score_threshold` | `0.5` | Minimum cosine similarity to include a result |
| `captioner.py` | `model_name` | `microsoft/git-base` | HuggingFace captioning model |
| `embedding.py` | `model_name` | `nomic-embed-text` | Ollama embedding model |
| `generation.py` | `model` | `Qwen2.5:3b` | Ollama LLM for generation |
| `generation.py` | `temperature` | `0.1` | LLM sampling temperature (low = deterministic) |
| `captioner.py` | `min_kb` | `5` | Minimum image file size in KB to caption |
| `captioner.py` | `min_dimension` | `500×500px` | Minimum image dimensions to caption |

---

## Module Breakdown

### [`src/document_loader.py`](src/document_loader.py)
The core ingestion module. The `Loaders` class accepts a list of mixed source paths/URLs and:
- Routes each source to the correct loader
- Extracts all embedded images to `temp-images/`
- Converts any downloaded SVGs to PNG format automatically

The inner `UrlLoader` class wraps the [Jina Reader AI](https://r.jina.ai) API, passing special headers to retain images, handle shadow DOMs, and cache responses.

### [`src/captioner.py`](src/captioner.py)
Uses `microsoft/git-base` (a vision-language model) to generate natural language captions for each extracted image. Filters out icons and tiny graphics (< 5 KB or < 500×500px). Runs on GPU if available.

### [`src/chunking.py`](src/chunking.py)
Wraps LangChain's `RecursiveCharacterTextSplitter` with Qwen 2.5's tokenizer to produce semantically coherent chunks that respect the target LLM's token vocabulary.

### [`src/embedding.py`](src/embedding.py)
A thin wrapper around Ollama's embedding endpoint using `nomic-embed-text`. Handles batched embedding for both text chunks and image captions. Also provides single-query embedding for retrieval time.

### [`src/vector_storage.py`](src/vector_storage.py)
Wraps ChromaDB's `PersistentClient` into a clean interface. Uses a single unified collection (`Multi_Media_Storage`) for both text and image entries. Image entries store the local file path as a URI alongside the caption as the document content.

### [`src/retriever.py`](src/retriever.py)
Takes a raw query, embeds it, and queries ChromaDB for the top-K most similar items. Filters by similarity threshold and separates results into text documents and image references. Converts cosine distances to similarity scores (`1 - distance`).

### [`src/generation.py`](src/generation.py)
Implements a two-stage prompting strategy:
1. **Stage 1 (Meta-Prompt)**: Ask the LLM to identify the ideal expert persona for the topic
2. **Stage 2 (Answer)**: Ask the LLM to answer the question while embodying that persona and using retrieved context

Falls back gracefully to the LLM's internal knowledge if no relevant context is retrieved.

---

## Privacy & Security

Vashist AI is designed with privacy as a first principle:

- All LLM inference happens **locally via Ollama** — no query or document content is sent to any remote LLM service
- The only external API call is to **Jina Reader AI** for URL-based document loading (optional feature)
- No telemetry or usage tracking of any kind

---

<div align="center">

Made with love for curious minds who want to study smarter, not harder.

**Vashist AI** — *Because your study materials deserve to talk back.*

</div>
