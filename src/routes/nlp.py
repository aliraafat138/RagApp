from fastapi import FastAPI,APIRouter,Request,status
from fastapi.responses import JSONResponse
from routes.schemes.nlp import pushRequest,searchRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.enums.ResponseEnums import ResponseSignals 
from controllers import NLPController
import logging
from helpers.config import get_settings
settings=get_settings()
logger = logging.getLogger('uvicorn.error')
nlp_router=APIRouter(
    prefix="/nlp"
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request:Request,project_id:str,push_request:pushRequest):
    project_model=await ProjectModel.create_instance(db_client=request.app.db_client)
    project=await project_model.get_project_or_create_one(project_id=project_id)
    chunk_model=await ChunkModel.create_instance(db_client=request.app.db_client)


    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal":ResponseSignals.PROJECT_NOT_FOUND_ERROR.value
            }
        )
    nlp_controller =NLPController(
        vectordb_client=request.app.vectordb_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generate_client,
        template_parser=request.app.template_parser
    )

    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0

    while has_records:
        page_chunks = await chunk_model.get_project_chunks(project_id=project.id, page=page_no)
        if len(page_chunks):
            page_no += 1
        
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunks_ids =  list(range(idx, idx + len(page_chunks)))
        idx += len(page_chunks)
        
        is_inserted = nlp_controller.index_into_vector_db(
            project=project,
            chunks=page_chunks,
            do_reset=push_request.do_reset,
            chunks_ids=chunks_ids
        )

        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignals.INSERT_INTO_VECTORDB_ERROR.value
                }
            )
        
        inserted_items_count += len(page_chunks)
        
    return JSONResponse(
        content={
            "signal": ResponseSignals.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        }
    )



@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request:Request,project_id:str):
    project_model=await ProjectModel.create_instance(db_client=request.app.db_client)
    project=await project_model.get_project_or_create_one(project_id=project_id)

    nlp_controller =NLPController(
        vectordb_client=request.app.vectordb_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generate_client,
        template_parser=request.app.template_parser
    )
    collection_info=nlp_controller.get_vector_db_collection_info(project=project)
    return JSONResponse(
          content={
            "signal": ResponseSignals.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info
        }
    )

@nlp_router.post("/index/search/{project_id}")
async def search_project_index(request:Request,project_id:str,search_request:searchRequest):
    project_model=await ProjectModel.create_instance(db_client=request.app.db_client)
    project=await project_model.get_project_or_create_one(project_id=project_id)
    nlp_controller =NLPController(
        vectordb_client=request.app.vectordb_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generate_client,
        template_parser=request.app.template_parser
    )

    results=nlp_controller.search_vectordb_collection(
        project=project,
        text=search_request.text,
        limit=search_request.limit
    )

    if not results:
        return JSONResponse(
             content={
            "signal": ResponseSignals.VECTORDB_SEARCH_ERROR.value,
           
        }
        )
    
    return JSONResponse(
        content={
            "signal":ResponseSignals.VECTORDB_SEARCH_SUCCESS.value,
             "results": [result.dict() for result in results]
        }
    )


@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(request: Request, project_id: str, search_request: searchRequest):
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)


    nlp_controller = NLPController(
        generation_client=request.app.generate_client,
        embedding_client=request.app.embedding_client,
        vectordb_client=request.app.vectordb_client,
        template_parser=request.app.template_parser
    )

    answer, full_prompt, chat_history = nlp_controller.answer_rag_question(
        project=project,
        query=search_request.text,
        limit=search_request.limit
    )

    if not answer:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignals.RAG_ANSWER_ERROR.value}
        )
    
    return JSONResponse(
        content={
            "signal": ResponseSignals.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history
        }
    )
