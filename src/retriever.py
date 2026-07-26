import time
class Retriever:
    def __init__(self,vector_store,embedding):
        self.vector_store = vector_store
        self.embedding = embedding

    def retrieve(self,query,top_k=3,score_threshold=0.5):
        print(f"Query: {query}\n Top_k: {top_k}\n Score Threshold: {score_threshold}")
        time.sleep(1)
        query_embedding = self.embedding.generate_query_embeddings([query])
        print(f"Retrieving docs...")
        time.sleep(1)
        results = self.vector_store.collection.query(
            query_embedding,
            n_results=top_k,
            include = ["uris","documents","distances","metadatas"]
        )
        retrived_docs = {
            "texts" : [],
            "images": []
        }

        if(results['documents'] and results["documents"][0]):
            documents = results["documents"][0]
            uris = results["uris"][0]
            distances = results["distances"][0]
            metadatas = results["metadatas"][0]
            ids = results["ids"][0]

            for (doc,uri,dist,metadata,id) in (zip(documents,uris,distances,metadatas,ids)):
                similarity_score = 1-dist
                if(similarity_score > score_threshold):
                    if uri:
                        retrived_docs["images"].append({
                            "id" : id,
                            "distance" : dist,
                            "metadata" : metadata,
                            "uri" : uri,
                            "caption": doc
                        })
                        print(f"for: {id} -> {uri} images retrieved.")
                    elif doc:
                        retrived_docs["texts"].append({
                            "id" : id,
                            "distance" : dist,
                            "metadata" : metadata,
                            "content" : doc,
                        })
            print(f"{len(retrived_docs["images"])} images retrieved\n{len(retrived_docs["texts"])} docs retrieved.")
            return retrived_docs
        else:
            print(f"No related documents found.")
            return retrived_docs
