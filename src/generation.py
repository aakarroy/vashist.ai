from langchain_ollama import ChatOllama
import json

llm = ChatOllama(
        model="Qwen2.5:3b",
        temperature=0.1
    )

def multi_query(query:str):
    multi_query_prompt = f"""
        You are an AI assistant tasked with optimizing search queries for a vector-based Retrieval-Augmented Generation (RAG) system. 
        Your goal is to take a single user query and break it down or generate 3 distinct alternative versions of it. These variations should:
        1. Rephrase the query using different vocabulary, industry synonyms, or related terms.
        2. Address different angles or semantic interpretations of the original query.
        3. Keep the original intent intact while optimizing for semantic document retrieval.
        =========================================
        <ORIGINAL_USER_QUERY>
        {query}
        <ORIGINAL_USER_QUERY>
        =========================================
        OUTPUT FORMAT:
        Return strictly a valid JSON object with a single key "queries" containing an array of exactly 3 string queries not any more than that. Do not include any intro, explanation, or markdown backticks outside the JSON.

        Example Output:
        "queries": [
            "First query variation here",
            "Second query variation here",
            "Third query variation here"
        ]
        """
    reponse = llm.invoke(multi_query_prompt)
    data = json.loads(reponse.content)
    sub_queries = data.get("queries",[])
    all_queries = [query] + sub_queries
    print(all_queries)
    return list(set([all_queries[0],all_queries[1],all_queries[2]]))    

def generation(retriver):
    while(True):
        query = input("Enter your Question: ")
        if(query=="quit"):
            quit()
        all_queries = multi_query(query)
        texts = []
        images = []
        for _ in all_queries:
            results = retriver.retrieve(query)
            texts.extend(results["texts"])
            images.extend(results["images"])
        if (len(texts)!=0 or len(images)!=0) :
            context_textual = "\n\n".join(doc['content'] for doc in texts if doc['content'])
            context_visual = "\n\n".join(doc["caption"] for doc in images)
            role_prompt = f""" 
                    You are an expert Meta-Prompt Engine. Your sole task is to analyze the provided context (text documents and visual descriptions) and determine the single most appropriate expert persona/role an AI assistant should adopt to explain or answer questions about this material.
                    =========================================
                    <USER_QUERY>
                    {query}
                    </USER_QUERY>
                    =========================================
                    INSTRUCTIONS:
                    1. Analyze the technical depth, domain (e.g., Embedded Electronics, Medical Diagnostics, Database Engineering, Legal Analysis), and the user's query level.
                    2. Formulate a specific, highly qualified expert persona that possesses deep authority on this subject.
                    3. Keep the output CONCISE (1 sentence max or a job title with key specialization).
                    4. OUTPUT FORMAT: Return ONLY the persona description. Do NOT include intro/outro text, conversational filler, or formatting quotes.
            
                    EXAMPLE OUTPUTS:
                    - Senior Embedded Systems Architect specializing in low-power microcontrollers and sensor arrays
                    - University Professor in Relational Database Management Systems and SQL Optimization
                    - Principal Computer Vision Engineer specializing in edge model deployment
                    - AI Expert
            
                    Target Persona:"""
            response = llm.invoke(role_prompt)
            role = response.content
            print(f"Acting as {role}")            
            prompt = f"""Act as the following expert: {role}.
                    Your task is to answer the user's question based strictly on the provided textual and visual context. Maintain your expert persona throughout the explanation.
                   STRICT FORMATTING & TONE RULES:
                    1. Start your response IMMEDIATELY with the answer. 
                    2. NEVER use greetings, pleasantries, or meta-commentary (e.g., do NOT say "As an expert...", "Sure!", or "Based on the context...").
                    3. DO NOT restate your role, title, or the user's question.
                    4. Maintain a strictly technical, concise, and analytical tone.
                    =========================================
                    TEXTUAL CONTEXT:
                    {context_textual}
                    VISUAL CONTEXT:
                    {context_visual}
                    =========================================
                    Question: {query}
                    Provide your expert answer:
                    """
            response = llm.invoke(prompt)
            print(response.content)
            if(texts):
                print("\n=== Associated References ===")
                for i in texts:
                    if("page" in i["metadata"]):  
                        print(f"{i["metadata"]["source"]} Page:{i["metadata"]["page"]}")
                    else:
                         print(f"{i["metadata"]["source"]}")
            if images:
                print("\n=== Associated Visual References ===")
                for img in images:
                    print(f"- Image Path: {img['uri']}")
        else:
            print(f"No context was found so LLM is using its own knowledge.")
            prompt = f"""
                        Question: {query}
                        Provide your expert answer:
                        """
            response = llm.invoke(prompt)
            print(response.content)
            


