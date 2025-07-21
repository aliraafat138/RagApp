from fastapi import FastAPI
from routes import base,data
from helpers.config import get_settings
from motor.motor_asyncio import  AsyncIOMotorClient
from stores.vectordb.VectorDBFactory import VectorDBFactory
from stores.llm.llmProviderFactory import LLMProviderFactory

app=FastAPI()

@app.on_event("startup")
async def start_db_client():
    settings=get_settings()
    app.mongo_conn=AsyncIOMotorClient(settings.DB_URL)
    app.db_client=app.mongo_conn[settings.MONGODB_DATABASE]
    llm_provider_factory=LLMProviderFactory(settings)
    vectorDB_provider_factory=VectorDBFactory(settings)

    app.generate_client=llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generate_client.generation_model(model_id=settings.GENERATION_MODEL_ID)

    app.embedding_client=llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                        embedding_size=settings.EMBEDDING_SIZE)
    app.vectordb_client=vectorDB_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vectordb_client.connect()



@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()

app.include_router(base.base_router)
app.include_router(data.data_router)