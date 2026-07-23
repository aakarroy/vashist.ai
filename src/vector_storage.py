import os
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from chromadb.utils.data_loaders import ImageLoader
import uuid


class VectorStore:
    def __init__(self,collection_name="Multi_Media_Storage",persistent_dir="vector_store"):
        print(f"Initializing Vector Storage at {persistent_dir}")
        self.collection_name = collection_name
        self.persistent_dir = persistent_dir
        self.client = None
        self.collection = None
        self._initialise_store()
    
    def _initialise_store(self):
        os.makedirs(self.persistent_dir,exist_ok=True)
        self.client = PersistentClient(
            path = self.persistent_dir,
        )
        self.collection = self.client.get_or_create_collection(
            name = self.collection_name,
            embedding_function=OpenCLIPEmbeddingFunction(),
            data_loader=ImageLoader(),
            metadata={
                "Description": "This is a multi model collection for storing textual and visual embeddings",
                "hnsw:space": "cosine"}
        )

    def add_documents(self,docs,embeddings):
        print(f"Adding documents and their embedings in vector store")
        ids = []
        metadatas = []
        document_text = []
        embedding_list = []

        for i,(doc,embed) in enumerate(zip(docs,embeddings)):
            id = f"{uuid.uuid4()}_{i}"
            ids.append(id)
            metadata = dict(doc.metadata)
            metadata["doc_index"] = i
            metadatas.append(metadata)
            document_text.append(doc.page_content)
            embedding_list.append(embed)

        self.collection.add(
                ids = ids,
                embeddings=embedding_list,
                documents=document_text,
                metadatas=metadatas
            )
            
    def add_visuals(self,imgs,embeddings):
        print(f"Adding images and their embedings in vector store")
        ids = []
        metadatas = []
        caption_text = []
        embedding_list = []
        img_paths = []

        for i,(img,embed) in enumerate(zip(imgs,embeddings)):
            id = f"{uuid.uuid4()}_{i}"
            ids.append(id)
            metadata = dict(img["metadata"])
            metadata["doc_index"] = i
            metadatas.append(metadata)
            caption_text.append(img["caption"])
            img_paths.append(img["image_path"])
            embedding_list.append(embed)

        self.collection.add(
                ids = ids,
                embeddings=embedding_list,
                documents=caption_text,
                metadatas=metadatas,
                uris = img_paths
            )


