from langchain_ollama import ChatOllama

# def multi_query

def generation(retriver):
    llm = ChatOllama(
        model="Qwen2.5:3b",
        temperature=0.1
    )
    while(True):
        query = input("Enter your Question: ")
        if(query=="quit"):
            quit()
        results = retriver.retrieve(query)
        texts = results["texts"]
        images = results["images"]
        if results:
            context_textual = "\n\n".join(doc['content'] for doc in texts if doc['content'])
            context_visual = "\n\n".join(doc["caption"] for doc in images)
            role_prompt = f""" 
                    You are an expert Meta-Prompt Engine. Your sole task is to analyze the provided context (text documents and visual descriptions) and determine the single most appropriate expert persona/role an AI assistant should adopt to explain or answer questions about this material.
                    =========================================
                    <TEXT_CONTEXT>
                    {context_textual}
                    </TEXT_CONTEXT>
            
                    <VISUAL_CONTEXT>
                    {context_visual}
                    </VISUAL_CONTEXT>

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
            
                    Target Persona:"""
            response = llm.invoke(role_prompt)
            role = response.content
            print(f"Acting as {role}")            
            prompt = f"""Act as the following expert: {role}.
                    Your task is to answer the user's question based strictly on the provided textual and visual context. Maintain your expert persona throughout the explanation.
                    =========================================
                    TEXTUAL CONTEXT:
                    {context_textual}
                    VISUAL CONTEXT:
                    {context_visual}
                    =========================================
                    Question: {query}
                    Provide your expert answer as {role}:
                    """
            response = llm.invoke(prompt)
            print(response.content)
            if images:
                print("\n=== Associated Visual References ===")
                for img in images:
                    print(f"- Image Path: {img['uri']}")
        else:
            role_prompt = f""" 
                            You are an expert Meta-Prompt Engine. Your sole task is to analyze the provided context (text documents and visual descriptions) and determine the single most appropriate expert persona/role an AI assistant should adopt to explain or answer questions about this material.
                            =========================================
                            <USER_QUERY>
                            {query}
                            <USER_QUERY>
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
                        
                            Target Persona:"""

            response = llm.invoke(role_prompt)
            role = response.content
            prompt = f"""Act as the following expert: {role}.
                        Question: {query}
                        Provide your expert answer:
                        """
            response = llm.invoke(prompt)
            print(f"No context was found so LLM is using its own knowledge.{response.content}")


