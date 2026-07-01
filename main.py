
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi import FastAPI, UploadFile, File, HTTPException, Request
# from pydantic import BaseModel
# from chatbot.chatapp_v2 import ChatApp
# from chatbot.chat_bot import get_embeddings_model
# from langchain_community.vectorstores import FAISS
# from typing import List
# from document_processor import pdf_processor, docu_embedder, pdfextractor_v2
# import shutil
# import os
# from pathlib import Path
# import logging
# from logging.handlers import RotatingFileHandler
# from dotenv import load_dotenv
# import sys
# load_dotenv()

# # Force stdout to use UTF-8 encoding on Windows
# if sys.platform == 'win32':
#     sys.stdout.reconfigure(encoding='utf-8')

# def setup_logging():
#     """Configure logging for the application with UTF-8 encoding"""
#     log_dir = os.getenv("log_dir")
#     os.makedirs(log_dir, exist_ok=True)

#     # Create formatters
#     detailed_formatter = logging.Formatter(
#         '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
#     )
#     simple_formatter = logging.Formatter(
#         '%(asctime)s - %(levelname)s - %(message)s'
#     )

#     # File handler with rotation (UTF-8 encoding)
#     file_handler = RotatingFileHandler(
#         os.path.join(log_dir, 'insurance_chatbot.log'),
#         maxBytes=10*1024*1024,  # 10MB
#         backupCount=5,
#         encoding='utf-8'
#     )
#     file_handler.setLevel(logging.DEBUG)
#     file_handler.setFormatter(detailed_formatter)

#     # Console handler (UTF-8 encoding)
#     console_handler = logging.StreamHandler(sys.stdout)
#     console_handler.setLevel(logging.INFO)
#     console_handler.setFormatter(simple_formatter)
    
#     # Configure root logger
#     root_logger = logging.getLogger()
#     root_logger.setLevel(logging.DEBUG)
    
#     # Clear any existing handlers to avoid duplicates
#     root_logger.handlers.clear()
    
#     # Add our handlers
#     root_logger.addHandler(file_handler)
#     root_logger.addHandler(console_handler)
    
#     # Set specific loggers to appropriate levels
#     logging.getLogger('uvicorn').setLevel(logging.INFO)
#     logging.getLogger('fastapi').setLevel(logging.INFO)
#     logging.getLogger('uvicorn.access').setLevel(logging.WARNING)

# # Initialize logging first
# setup_logging()
# logger = logging.getLogger(__name__)

# app = FastAPI()

# # Allow CORS for the frontend domain
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  
#     allow_credentials=True,
#     allow_methods=["*"], 
#     allow_headers=["*"],  
#     expose_headers=["Access-Control-Allow-Origin", "Access-Control-Allow-Private-Network"]
# )

# # Initialize embeddings and vector stores
# try:
#     logger.info("Initializing embeddings and vector stores...")
#     embeddings_model = get_embeddings_model()
#     logger.info("Embeddings model loaded successfully")
#     FAISS_DIR = os.getenv("FAISS_DIR")
#     # Load vector stores
#     vector_store = None
#     if os.path.exists(os.path.join(FAISS_DIR, "index.faiss")):
#         vector_store = FAISS.load_local(FAISS_DIR, embeddings_model, allow_dangerous_deserialization=True)
#         logger.info(f"Main vector store loaded from {FAISS_DIR}")
#     else:
#         logger.warning(f"Main vector store not found at {FAISS_DIR}")
    
#     TEMP_FAISS_DIR = os.getenv("TEMP_FAISS_DIR")
#     vector_store1 = None
#     if os.path.exists(os.path.join(TEMP_FAISS_DIR, "index.faiss")):
#         vector_store1 = FAISS.load_local(TEMP_FAISS_DIR, embeddings_model, allow_dangerous_deserialization=True)
#         logger.info(f"Temporary vector store loaded from {TEMP_FAISS_DIR}")
#     else:
#         logger.info(f"Temporary vector store not found at {TEMP_FAISS_DIR} (this is normal on first run)")
        
# except Exception as e:
#     logger.error(f"Could not load vector stores: {str(e)}", exc_info=True)
#     vector_store = None
#     vector_store1 = None


# @app.middleware("http")
# async def add_private_network_headers(request: Request, call_next):
#     response = await call_next(request)
#     response.headers["Access-Control-Allow-Private-Network"] = "true"
#     return response


# class ChatRequest(BaseModel):
#     prompt: str
#     language : str

# class Validator(BaseModel):
#     valid: bool 

# class Data:
#     temp_file = False
#     chat_history = []


# from deep_translator import GoogleTranslator

# arbic_translator = GoogleTranslator(source='en', target='ar')
# eng_translator = GoogleTranslator(source='auto', target='en')


# chat_bot = ChatApp(vector_store, vector_store1, Data.temp_file)

# @app.post("/insurance/chat")
# async def chat(request: ChatRequest):
#     if request.language == 'ar':
#         query = eng_translator.translate(request.prompt)
#     else:
#         query = request.prompt
    
#     """Endpoint to process a chat query."""
#     logger.info(f"Received chat request: {query[:100]}...")  # Log first 100 chars
    
#     try:

#         if not query:
#             logger.warning("Empty prompt received")
#             raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

#         response = chat_bot.chat(query)
#         Data.chat_history.append({'user': query, 'assistant':response})
        
#         if not response:
#             logger.error("Chat bot returned empty response")
#             raise HTTPException(status_code=500, detail="Failed to process the query.")

#         logger.info("Chat response generated successfully")
#         if request.language == 'ar':
#             response = arbic_translator.translate(response)
#             md_text = response.replace("** ", "**").replace(" **", "**")
#             processed_arabic = md_text.replace("•", "• ") 
#             return {"answer": processed_arabic}
#         else:
#             return {"answer": response}
        
#     except HTTPException as he:
#         logger.error(f"HTTP Exception in chat endpoint: {he.detail}")
#         raise he
#     except Exception as e:
#         logger.error(f"Unexpected error in chat endpoint: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


# @app.post('/insurance/document_uploader')
# async def pdf_process_engine(files: List[UploadFile] = File(...)):
#     try:
#         logger.info(f"Starting document processing for {len(files)} files")
        
#         # Log file details
#         for i, file in enumerate(files):
#             logger.info(f"File {i+1}: {file.filename}, size: {file.size if hasattr(file, 'size') else 'unknown'}")
        
#         processor = pdf_processor.PDFProcessor()
#         processed_files = await processor.process_documents(files)
#         logger.info(f"Files saved to temporary directory: {len(processed_files)} files processed")
        
#         loader = pdfextractor_v2.DoclingPDFLoader(processed_files)
#         docs = loader.load()
#         docs_list = list(docs)  # Convert to list to get count
#         logger.info(f"Loaded {len(docs_list)} documents")
        
#         text = processor.format_docs(docs_list)
#         logger.info(f"Formatted text length: {len(text)} characters")
        
#         structured_data = processor.preprocess_document(text)
#         logger.info(f"Created {len(structured_data)} structured sections")
        
#         if structured_data:
#             docu_embedder.document_embedder(structured_data, embeddings_model)
#             Data.temp_file = True
#             logger.info("Document processing completed successfully")
#             return {'message': 'Document processed successfully', 'sections_created': len(structured_data)}
#         else:
#             logger.warning("No content found in document after processing")
#             return {'message': 'No content found in document', 'sections_created': 0}
            
#     except HTTPException as he:
#         logger.error(f"HTTP Exception in pdf_process_engine: {he.detail}")
#         raise he
#     except Exception as e:
#         logger.error(f"Unexpected error in pdf_process_engine: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")


# @app.post('/insurance/remove_vb')
# async def remove_temp_vb(request: Validator):
#     try:
#         logger.info(f"Received request to remove temporary data: {request.valid}")
        
#         if request.valid:
#             removed_items = []
            
#             # Remove temporary vector store
#             if os.path.exists(TEMP_FAISS_DIR):
#                 shutil.rmtree(TEMP_FAISS_DIR)
#                 removed_items.append("temporary vector store")
#                 logger.info(f"Removed temporary vector store: {TEMP_FAISS_DIR}")
            
#             # Remove temporary documents
#             if os.path.exists('temp_docs'):
#                 shutil.rmtree('temp_docs')
#                 removed_items.append("temporary documents")
#                 logger.info("Removed temporary documents directory")
            
#             # Reset temp file flag
#             Data.temp_file = False
#             logger.info("Reset temp_file flag to False")
            
#             if removed_items:
#                 logger.info(f"Successfully cleaned up: {', '.join(removed_items)}")
#                 return {'message': f'Successfully removed: {", ".join(removed_items)}', 'temp_file': Data.temp_file}
#             else:
#                 logger.info("No temporary data found to remove")
#                 return {'message': 'No temporary data found to remove', 'temp_file': Data.temp_file}
#         else:
#             logger.warning("Invalid request to remove temporary data (valid=False)")
#             return {'message': 'Invalid request', 'temp_file': Data.temp_file}
            
#     except Exception as e:
#         logger.error(f"Error removing temporary data: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=f"Failed to remove temporary data: {str(e)}")

# @app.post('/reset')
# async def reset():
#     chat_bot.reset_session()

# @app.get("/")
# async def root():
#     """Health check endpoint"""
#     logger.info("Health check requested")
#     return {"message": "Insurance Chatbot API is running", "temp_file": Data.temp_file}


# @app.get("/health")
# async def health():
#     """Detailed health check"""
#     logger.debug("Detailed health check requested")
    
#     health_status = {
#         "status": "healthy",
#         "vector_stores": {
#             "main": vector_store is not None,
#             "temporary": vector_store1 is not None
#         },
#         "temp_file_active": Data.temp_file,
#         "directories": {
#             "main_vector_store": os.path.exists(FAISS_DIR),
#             "temp_vector_store": os.path.exists(TEMP_FAISS_DIR),
#             "temp_docs": os.path.exists('./temp_docs')
#         }
#     }
    
#     logger.info(f"Health check result: {health_status}")
#     return health_status


# if __name__ == "__main__":
#      import uvicorn
#      logger.info("Starting Insurance Chatbot API server...")
#      #uvicorn.run(app, host="0.0.0.0", port=8080)
#      uvicorn.run(app)

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from pydantic import BaseModel
from chatbot.chatapp_v2 import ChatApp
from chatbot.chat_bot import get_embeddings_model
from langchain_community.vectorstores import FAISS
from typing import List
from document_processor import pdf_processor, docu_embedder, pdfextractor_v2
import shutil
import os
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import sys
from typing import Dict, Optional
import uuid

load_dotenv()

# Force stdout to use UTF-8 encoding on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def setup_logging():
    """Configure logging for the application with UTF-8 encoding"""
    log_dir = os.getenv("log_dir")
    os.makedirs(log_dir, exist_ok=True)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # File handler with rotation (UTF-8 encoding)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'insurance_chatbot.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)

    # Console handler (UTF-8 encoding)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Add our handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set specific loggers to appropriate levels
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('fastapi').setLevel(logging.INFO)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)

# Initialize logging first
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

# Global session storage
user_sessions: Dict[str, ChatApp] = {}

def get_or_create_session(session_id: Optional[str] = None) -> tuple[str, ChatApp]:
    """Get existing session or create new one"""
    if session_id and session_id in user_sessions:
        return session_id, user_sessions[session_id]
    else:
        new_id = str(uuid.uuid4())
        new_session = ChatApp(vector_store, vector_store1, temp=False)
        user_sessions[new_id] = new_session
        logger.info(f"Created new session: {new_id}")
        return new_id, new_session

# Allow CORS for the frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
    expose_headers=["Access-Control-Allow-Origin", "Access-Control-Allow-Private-Network"]
)

# Initialize embeddings and vector stores
try:
    logger.info("Initializing embeddings and vector stores...")
    embeddings_model = get_embeddings_model()
    logger.info("Embeddings model loaded successfully")
    FAISS_DIR = os.getenv("FAISS_DIR")
    # Load vector stores
    vector_store = None
    if os.path.exists(os.path.join(FAISS_DIR, "index.faiss")):
        vector_store = FAISS.load_local(FAISS_DIR, embeddings_model, allow_dangerous_deserialization=True)
        logger.info(f"Main vector store loaded from {FAISS_DIR}")
    else:
        logger.warning(f"Main vector store not found at {FAISS_DIR}")
    
    TEMP_FAISS_DIR = os.getenv("TEMP_FAISS_DIR")
    vector_store1 = None
    if os.path.exists(os.path.join(TEMP_FAISS_DIR, "index.faiss")):
        vector_store1 = FAISS.load_local(TEMP_FAISS_DIR, embeddings_model, allow_dangerous_deserialization=True)
        logger.info(f"Temporary vector store loaded from {TEMP_FAISS_DIR}")
    else:
        logger.info(f"Temporary vector store not found at {TEMP_FAISS_DIR} (this is normal on first run)")
        
except Exception as e:
    logger.error(f"Could not load vector stores: {str(e)}", exc_info=True)
    vector_store = None
    vector_store1 = None


@app.middleware("http")
async def add_private_network_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Private-Network"] = "true"
    return response


class ChatRequest(BaseModel):
    prompt: str
    language : str
    session_id: Optional[str] = None

class Validator(BaseModel):
    valid: bool 

class Data:
    temp_file = False
    chat_history = []


from deep_translator import GoogleTranslator

arbic_translator = GoogleTranslator(source='en', target='ar')
eng_translator = GoogleTranslator(source='auto', target='en')


chat_bot = ChatApp(vector_store, vector_store1, Data.temp_file)

@app.post("/insurance/chat")
async def chat(request: ChatRequest):
    """Endpoint to process a chat query."""
    try:
        if not request.prompt:
            raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
            
        # Get or create session
        session_id, session_chatbot = get_or_create_session(request.session_id)
        
        # Process translation
        query = request.prompt
        if request.language == 'ar':
            query = eng_translator.translate(request.prompt)
        
        # Generate response
        response = session_chatbot.chat(query)
        
        if not response:
            raise HTTPException(status_code=500, detail="Failed to process the query.")

        # Translate back if Arabic
        if request.language == 'ar':
            response = arbic_translator.translate(response)
            md_text = response.replace("** ", "**").replace(" **", "**")
            processed_arabic = md_text.replace("•", "• ") 
            return {"answer": processed_arabic, "session_id": session_id}
        else:
            return {"answer": response, "session_id": session_id}
        
    except HTTPException as he:
        logger.error(f"HTTP Exception in chat endpoint: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.post('/insurance/document_uploader')
async def pdf_process_engine(files: List[UploadFile] = File(...)):
    try:
        logger.info(f"Starting document processing for {len(files)} files")
        
        # Log file details
        for i, file in enumerate(files):
            logger.info(f"File {i+1}: {file.filename}, size: {file.size if hasattr(file, 'size') else 'unknown'}")
        
        processor = pdf_processor.PDFProcessor()
        processed_files = await processor.process_documents(files)
        logger.info(f"Files saved to temporary directory: {len(processed_files)} files processed")
        
        loader = pdfextractor_v2.DoclingPDFLoader(processed_files)
        docs = loader.load()
        docs_list = list(docs)  # Convert to list to get count
        logger.info(f"Loaded {len(docs_list)} documents")
        
        text = processor.format_docs(docs_list)
        logger.info(f"Formatted text length: {len(text)} characters")
        
        structured_data = processor.preprocess_document(text)
        logger.info(f"Created {len(structured_data)} structured sections")
        
        if structured_data:
            docu_embedder.document_embedder(structured_data, embeddings_model)
            Data.temp_file = True
            logger.info("Document processing completed successfully")
            return {'message': 'Document processed successfully', 'sections_created': len(structured_data)}
        else:
            logger.warning("No content found in document after processing")
            return {'message': 'No content found in document', 'sections_created': 0}
            
    except HTTPException as he:
        logger.error(f"HTTP Exception in pdf_process_engine: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in pdf_process_engine: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")


@app.post('/insurance/remove_vb')
async def remove_temp_vb(request: Validator):
    try:
        logger.info(f"Received request to remove temporary data: {request.valid}")
        
        if request.valid:
            removed_items = []
            
            # Remove temporary vector store
            if os.path.exists(TEMP_FAISS_DIR):
                shutil.rmtree(TEMP_FAISS_DIR)
                removed_items.append("temporary vector store")
                logger.info(f"Removed temporary vector store: {TEMP_FAISS_DIR}")
            
            # Remove temporary documents
            if os.path.exists('temp_docs'):
                shutil.rmtree('temp_docs')
                removed_items.append("temporary documents")
                logger.info("Removed temporary documents directory")
            
            # Reset temp file flag
            Data.temp_file = False
            logger.info("Reset temp_file flag to False")
            
            if removed_items:
                logger.info(f"Successfully cleaned up: {', '.join(removed_items)}")
                return {'message': f'Successfully removed: {", ".join(removed_items)}', 'temp_file': Data.temp_file}
            else:
                logger.info("No temporary data found to remove")
                return {'message': 'No temporary data found to remove', 'temp_file': Data.temp_file}
        else:
            logger.warning("Invalid request to remove temporary data (valid=False)")
            return {'message': 'Invalid request', 'temp_file': Data.temp_file}
            
    except Exception as e:
        logger.error(f"Error removing temporary data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to remove temporary data: {str(e)}")

@app.post('/reset')
async def reset(request: Request):
    """Reset a specific session"""
    try:
        body = await request.json()
        session_id = body.get('session_id')
        
        if session_id and session_id in user_sessions:
            user_sessions[session_id].reset_session()
            return {"message": "Session reset successfully"}
        return {"message": "Session not found"}
    except Exception as e:
        logger.error(f"Reset error: {e}")
        raise HTTPException(status_code=500, detail="Reset failed")

@app.get("/")
async def root():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {"message": "Insurance Chatbot API is running", "temp_file": Data.temp_file}


@app.get("/health")
async def health():
    """Detailed health check"""
    logger.debug("Detailed health check requested")
    
    health_status = {
        "status": "healthy",
        "vector_stores": {
            "main": vector_store is not None,
            "temporary": vector_store1 is not None
        },
        "temp_file_active": Data.temp_file,
        "directories": {
            "main_vector_store": os.path.exists(FAISS_DIR),
            "temp_vector_store": os.path.exists(TEMP_FAISS_DIR),
            "temp_docs": os.path.exists('./temp_docs')
        },
        "active_sessions": len(user_sessions)
    }
    
    logger.info(f"Health check result: {health_status}")
    return health_status


if __name__ == "__main__":
     import uvicorn
     logger.info("Starting Insurance Chatbot API server...")
     uvicorn.run(app)