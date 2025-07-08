from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from models import ProcessingEnums
from langchain_community.document_loaders import TextLoader,PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ProcessController(BaseController):
    def __init__(self,project_id):
        super().__init__()
        self.project_id=project_id
        self.project_path=ProjectController().get_project_path(project_id=project_id)


    def get_file_extension(self,file_name:str):
        return os.path.splitext(file_name)[-1]
        
    def get_file_loader(self,file_name:str):
        file_ext=self.get_file_extension(file_name=file_name)    
        file_path=os.path.join(self.project_path,file_name)
        if not os.path.exists(file_path):
            return None
        if file_ext == ProcessingEnums.PDF.value:
            return PyMuPDFLoader(file_path)
        if file_ext ==ProcessingEnums.TXT.value:
            return TextLoader(file_path,encoding="utf-8")
        return None
    
    def get_file_content(self,file_name:str):
        loader=self.get_file_loader(file_name=file_name)
        if loader is None:
            return None
        return loader.load()

    def process_file_content(self,file_name:str,file_content:list,chunk_size:int=100,overlap_size:int=20):
        text_splitter=RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            overlap_size=overlap_size,
            length_function=len
        )

        file_content_text=[
            rec.page_content
            for rec in file_content
        ]

        file_content_metadata=[
            rec.metadata
            for rec in file_content
        ]

        chunks =text_splitter.create_documents(
            file_content_text,
            metadatas=file_content_metadata
        )
        return chunks
