from llm.bedrockLLM import hr_llm

def hr_rag_response(index, question: str):
    rag_llm = hr_llm()
    return index.query(question=question, llm=rag_llm)