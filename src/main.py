import os
from document_loader import Loaders
from captioner import CaptionGenerator
from chunking import chunking
from embedding import Embeddings
from vector_storage import VectorStore
from retriever import Retriever
from generation import generation
from dotenv import load_dotenv
from security import PIIDetector
import logging
from config import get_settings

settings = get_settings()

logging.basicConfig(
    format = "%(asctime)s %(levelname)s : %(message)s",
    level=settings.log_level,
    handlers=[
        logging.FileHandler(settings.log_file_name,mode="w"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

load_dotenv()

def main():
    """Getting Sources"""
    PARENT_DIR = r"vashist.ai\data"
    sources = [os.path.join(PARENT_DIR,_) for _ in os.listdir(PARENT_DIR)] #list containing all the data uploaded by the user. .pdf, .pptx and urls only
    sources.append(r"https://openai.com/index/gpt-4/")
    sources.append(r"https://www.anthropic.com/news/model-context-protocol")
    sources.append(r"https://www.pinecone.io/learn/retrieval-augmented-generation/")
    sources.append(r"https://www.databricks.com/blog/llm-rag-best-practices")
    # sources.append(r"https://llava-vl.github.io/")
    # sources.append(r"https://huggingface.co/blog/vlms")
    
    if(not os.path.isdir("vector_store")):
        """Loading Data and Images from Sources"""
        loader = Loaders(sources)
        all_doc = loader.all_doc
        all_img = loader.imgs
        """Captioning all images"""
        cap = CaptionGenerator()
        captions = cap.generate_caption(all_img)
        """Chunking all textual Data"""
        chunks = chunking(all_doc)
        """Embedding all the chunks and Imgs"""
        embedding = Embeddings()
        text_embeddings = embedding.generate_text_embedding(chunks)
        img_embeddings = embedding.generate_caption_embedding(captions)
        """Storing Embeddings and Data in Vector Storage"""
        vector_store = VectorStore()
        vector_store.add_documents(chunks,text_embeddings)
        vector_store.add_visuals(captions,img_embeddings)
        """Retriever for document retrieval"""
        retriever = Retriever(vector_store,embedding)

    embedding = Embeddings()
    vector_store = VectorStore()
    retriever = Retriever(vector_store,embedding)
    piidetector = PIIDetector()
    
    # """Generation"""
    while(True):
        query = input("Enter Your Query: (enter Q to quit) ")
        if(query == 'q'):
            break
        found = piidetector.detect(query)
        if found:
            logger.warning(f"PII Detected of Type : {found.keys}")
        masked_query = piidetector.mask(query)
        generation(retriever,masked_query)

if __name__ == "__main__":
    main()
