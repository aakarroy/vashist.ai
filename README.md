<div align="center">

# Vashist AI

### Your Personal AI Study Companion Powered by Local LLMs

[![Python](https://img.shields.io/badge/Python-3.14+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20DB-FF6B35?style=for-the-badge)](https://www.trychroma.com)
[![LangChain](https://img.shields.io/badge/LangChain-Orchestration-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

**Vashist AI** is a fully local, privacy-first Retrieval-Augmented Generation (RAG) study assistant. Upload your PDFs, PowerPoint slides, and web URLs, then chat with a locally running LLM that has been grounded in your study material. No cloud. No data leakage. Just intelligence.

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Module Breakdown](#module-breakdown)
- [How It Works](#how-it-works)
- [Getting Started](#getting-started)
- [Configuration Reference](#configuration-reference)
- [Environment Variables](#environment-variables)
- [Privacy and Security](#privacy-and-security)
- [License](#license)

---

## Overview

Vashist AI is a terminal-based study assistant that lets you load documents from multiple formats (PDFs, PowerPoint presentations, and live web URLs), indexes them into a persistent local vector database, and answers your questions using a locally running large language model. The system is built entirely around local inference via Ollama, meaning no document content or query ever leaves your machine during the core question-answering workflow.

The pipeline has two distinct phases:

1. **Ingestion** — runs once. Documents are loaded, images are extracted and captioned, text is chunked, all embeddings are generated, and everything is stored persistently in ChromaDB.
2. **Q&A Loop** — runs on every subsequent invocation. The vector store is loaded from disk and the system enters an interactive query loop.

---

## Features

- **Multi-format Document Ingestion** — Simultaneously load study material from PDFs, PowerPoint files (.pptx), and live web URLs
- **Multimodal Understanding** — Automatically extracts and captions images from all supported source types (PDFs, PPTs, and web pages)
- **Semantic Retrieval** — Uses `nomic-embed-text` via Ollama to embed text chunks and image captions, then retrieves the most relevant ones via cosine similarity in ChromaDB
- **Multi-Query Expansion** — The LLM generates multiple semantically varied rephrasings of the user query before retrieval to maximize recall across the vector store
- **Tokenizer-Aware Chunking** — Documents are split using LangChain's `RecursiveCharacterTextSplitter` calibrated to the Qwen 2.5 tokenizer vocabulary (1000-token chunks, 300-token overlap)
- **Dynamic Expert Persona** — A meta-prompt stage determines the most appropriate expert role for each query (for example, "Principal Computer Vision Researcher") before generating the final answer
- **Persistent Vector Store** — ChromaDB stores all embeddings on disk; ingestion only runs once. Subsequent runs load the existing store and skip directly to the Q&A loop
- **URL Ingestion via Jina Reader** — Web pages are fetched via the Jina Reader AI API, which converts them to clean markdown and preserves image references
- **SVG-to-PNG Conversion** — Any SVG images encountered during web ingestion are automatically converted to PNG via PyMuPDF before captioning
- **In-Memory Response Cache** — Identical (or near-identical) queries are served from an in-memory SHA-256-keyed cache with a configurable TTL, avoiding redundant LLM inference
- **PII Detection and Masking** — User queries are scanned for Personally Identifiable Information (emails, phone numbers, SSNs, credit card numbers, IP addresses) before being sent to the LLM; detected PII is replaced with redaction tokens
- **Output Validation** — LLM responses are scanned for PII and harmful content patterns before being returned to the user
- **Structured Logging** — All pipeline stages emit structured log messages to both a rotating log file and stdout, configurable via the settings system
- **Centralized Settings via Pydantic** — All tuneable parameters are managed through a `pydantic-settings` `BaseSettings` class, populated from the `.env` file with `lru_cache` for singleton behavior
- **100% Local and Private** — All LLM inference and embedding generation run entirely through Ollama; your documents never leave your machine (the only external call is to Jina Reader AI for URL loading, and it is optional)

---

## Architecture Overview

```
                        +----------------------------------------------+
                        |              DATA SOURCES                    |
                        |    PDFs  |  PPTXs  |  URLs                   |
                        +------------------+---------------------------+
                                           |
                                           v
                        +----------------------------------------------+
                        |           DOCUMENT LOADER (Loaders)          |
                        |  PyMuPDF  |  UnstructuredPPT  |  Jina Reader |
                        |  + Image Extraction from all source types    |
                        +----------+-------------------+---------------+
                                   |                   |
                          Text Docs|            Images |
                                   v                   v
                   +-------------------+   +----------------------+
                   |  CHUNKING         |   |  CAPTIONER           |
                   |  Qwen 2.5 Tokens  |   |  microsoft/git-base  |
                   |  1000 tok chunks  |   |  HuggingFace model   |
                   +--------+----------+   +----------+-----------+
                            |                         |
                            v                         v
                   +-----------------------------------------+
                   |      EMBEDDINGS (nomic-embed-text)      |
                   |      via Ollama  --  Text and Caption   |
                   +----------------------+------------------+
                                          |
                                          v
                   +-----------------------------------------+
                   |        VECTOR STORE (ChromaDB)          |
                   |   Persistent on disk  |  Cosine Space   |
                   |   Unified collection for text + images  |
                   +----------------------+------------------+
                                          |
                              +-----------+
                              |     At Query Time
                              v
                   +-----------------------------------------+
                   |        MULTI-QUERY EXPANSION            |
                   |  Qwen2.5:3b generates 2 extra variants  |
                   |  of the user query for broader recall   |
                   +----------------------+------------------+
                                          |
                                          v
                   +-----------------------------------------+
                   |             RETRIEVER                   |
                   |  Embed query -> Top-K -> Score filter   |
                   |  Returns: text chunks + image captions  |
                   +----------------------+------------------+
                                          |
                                          v
                   +-----------------------------------------+
                   |     SECURITY: PII INPUT DETECTION       |
                   |  Regex scan of query, mask if found     |
                   +----------------------+------------------+
                                          |
                                          v
                   +-----------------------------------------+
                   |   CACHE LOOKUP (CacheLayer)             |
                   |  SHA-256 key, TTL-based, in-memory      |
                   +----------------------+------------------+
                                          |
                                          v
                   +-----------------------------------------+
                   |   GENERATION (Qwen2.5:3b via Ollama)    |
                   |  1. Meta-Prompt: determine expert role  |
                   |  2. Answer grounded in retrieved context|
                   |  3. Fallback to LLM knowledge if empty  |
                   +----------------------+------------------+
                                          |
                                          v
                   +-----------------------------------------+
                   |   SECURITY: OUTPUT VALIDATION           |
                   |  PII masking + harmful content check    |
                   +----------------------+------------------+
                                          |
                                          v
                                    Final Answer
                              + Source References
                              + Visual Asset Paths
```

---

## Project Structure

```
vashist.ai/
|
+-- src/
|   +-- main.py              # Entry point -- orchestrates the full pipeline
|   +-- config.py            # Pydantic-settings configuration singleton
|   +-- document_loader.py   # Multi-format loader (PDF, PPTX, URL + images)
|   +-- captioner.py         # Image captioning using microsoft/git-base
|   +-- chunking.py          # Tokenizer-aware text splitter (Qwen2.5)
|   +-- embedding.py         # Text and caption embeddings via Ollama
|   +-- vector_storage.py    # ChromaDB persistent vector store wrapper
|   +-- retriever.py         # Semantic retrieval with cosine similarity scoring
|   +-- generation.py        # LLM interaction, multi-query, and dynamic persona
|   +-- security.py          # PII detection/masking and output validation
|   +-- cache.py             # In-memory TTL-based query response cache
|   +-- __init__.py
|
+-- data/                    # Place study materials here (gitignored)
|   +-- your_paper.pdf
|   +-- your_lecture.pptx
|   +-- ...
|
+-- vector_store/            # Auto-generated ChromaDB store (gitignored)
+-- .temp-images/            # Temporarily extracted images during ingestion (gitignored)
+-- .env                     # Runtime configuration and API keys (gitignored)
+-- .env.example             # Template for environment variables
+-- requirements.txt         # Python dependencies
+-- pyproject.toml           # Project metadata and build configuration
+-- .python-version          # Required Python version pin (3.14)
+-- LICENSE                  # MIT License
```

---

## Module Breakdown

### `src/main.py` -- Entry Point

The orchestrator of the entire pipeline. On startup it:

1. Reads all files from the `data/` directory and appends any hardcoded URLs to the sources list.
2. Detects whether a `vector_store/` directory already exists on disk.
   - If it does **not** exist, the full ingestion pipeline runs: loading, captioning, chunking, embedding, and storage.
   - If it **does** exist, ingestion is skipped entirely and the existing store is loaded.
3. Initializes the `PIIDetector`, `Embeddings`, `VectorStore`, and `Retriever` instances for the Q&A session.
4. Enters a `while True` loop that reads user queries from stdin, applies PII detection, checks the cache, and delegates to the `generation()` function.

Logging is configured here using the settings from `config.py`, writing to both a file (default: `logs.log`) and stdout.

---

### `src/config.py` -- Centralized Settings

A `pydantic-settings` `BaseSettings` subclass called `Settings` that reads configuration values from the `.env` file. The `get_settings()` function is decorated with `@lru_cache` to ensure the settings are loaded once and reused as a singleton throughout the application.

**Available settings:**

| Setting | Default | Description |
|---|---|---|
| `jina_api_key` | `""` | Jina Reader AI API key for URL ingestion |
| `log_level` | `"INFO"` | Python logging level |
| `max_retries` | `5` | Maximum retry attempts (used for resilience) |
| `cache_ttl_seconds` | `300` | Time-to-live for cached query responses in seconds |
| `log_file_name` | `"logs.log"` | Output file path for the log handler |

---

### `src/document_loader.py` -- Multi-Format Document Loader

Contains two classes:

**`UrlLoader(BaseLoader)`**

A custom LangChain-compatible loader that wraps the Jina Reader AI API (`https://r.jina.ai/`). It uses the following request headers to maximize fidelity of the retrieved content:

- `X-Retain-Images: all` -- preserves all image references in the markdown output
- `X-With-Shadow-Dom: true` -- renders shadow DOM elements
- `X-With-Iframe: true` -- includes iframe content
- `X-Cache-Tolerance: 3600` -- allows Jina to cache responses for up to one hour

The `get_images()` method parses the markdown output for image URLs using a regex, downloads each image, saves it to `.temp-images/` with a UUID filename, and returns a list of image path dictionaries with source metadata.

**`Loaders`**

The main ingestion dispatcher. Accepts a list of mixed source strings (file paths and URLs) and:

1. Classifies each source as a PDF, PPTX, or URL based on its prefix or suffix.
2. Calls the appropriate loader method: `pdf_loader()`, `ppt_loader()`, or `url_loader()`.
3. Aggregates all LangChain `Document` objects into `self.all_doc` and all image path dicts into `self.imgs`.
4. After all sources are loaded, calls `convert_all_svgs_to_png()` to convert any downloaded SVG files to PNG using PyMuPDF, then deletes the original SVG files.

Image extraction for PDFs uses PyMuPDF (`fitz`) to iterate over every page and extract each embedded image by xref. Image extraction for PPTs uses `python-pptx` to iterate over every slide shape that has an `image` attribute.

---

### `src/captioner.py` -- Image Captioning

The `CaptionGenerator` class loads `microsoft/git-base` from HuggingFace using `AutoProcessor` and `AutoModelForCausalLM`. It automatically detects whether a CUDA GPU is available and loads the model in `float16` (GPU) or `float32` (CPU). If no GPU is found, the user is prompted to confirm CPU usage before proceeding.

The `generate_caption()` method filters images before captioning using two quality gates:

- **Minimum file size**: images smaller than 5 KB are discarded (likely icons or decorative elements).
- **Minimum dimensions**: images smaller than 500x500 pixels are discarded.

Qualifying images are resized to a 512x512 thumbnail, passed through the GIT model with `min_new_tokens=20` and `max_new_tokens=100`, and the resulting natural language caption is stored alongside the image path and source metadata.

---

### `src/chunking.py` -- Tokenizer-Aware Text Splitting

A single function `chunking()` that instantiates LangChain's `RecursiveCharacterTextSplitter` configured with the Qwen 2.5 3B tokenizer from HuggingFace (`Qwen/Qwen2.5-3B`). This ensures that chunk boundaries are determined by the same token vocabulary the generation LLM uses, avoiding token count mismatches at inference time.

**Chunking parameters:**

| Parameter | Value | Notes |
|---|---|---|
| `chunk_size` | `1000` | Maximum tokens per chunk |
| `chunk_overlap` | `300` | Overlapping tokens between consecutive chunks |
| Separators | `\n\n`, `\n`, ` `, `""` | Priority order for splitting |

---

### `src/embedding.py` -- Embedding Generation

The `Embeddings` class wraps Ollama's `embed` endpoint using the `nomic-embed-text` model. It exposes three methods:

- `generate_query_embeddings(query)` -- embeds a single query string at retrieval time.
- `generate_text_embedding(chunks, batch_size=16)` -- batched embedding of text chunks with a tqdm progress bar.
- `generate_caption_embedding(imgs, batch_size=16)` -- batched embedding of image captions with a tqdm progress bar.

All three methods call `ollama.embed()` directly from the `ollama` Python SDK.

---

### `src/vector_storage.py` -- Persistent Vector Store

The `VectorStore` class wraps ChromaDB's `PersistentClient`. It maintains a single unified collection named `Multi_Media_Storage` configured with `hnsw:space: cosine` for cosine similarity search.

Two storage methods are available:

- `add_documents(docs, embeddings)` -- stores text chunks with their embeddings, metadata (including source file path and page number), and document content.
- `add_visuals(imgs, embeddings)` -- stores image caption embeddings alongside the caption text as the document and the local file path as a URI.

By using a single collection for both text and images, retrieval queries can surface either type in a single ChromaDB query.

---

### `src/retriever.py` -- Semantic Retrieval

The `Retriever` class accepts a `VectorStore` and `Embeddings` instance. Its `retrieve()` method:

1. Embeds the input query using `Embeddings.generate_query_embeddings()`.
2. Queries ChromaDB for the top-K nearest neighbors, requesting `uris`, `documents`, `distances`, and `metadatas`.
3. Converts ChromaDB's cosine distance to a similarity score via `similarity = 1 - distance`.
4. Filters out results below the `score_threshold` (default: 0.5).
5. Separates results into `texts` (no URI) and `images` (has URI) and returns both.

**Default retrieval parameters:**

| Parameter | Default | Description |
|---|---|---|
| `top_k` | `3` | Number of nearest neighbors to retrieve |
| `score_threshold` | `0.5` | Minimum cosine similarity to include a result |

---

### `src/generation.py` -- LLM Generation with Multi-Query and Persona

This module contains the two core functions that drive the answer generation pipeline.

**`multi_query(query)`**

Uses `Qwen2.5:3b` to generate two semantically diverse alternative phrasings of the user's original query. These alternatives, combined with the original, give three total queries that are each sent independently to the retriever, and their results are merged before generation. This multi-query strategy improves recall by retrieving documents that might be missed by a single formulation.

**`generation(retriever, query)`**

The main generation function. It:

1. Calls `multi_query()` to get three query variants.
2. Calls `retriever.retrieve()` for each variant and merges all text and image results.
3. If context is found:
   - Sends a **meta-prompt** to the LLM asking it to identify the single most appropriate expert persona for the query and context.
   - Sends the actual user question along with all retrieved text and image caption context to the LLM, instructing it to answer in the voice of the identified persona without greetings or meta-commentary.
4. If no context is found, falls back to a direct zero-context prompt to the LLM.
5. Passes the response through `OutputValidator.detect()` for PII masking and harmful content blocking.
6. Stores the final response in the cache via `cached.set()`.
7. Prints source document references (with page numbers where available) and visual asset paths.

The LLM is initialized with `temperature=0.1` for near-deterministic, factual responses.

---

### `src/security.py` -- PII Detection, Masking, and Output Validation

**`PIIDetector`**

Scans text for five categories of PII using regular expressions:

| PII Type | Pattern Description | Mask Token |
|---|---|---|
| `email` | Standard email format | `[EMAIL REDACTED]` |
| `phone` | 10-digit US phone numbers | `[PHONE REDACTED]` |
| `ssn` | US Social Security Number | `[SSN REDACTED]` |
| `credit_card` | 16-digit card numbers | `[CARD REDACTED]` |
| `ip_address` | IPv4 addresses | `[IP REDACTED]` |

- `detect(text)` returns a dict of detected PII types and their matched values.
- `mask(text)` returns the input text with all PII replaced by the corresponding mask token.

**`OutPutValidator`**

Combines `PIIDetector` with a set of regex patterns for harmful content (such as instructions for hacking, exposed passwords, or leaked API keys). The `detect(text)` method:

1. Runs PII detection and masking on the LLM response.
2. Checks for harmful content patterns.
3. If harmful content is found, replaces the entire response with `[Response blocked: Potentially Harmful Content]`.
4. Returns the sanitized output and a list of any warnings generated.

---

### `src/cache.py` -- In-Memory Response Cache

The `CacheLayer` class provides a simple in-memory key-value cache for query responses.

- Keys are SHA-256 hashes of the lowercased, stripped query string, ensuring case-insensitive deduplication.
- Each cache entry stores the original query, the response string, and a Unix timestamp.
- `get(query)` checks whether a valid (non-expired) entry exists and returns it; expired entries are deleted on access.
- `set(query, response)` stores a new entry with the current timestamp.
- TTL is read from `settings.cache_ttl_seconds` (default: 300 seconds / 5 minutes).

A module-level singleton `cached = CacheLayer()` is imported directly by `main.py` and `generation.py`.

---

## How It Works

### Phase 1: Ingestion (Runs Once)

This phase executes only when the `vector_store/` directory does not exist. All ingestion results are persisted to disk, so this phase is skipped on all subsequent runs.

1. **Source Classification** -- Each path in the `data/` directory and each hardcoded URL is classified as PDF, PPTX, or URL based on its prefix or file extension. Classification is case-insensitive.

2. **Document Loading**
   - **PDFs**: Loaded with LangChain's `PyMuPDFLoader`. Separately, PyMuPDF's `fitz` API iterates over every page to extract embedded images by xref, saving them to `.temp-images/`.
   - **PowerPoints**: Partitioned with `unstructured.partition.pptx`. All text elements from all slides are concatenated into a single `Document`. Images are extracted separately using `python-pptx` by inspecting each shape on every slide for an `image` attribute.
   - **Web URLs**: Each URL is fetched through the Jina Reader AI API, which returns the page as clean markdown. Images referenced in the markdown are downloaded individually and saved to `.temp-images/`.
   - **SVG Conversion**: After all sources are loaded, all `.svg` files in `.temp-images/` are converted to `.png` using PyMuPDF and the originals are deleted.

3. **Image Captioning** -- Each image in `.temp-images/` is evaluated against size and dimension filters. Qualifying images are captioned using `microsoft/git-base` via HuggingFace Transformers. Captions are 20 to 100 tokens in length.

4. **Text Chunking** -- All loaded `Document` objects are split with `RecursiveCharacterTextSplitter` using the Qwen 2.5 3B tokenizer. Each chunk retains the source metadata from its parent document.

5. **Embedding Generation** -- Text chunks are embedded in batches of 16 using `nomic-embed-text` via Ollama. Image captions are embedded in the same batch size using the same model.

6. **Vector Store Population** -- Text chunk embeddings are stored in ChromaDB's `Multi_Media_Storage` collection with document content and metadata. Image caption embeddings are stored in the same collection with the caption as the document and the local image file path as a URI.

### Phase 2: Q&A Loop (Interactive)

This phase runs on every invocation once the vector store exists.

1. **Query Input** -- The user types a natural language question. Entering `q` exits the loop.
2. **PII Check** -- `PIIDetector.detect()` scans the query. If PII is found, a warning is logged and `PIIDetector.mask()` replaces the sensitive values before the query is used further.
3. **Cache Lookup** -- The cache is checked for an existing response. If a valid cached response is found, it is returned immediately without invoking the LLM or retriever.
4. **Multi-Query Expansion** -- `multi_query()` uses the LLM to produce two additional semantically varied phrasings of the original query.
5. **Retrieval** -- All three query variants are embedded and used to query ChromaDB. Top-3 results per query (above the 0.5 similarity threshold) are merged across all variants into a combined context.
6. **Expert Persona Assignment** -- If any context was retrieved, the LLM is first asked via a meta-prompt to determine the most appropriate expert role for answering the question based on the retrieved material.
7. **Answer Generation** -- The LLM generates the final answer using the expert persona, the retrieved text context, and the retrieved image captions. Strict tone rules prevent greetings, meta-commentary, and role restatements.
8. **Output Validation** -- The LLM response passes through `OutPutValidator.detect()` for PII masking and harmful content blocking before being printed.
9. **Cache Storage** -- The validated response is stored in `CacheLayer` under the SHA-256 hash of the query.
10. **Source References** -- After the answer, source document paths (with page numbers for PDFs) and local image file paths are printed for traceability.
11. **Repeat** -- The loop returns to step 1 until the user quits.

---

## Getting Started

### Prerequisites

| Requirement | Details |
|---|---|
| **Python** | 3.14 (pinned in `.python-version`) |
| **Ollama** | Must be installed and running locally on the default port |
| **CUDA GPU** (optional) | Required for fast image captioning; CPU fallback is available with a confirmation prompt |
| **Jina API Key** | Required only for URL ingestion; free tier available at [jina.ai](https://jina.ai) |

### Step 1: Install Ollama and Pull Required Models

Install Ollama from [ollama.com/download](https://ollama.com/download), then pull the two required models:

```bash
ollama pull nomic-embed-text
ollama pull qwen2.5:3b
```

`nomic-embed-text` is used for all embedding generation (text chunks, image captions, and query embeddings). `qwen2.5:3b` is used for multi-query expansion, expert persona assignment, and final answer generation.

### Step 2: Clone the Repository and Set Up a Virtual Environment

```bash
git clone https://github.com/aakarroy/vashist.ai.git
cd vashist.ai

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

```bash
copy .env.example .env
```

Open `.env` and fill in the values. At minimum, set `JINA_API_KEY` if you intend to load content from URLs.

```
JINA_API_KEY="your_jina_api_key_here"
log_level=INFO
max_retries=5
cache_ttl_seconds=300
log_file_name=logs.log
```

If you only use local PDF and PPTX files, `JINA_API_KEY` can be left blank and URL sources should be removed from `src/main.py`.

### Step 4: Add Study Materials

Place PDF and PPTX files in the `data/` directory:

```
data/
+-- lecture1.pdf
+-- research_paper.pdf
+-- slides.pptx
+-- ...
```

To include web pages, add their URLs directly in `src/main.py` by appending to the `sources` list in `main()`:

```python
sources.append(r"https://example.com/your-study-page")
```

### Step 5: Run Vashist AI

```bash
cd src
python main.py
```

On the **first run**, the complete ingestion pipeline executes: document loading, image extraction, SVG conversion, captioning, chunking, embedding, and vector store population. Depending on the number of documents, the size of your files, and whether a GPU is available for captioning, this may take several minutes to complete.

On **subsequent runs**, the pipeline detects the existing `vector_store/` directory, skips ingestion entirely, and proceeds directly to the interactive Q&A loop.

**Example session:**

```
Enter Your Query: (enter Q to quit) What is contrastive learning in CLIP?
Acting as Principal Computer Vision Researcher specializing in multimodal representation learning

Contrastive learning in CLIP pairs images with their corresponding text descriptions
and trains the model to bring matching pairs closer together in a shared embedding
space while pushing non-matching pairs apart...

=== Associated References ===
data/2304.08485v2.pdf Page:3
data/NIPS-2017-attention-is-all-you-need-Paper.pdf Page:7

=== Associated Visual References ===
- Image Path: .temp-images/pdf_abc123.png
```

Enter `q` to exit the loop.

---

## Configuration Reference

All tuneable parameters across source files:

| File | Parameter / Setting | Default | Description |
|---|---|---|---|
| `config.py` | `jina_api_key` | `""` | Jina Reader AI API key |
| `config.py` | `log_level` | `"INFO"` | Python logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `config.py` | `max_retries` | `5` | Maximum number of retries for resilient operations |
| `config.py` | `cache_ttl_seconds` | `300` | Query cache time-to-live in seconds |
| `config.py` | `log_file_name` | `"logs.log"` | Path to the log output file |
| `chunking.py` | `chunk_size` | `1000` | Maximum tokens per document chunk |
| `chunking.py` | `chunk_overlap` | `300` | Token overlap between consecutive chunks |
| `embedding.py` | `model_name` | `"nomic-embed-text"` | Ollama model used for all embedding generation |
| `embedding.py` | `batch_size` | `16` | Number of texts or captions embedded per Ollama API call |
| `retriever.py` | `top_k` | `3` | Number of nearest neighbors retrieved per query |
| `retriever.py` | `score_threshold` | `0.5` | Minimum cosine similarity required to include a result |
| `captioner.py` | `model_name` | `"microsoft/git-base"` | HuggingFace model used for image captioning |
| `captioner.py` | `min_kb` | `5` | Minimum image file size in KB; smaller images are skipped |
| `captioner.py` | `min_dimension` | `500 x 500 px` | Minimum image width and height; smaller images are skipped |
| `captioner.py` | `min_new_tokens` | `20` | Minimum caption length in tokens |
| `captioner.py` | `max_new_tokens` | `100` | Maximum caption length in tokens |
| `generation.py` | `model` | `"Qwen2.5:3b"` | Ollama LLM used for multi-query, persona, and generation |
| `generation.py` | `temperature` | `0.1` | LLM sampling temperature; lower values are more deterministic |
| `vector_storage.py` | `collection_name` | `"Multi_Media_Storage"` | ChromaDB collection name |
| `vector_storage.py` | `persistent_dir` | `"vector_store"` | Directory path for ChromaDB persistent storage |

---

## Environment Variables

All environment variables are read from the `.env` file and validated through `src/config.py`. The `.env.example` file contains a template with all recognized keys.

| Variable | Required | Description |
|---|---|---|
| `JINA_API_KEY` | Yes, for URL ingestion | API key for Jina Reader AI. Required to load content from web URLs. If only using local PDFs and PPTs, this can be left empty. |
| `log_level` | No | Python logging verbosity level. Defaults to `INFO`. |
| `max_retries` | No | Maximum retry count for resilient operations. Defaults to `5`. |
| `cache_ttl_seconds` | No | Number of seconds before a cached response expires. Defaults to `300`. |
| `log_file_name` | No | File path for the log output. Defaults to `logs.log` in the working directory. |

---

## Privacy and Security

Vashist AI is designed with privacy as a first principle.

**Local Inference** -- All LLM inference (embedding generation, multi-query expansion, persona assignment, and answer generation) runs entirely through Ollama on the local machine. No query text, document content, or generated response is sent to any remote LLM API.

**Optional External Call** -- The only external network call in the core pipeline is to the Jina Reader AI API, which is used exclusively for converting web URLs into clean markdown. This call is entirely optional; if you only use local PDF and PPTX files, Jina is never contacted. The Jina API key can be left blank in that case.

**PII Protection on Input** -- Every user query is scanned by `PIIDetector` before being passed to the retriever or the LLM. Detected PII (emails, phone numbers, SSNs, credit card numbers, IPv4 addresses) is replaced with redaction tokens before further processing.

**PII Protection and Harmful Content Blocking on Output** -- Every LLM response passes through `OutPutValidator` before being displayed to the user. This layer applies PII masking and blocks responses that match patterns associated with harmful instructions.

**No Telemetry** -- There is no usage tracking, analytics, or telemetry of any kind.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Aakar Roy
