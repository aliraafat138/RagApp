from .BaseController import BaseController
from models.db_schemes import Project,DataChunk
from stores.llm.llmEnums import DocumentTypeEnums
from stores.llm.llmEnums import OpenAIEnums
from typing import List
import json
class NLPController(BaseController):
    def __init__(self,vectordb_client,embedding_client,generation_client,template_parser):
        super().__init__()

        self.vectordb_client=vectordb_client
        self.embedding_client=embedding_client
        self.generation_client=generation_client
        self.template_parser=template_parser

    def create_collection_name(self,project_id:str):
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self,project:Project):
        collection_name=self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)
    
    def get_vector_db_collection_info(self,project:Project):
        collection_name=self.create_collection_name(project_id=project.project_id)
        collection_info=self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.loads(
            json.dumps(collection_info,default=lambda x:x.__dict__)
        )
    
    def index_into_vector_db(self,project:Project,chunks:List[DataChunk],chunks_ids: List[int],do_reset:bool=False):
        collection_name=self.create_collection_name(project_id=project.project_id)
        texts=[ c.chunk_text for c in chunks]
        metadata=[c.chunk_metadata for c in chunks]
        vectors=[self.embedding_client.embedding_text(text=text,document_type=DocumentTypeEnums.document.value)
            for text in texts
        ]

        _=self.vectordb_client.create_collection(collection_name=collection_name,
                                                 embedding_size=self.embedding_client.embedding_size,
                                                 do_reset=do_reset)
        
        _=self.vectordb_client.insert_many(collection_name=collection_name,
                                           metadata=metadata,
                                           texts=texts,
                                           vectors=vectors,
                                           record_ids=chunks_ids)
        return True
    
    def search_vectordb_collection(self,project:Project,text:str,limit:int=5):
        collection_name=self.create_collection_name(project_id=project.project_id)
        vector=self.embedding_client.embedding_text(text=text,document_type=DocumentTypeEnums.query.value)
        if not vector or len(vector)==0:
            return False
        
        result=self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )
        if not result:
            return False
        
        return result
    def answer_rag_question(self, project: Project, query: str, limit: int = 10):
        
        answer, full_prompt, chat_history = None, None, None

        # step1: retrieve related documents
        retrieved_documents = self.search_vectordb_collection(
            project=project,
            text=query,
            limit=limit,
        )

        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer, full_prompt, chat_history
        
        # step2: Construct LLM prompt
        system_prompt = self.template_parser.get("rag", "system_prompt")

        documents_prompts = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                    "doc_num": idx + 1,
                    "chunk_text": doc.text,
            })
            for idx, doc in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get("rag", "footer_prompt",{
            "query":query
        })

        # step3: Construct Generation Client Prompts
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]

        full_prompt = "\n\n".join([ documents_prompts,  footer_prompt])

        # step4: Retrieve the Answer
        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history