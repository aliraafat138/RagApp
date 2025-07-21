from stores.vectordb.providers import QdrantProvider
from controllers.BaseController import BaseController
from stores.vectordb.VectorDBEnums import VectorDBEnums
class VectorDBFactory:
    def __init__(self,config):
        self.config=config
        self.base_controller=BaseController()

    def create(self,provider):
        if provider==VectorDBEnums.QDRANT.value:
            return QdrantProvider(
                db_path=self.base_controller.get_database_path(db_name=self.config.VECTOR_DB_PATH),
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD
            )
        return None

