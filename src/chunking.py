import time
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer

logger = logging.getLogger(__name__)

def chunking(all_doc):
    # print(f"Chunking {len(all_doc)} docs to chunks according to Qwen Tokens..")
    logger.info(f"Chunking {len(all_doc)} docs to chunks according to Qwen Tokens..")
    model_name = "Qwen/Qwen2.5-3B"
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
    except Exception as e:
        logger.critical("Chunking Model Not Loaded.")
    text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        tokenizer = tokenizer,
        chunk_size=1000,
        chunk_overlap=300,
        separators = ["\n\n","\n"," ",""]
    )
    chunks = text_splitter.split_documents(all_doc)
    # print(f"Converted {len(all_doc)} docs to {len(chunks)} chunks")
    logger.info(f"Converted {len(all_doc)} docs to {len(chunks)} chunks")
    time.sleep(1)
    return chunks
