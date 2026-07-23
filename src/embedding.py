import ollama
import time
import tqdm
class Embeddings():
    def __init__(self,model_name="nomic-embed-text"):
        self.model_name = model_name
    
    def generate_query_embeddings(self,query):
        print("Generating Query Embeddings...")
        time.sleep(1)
        response = ollama.embed(model=self.model_name, input=query)
        return response["embeddings"][0]

    def generate_text_embedding(self,chunks,batch_size=16):
        print("Generating Text Embeddings...")
        time.sleep(1)
        texts = [chunk.page_content for chunk in chunks]
        text_embedding = []
        for i in tqdm.tqdm(range(0,len(chunks),batch_size),desc="Encoding Text Chunks"):
            batch = texts[i:i+batch_size]
            response = ollama.embed(model=self.model_name,input=batch)
            text_embedding.extend(response["embeddings"])
        return text_embedding    

    def generate_caption_embedding(self,imgs,batch_size=16):
        print("Generating Visual Embeddings...")
        captions = [img["caption"] for img in imgs]
        caption_embedding = []
        for i in tqdm.tqdm(range(0,len(captions),batch_size),desc="Encoding Images Captions"):
            batch = captions[i:i+batch_size]
            response = ollama.embed(model=self.model_name,input=batch)
            caption_embedding.extend(response["embeddings"])
        return caption_embedding

# all_doc = loader.all_doc
# all_img = loader.imgs
# # print(all_img)
# # for i in all_img:
# #     print(i)
# chunks = chunking(all_doc)
# embed = Embeddings()
# img_embeddings = embed.generate_img_embedding(all_img)
# text_embeddings = embed.generate_text_embedding(all_doc)
# print(img_embeddings)
# print(text_embeddings)

