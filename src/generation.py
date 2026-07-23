from langchain_ollama import ChatOllama

def generation(retriver):
    llm = ChatOllama(
        model="Qwen2.5:3b",
        temperature=0.1
    )
    query = input("Enter your Question: ")
    results = retriver.retrieve(query)
    texts = results["texts"]
    images = results["images"]
    if results:
        context_textual = "\n\n".join(doc['content'] for doc in texts if doc['content'])
        context_visual = "\n\n".join(doc["caption"] for doc in images)
        prompt = f"""Use the following context then answer the question accordingly
        Context: {context_textual}\n {context_visual}
        Question: {query}
        Answer: """

        response = llm.invoke(prompt)
        print(response.content)
        if images:
            print("\n=== Associated Visual References ===")
            for img in images:
                print(f"- Image Path: {img['uri']}")
    else:
        print("No content found")

