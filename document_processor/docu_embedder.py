import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from pathlib import Path
from fastapi import HTTPException
import os
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)

DB_FAISS_PATH = Path(os.getenv("DB_FAISS_PATH"))
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

def document_embedder(structured_data, embedding):
    logger.info(f"Starting document embedding process with {len(structured_data) if structured_data else 0} sections")
    
    # Input validation
    if not structured_data:
        logger.error("No structured data provided for embedding")
        raise HTTPException(status_code=400, detail="No structured data provided for embedding")
    
    splits = []
    for i, section in enumerate(structured_data):
        if section and section.strip():  # Only process non-empty sections
            logger.debug(f"Processing section {i+1}/{len(structured_data)}")
            section_splits = text_splitter.split_text(section)
            # Filter out any empty splits
            valid_splits = [split for split in section_splits if split.strip()]
            splits.extend(valid_splits)
            logger.debug(f"Section {i+1} generated {len(valid_splits)} valid chunks")
        else:
            logger.warning(f"Skipping empty section {i+1}")
    
    # Final validation before creating FAISS index
    if not splits:
        logger.error("No valid text chunks generated for embedding")
        raise HTTPException(status_code=400, detail="No valid text chunks generated for embedding")
    
    logger.info(f"Creating FAISS index with {len(splits)} text chunks")
    
    try:
        db = FAISS.from_texts(splits, embedding)
        DB_FAISS_PATH.parent.mkdir(parents=True, exist_ok=True)
        db.save_local(str(DB_FAISS_PATH))
        logger.info(f"FAISS index successfully saved to {DB_FAISS_PATH}")
    except Exception as e:
        logger.error(f"Failed to create FAISS index: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create vector database: {str(e)}")