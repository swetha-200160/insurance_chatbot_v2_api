# from typing import Iterator, Union, List
# from docling.datamodel.base_models import InputFormat
# from langchain_core.document_loaders import BaseLoader
# from langchain_core.documents import Document as LCDocument
# from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions
# from docling.document_converter import DocumentConverter, PdfFormatOption
# import fitz 

# class DoclingPDFLoader(BaseLoader):
#     def __init__(self, file_paths: Union[str, List[str]]) -> None:
#         self._file_paths = [file_paths] if isinstance(file_paths, str) else file_paths
#         self._converter = DocumentConverter()
#         self.pipeline_options = PdfPipelineOptions(
#             do_ocr=True,
#             do_table_structure=True,
#             table_structure_options={'do_cell_matching': True}
#         )
#         self.ocr_options = EasyOcrOptions(force_full_page_ocr=True)
#         self.pipeline_options.ocr_options = self.ocr_options

#     def is_scanned_pdf(self, file_path: str) -> bool:
#         try:
#             doc = fitz.open(file_path)
#             text_content = ""
#             pages_to_check = min(3, doc.page_count)

#             for page_num in range(pages_to_check):
#                 text_content += doc[page_num].get_text().strip()

#             doc.close()
#             return len(text_content) < 100
#         except Exception as e:
#             print(f"Error checking PDF type for {file_path}: {e}")
#             return False

#     def lazy_load(self, lcdocument: bool = True) -> Iterator[Union[LCDocument, str]]:
#         for source in self._file_paths:
#             if self.is_scanned_pdf(source):
#                 self._converter = DocumentConverter(
#                     format_options={
#                         InputFormat.PDF: PdfFormatOption(
#                             pipeline_options=self.pipeline_options,
#                         )
#                     }
#                 )
#             else:
#                 self._converter = DocumentConverter()

#             try:
#                 dl_doc = self._converter.convert(source).document
#                 text = dl_doc.export_to_markdown()
#                 if lcdocument:
#                     yield LCDocument(page_content=text)
#                 else:
#                     yield text
#             except Exception as e:
#                 print(f"Error processing {source}: {e}")

import logging
from typing import Iterator, Union, List
from docling.datamodel.base_models import InputFormat
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document as LCDocument
from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
import fitz

logger = logging.getLogger(__name__)

class DoclingPDFLoader(BaseLoader):
    def __init__(self, file_paths: Union[str, List[str]]) -> None:
        self._file_paths = [file_paths] if isinstance(file_paths, str) else file_paths
        self._converter = DocumentConverter()
        self.pipeline_options = PdfPipelineOptions(
            do_ocr=True,
            do_table_structure=True,
            table_structure_options={'do_cell_matching': True}
        )
        self.ocr_options = EasyOcrOptions(force_full_page_ocr=True)
        self.pipeline_options.ocr_options = self.ocr_options
        logger.info(f"Initialized DoclingPDFLoader with {len(self._file_paths)} files")

    def is_scanned_pdf(self, file_path: str) -> bool:
        try:
            logger.debug(f"Checking if PDF is scanned: {file_path}")
            doc = fitz.open(file_path)
            text_content = ""
            pages_to_check = min(3, doc.page_count)
            
            for page_num in range(pages_to_check):
                text_content += doc[page_num].get_text().strip()
            
            doc.close()
            is_scanned = len(text_content) < 100
            logger.info(f"PDF {file_path} is {'scanned' if is_scanned else 'text-based'} (text length: {len(text_content)})")
            return is_scanned
            
        except Exception as e:
            logger.error(f"Error checking PDF type for {file_path}: {e}")
            return False

    def lazy_load(self, lcdocument: bool = True) -> Iterator[Union[LCDocument, str]]:
        for source in self._file_paths:
            logger.info(f"Processing document: {source}")
            
            if self.is_scanned_pdf(source):
                logger.info(f"Using OCR pipeline for scanned PDF: {source}")
                self._converter = DocumentConverter(
                    format_options={
                        InputFormat.PDF: PdfFormatOption(
                            pipeline_options=self.pipeline_options,
                        )
                    }
                )
            else:
                logger.info(f"Using standard pipeline for text-based PDF: {source}")
                self._converter = DocumentConverter()
            
            try:
                dl_doc = self._converter.convert(source).document
                text = dl_doc.export_to_markdown()
                logger.info(f"Successfully extracted {len(text)} characters from {source}")
                
                if lcdocument:
                    yield LCDocument(page_content=text)
                else:
                    yield text
                    
            except Exception as e:
                logger.error(f"Error processing {source}: {e}")
                # You might want to raise the exception or yield an empty document
                # depending on your error handling strategy