import os
import shutil
from pathlib import Path
import warnings
import re
from typing import List,Iterable
from langchain_core.documents import Document as LCDocument
import logging
import os
from dotenv import load_dotenv
load_dotenv()

warnings.filterwarnings("ignore", message=".*clean_up_tokenization_spaces.*")
logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self):
        self.TMP_DIR = Path(os.getenv("TMP_DIR"))

    def format_docs(self,docs: Iterable[LCDocument]) -> str:
        return "\n\n".join(doc.page_content for doc in docs)



    def preprocess_document(self, text: str) -> List[str]:
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL).strip()
        text = re.sub(r'\s+', ' ', text)
        
        logger.debug(f"Processed text before splitting: {text[:200]}...")  # First 200 chars
        
        # Try to split by headers first
        sections = re.split(r'(#{2,3} .+)', text)
        logger.debug(f"Sections after splitting: {len(sections)} sections found")
        
        structured_sections = []
        for i in range(1, len(sections), 2):
            header = sections[i].strip()
            content = sections[i + 1].strip() if i + 1 < len(sections) else ''
            if header or content:
                structured_sections.append(f"{header}\n{content}")
        
        # Filter out empty sections
        structured_sections = [section for section in structured_sections if section.strip()]
        
        # If no structured sections found, return the original text as a single section
        if len(structured_sections) < 1:
            logger.warning("No structured sections found using header splitting")
            # Instead of returning raw sections, return the cleaned text
            if text.strip():  # Only if there's actual content
                logger.info("Returning original text as single section")
                return [text.strip()]
            else:
                logger.warning("No valid content found in document")
                return []  # Return empty list if no content
        
        logger.info(f"Successfully created {len(structured_sections)} structured sections")
        return structured_sections
        
    # async def process_documents(self, uploaded_files) -> str:        
    #     if self.TMP_DIR.exists():
    #         shutil.rmtree(self.TMP_DIR)
    #     self.TMP_DIR.mkdir(parents=True, exist_ok=True)
    
    #     # Save uploaded files
    #     processed_files = []
    #     for idx, uploaded_file in enumerate(uploaded_files):
    #         temp_path = self.TMP_DIR / f"doc_{idx}.pdf"
    #         with open(temp_path, 'wb') as temp_file:
    #             data = await uploaded_file.read()
    #             temp_file.write(data)
    #         processed_files.append(temp_path)
    #     return processed_files
    async def process_documents(self, uploaded_files) -> str:        
        if self.TMP_DIR.exists():
            shutil.rmtree(self.TMP_DIR)
        self.TMP_DIR.mkdir(parents=True, exist_ok=True)
    
        # Save uploaded files and extract text
        processed_texts = []
        for idx, uploaded_file in enumerate(uploaded_files):
            temp_path = self.TMP_DIR / f"doc_{idx}.pdf"
            
            # Save the uploaded PDF
            with open(temp_path, 'wb') as temp_file:
                data = await uploaded_file.read()
                temp_file.write(data)

            processed_texts.append(temp_path)

        return processed_texts