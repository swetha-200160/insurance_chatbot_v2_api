import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq 
from langchain_core.prompts import PromptTemplate
# from langchain.chains.conversation.memory import ConversationBufferWindowMemory
# from langchain.chains import ConversationalRetrievalChain
from langchain.retrievers import EnsembleRetriever
from langchain.chains import create_history_aware_retriever,create_retrieval_chain
from langchain_core.prompts import MessagesPlaceholder,ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain


import os
from dotenv import load_dotenv
load_dotenv()
# Constants
FAISS_DIR = os.getenv("FAISS_DIR")

# Create necessary directories
os.makedirs(FAISS_DIR, exist_ok=True)

#Insurance chatbot system prompt with anti-hallucination measures
system_prompt = """ **Role**: Insurance preauthorization advisor chatbot for CAN INSURANCE (UAE)

**ANTI-HALLUCINATION RULES** (HIGHEST PRIORITY):
1. ⚠️ ONLY use information from the provided context below
2. ⚠️ If information is NOT in the context, say "I don't have that specific information in our documents"
3. ⚠️ NEVER make up preauth details, costs, approval numbers, or medical procedures
4. ⚠️ If unsure, say "Let me connect you with our preauthorization team for accurate details"
5. ⚠️ Do NOT invent approval numbers, denial reasons, or cost information

**CORE REQUIREMENTS**:
- CONCISE: Responses must be extremely brief and to the point
- STRICTLY don't assume anything. Ask clarification questions. Don't answer with assumptions.
- STRICTLY answer ONLY based on the provided context and user queries
- STRICTLY TWO LINES MAX: First line = short answer or clarification question if clarification needed, Second line = very short follow-up or can avoid if question asked in first line

**Instructions**:
1. STRICTLY Provide ONLY information found in the context - no elaboration beyond what's given
2. STRICTLY Cut any unnecessary words, adjectives, or details
3. Keep emotional language but make it brief and efficient
4. Total response must fit in EXACTLY two short lines
5. If context doesn't contain the answer, admit it honestly

**Critical Rules**:
- For preauth questions, use enthusiastic or curious starters
- STRICTLY NEVER exceed two SHORT lines total
- NEVER fabricate information not in the context

**Context from Knowledge Base**:
{context}

**Response Examples (BRIEF but still emotional)**:
User: "what is preauthorization"
Correct response:
Preauthorization is prior approval from your insurer before getting treatment or medication.
It ensures the service is covered and medically necessary under your policy.

User: "how long does it take"
Correct response:
Standard requests take 2-5 business days, urgent cases within 24 hours.
Would you like to submit a new request?

User: "thanks"
Correct response:
Always happy to help with preauthorization questions.
Anything else you need today?

User: "my preauth was denied"
Correct response:
Let's review your denial reason together.
Could you share your request ID or Emirates ID so I can look into this?

User: "how much will be covered"
Correct response:
Coverage depends on your policy and medical necessity review.
Would you like me to check your specific preauth request status?

User: "I need surgery approval"
Correct response:
Please know we're here to help with the preauthorization process.
Do you have the procedure code and provider details ready?"""

# system_prompt = """ """
 
retriever_prompt = """Given a chat history and the latest user question:
1. Identify if the question contains ambiguities or missing information critical to providing an accurate response
2. If clarification is needed, return ONLY the specific questions needed for clarity without attempting to answer
3. If the question is complete but references chat history, reformulate it as a standalone question
4. If the question is already clear and standalone, return it unchanged
5. Never attempt to answer unclear questions - prioritize seeking clarification first"""
################## _____________________################

#############################____________________#########################

def get_embeddings_model():
    """Initialize and return the embeddings model."""
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def en_retriver(vector_store, vector_store1, temp_file:bool = False):
    """Initialize the QA chain with Groq and custom prompt."""
    # Create two retrievers with different search strategies
    retriever_1 = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 2})

    if temp_file:
        retriever_2 = vector_store1.as_retriever(search_type="similarity", search_kwargs={"k": 5})
        return EnsembleRetriever(retrievers=[retriever_1, retriever_2], weights=[0.05,0.95])
    import os

try:
    groq_api_key = os.getenv("GROQ_API_KEY")
except Exception as e:
    print("Error:", e)
    groq_api_key = None


def initialize_qa_chain(vector_store, vector_store1=None, temp_file: bool = False):
    try:
        memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            k=5,
            return_messages=True,
            output_key="answer"
        )

        history_aware_retriever = create_history_aware_retriever(
            llm,
            retriever,
            contextualize_q_prompt
        )

        question_answer_chain = create_stuff_documents_chain(
            llm,
            qa_prompt
        )

        rag_chain = create_retrieval_chain(
            history_aware_retriever,
            question_answer_chain
        )

        return rag_chain

    except Exception as e:
        print(f"Error initializing QA chain: {str(e)}")
        return None









