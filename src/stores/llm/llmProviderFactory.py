from stores.llm.providers import OpenAIProvider,CoHereProvider
from .llmEnums import LLMEnums

class LLMProviderFactory:
    def __init__(self,config):
        self.config=config

    def create(self,provider):
        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(

                api_key=self.config.OPENAI_API_KEY,
                api_url=self.config.OPENAI_URL,
                default_generation_max_output_tokens=self.config. GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
                default_input_max_character=self.config.INPUT_DEFAULT_MAX_CHARACTERS
            )
        
        if provider ==LLMEnums.COHERE.value:
            return CoHereProvider(
                api_key=self.config.COHERE_API_KEY,
                default_generation_max_token=self.config. GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
                default_input_max_character=self.config.INPUT_DEFAULT_MAX_CHARACTERS
            )
        
        return None