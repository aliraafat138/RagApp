from ..llmInterface import LLMInterface
import logging
from ..llmEnums import CoHereEnums,DocumentTypeEnums
import cohere


class CoHereProvider(LLMInterface):
    def __init__(self,api_key:str,
                 default_input_max_character:int=1000,
                 default_generation_max_token:int=1000,
                 default_generation_temperature:int=0.1):
        
        self.api_key=api_key
        self.default_input_max_character=default_input_max_character
        self.default_generation_max_token=default_generation_max_token
        self.default_generation_temperature=default_generation_temperature

        self.generation_model_id=None
        self.embedding_model_id=None
        self.embedding_size=None
        self.client=cohere.Client(api_key=self.api_key)
        self.logger=logging.getLogger(__name__)
        self.enums=CoHereEnums


    def generation_model(self,model_id:str):

        self.generation_model_id=model_id

    def embedding_model(self,model_id:str,embedding_size:int):  
        self.embedding_model_id=model_id
        self.embedding_size=embedding_size
  
    def process_text(self,text:str):
        return text[:self.default_input_max_character].strip()
    
    
    def generate_text(self,prompt:str,chat_history: list=[] ,max_output_token:int=None,temperature:float=None):

        if not self.client:
            self.logger.error("CoHere client was not set")
            return None


        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI was not set")
            return None
        
        max_token=max_output_token if max_output_token else self.default_generation_max_token
        temperature=temperature if temperature else self.default_generation_temperature

        response=self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            max_tokens=max_token,
            message=self.process_text(prompt),
            temperature=temperature
            
        )
        if not response or not response.text:
            self.logger.error("Error while generating text with CoHere") 
            return None
        return response.text
    
    def embedding_text(self,text:str,document_type:str=None):
        if not self.client:
            self.logger.error("CoHere Client was not set")
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set")
            return None
        input_type=CoHereEnums.DOCUMENT
        if document_type==DocumentTypeEnums.query:
            input_type=CoHereEnums.QUERY

        response=self.client.embed(
            model=self.embedding_model_id,
            input_type=input_type,
            texts=[self.process_text(text)],
            embedding_types=['float'],

        )
        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding text with CoHere")
            return None
        return response.embeddings.float[0]
    
    def construct_prompt(self,prompt:str,role:str):
        return{
            "role":role,
            "text":self.process_text(prompt)
        }
           