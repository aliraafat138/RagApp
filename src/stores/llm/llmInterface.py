from abc import ABC,abstractmethod
class LLMInterface(ABC):

    @abstractmethod
    def generation_model(self,model_id:str):
        pass

    @abstractmethod
    def embedding_model(self,model_id:str,embedding_size:int):
        pass

    @abstractmethod
    def generate_text(self,prompt:str,chat_history:list=[],max_output_token:int=None,temperature:float=None):
        pass

    @abstractmethod
    def embedding_text(self,text:str,document_type:str=None):  # improve quality of vectors
        pass

    @abstractmethod
    def construct_prompt(self,prompt:str,role:str):  #bt3eed seyagha el text abl me genrateText tstkhdmo
        pass