from fastapi import FastAPI,APIRouter,UploadFile,Request,Depends,status
from helpers.config import get_settings,Settings
from models.ProjectModel import ProjectModel
from models.AssetModel import AssetModel
from models.ChunkModel import ChunkModel
from models.db_schemes import Asset
from models.enums.AssetTypeEnums import AssetTypesEnums
from controllers import DataController,ProjectController,ProcessController
from fastapi.responses import JSONResponse
from models import ResponseSignals
import uuid
import os 
import aiofiles
from models.ChunkModel import DataChunk
import logging
from .schemes.data import processRequest
logger=logging.getLogger("uvicorn.error")
data_router=APIRouter(
    prefix="/data"
)
@data_router.post("/upload/{project_id}")
async def upload_file(request:Request,project_id:str,file:UploadFile,app_settings:Settings=Depends(get_settings)):
    project_model= await ProjectModel.create_instance(db_client=request.app.db_client)
    project=await project_model.get_project_or_create_one(project_id=project_id)
    is_valid,signal_result=DataController().validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal":signal_result}
        )
    
    project_dir_path=ProjectController().get_project_path(project_id=project_id)
    # Extract the original file extension (includes the dot, e.g. ".pdf")
    file_ext = os.path.splitext(file.filename)[-1]

    # Generate an 8-character random ID
    file_id = uuid.uuid4().hex[:8]

    # Create the new filename: 8-char ID + extension
    file_name = f"{file_id}{file_ext}"

    # Full file path
    file_path = os.path.join(project_dir_path, file_name)

   
    try:
        async with  aiofiles.open(file_path,"wb") as f:
         while chunk:= await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
            await f.write(chunk)


    except Exception as e:  
        return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"signal,",ResponseSignals.FILE_UPLOADED_FAIL.value}
        )


    asset_model=await AssetModel.create_instance(request.app.db_client)
    asset_resources= Asset(
        asset_project_id=project.id,
        asset_type=AssetTypesEnums.FILE.value,
        asset_name=file_name,
        asset_size=os.path.getsize(file_path)
    )

    asset_record=await asset_model.create_asset(asset=asset_resources)


    return JSONResponse(content={
        "signal":ResponseSignals.FILE_UPLOADED_SUCCESS.value,
        "file_name":str(asset_record.id),
        
        })

@data_router.post("/process/{project_id}")
async def process_endpoint(request:Request,project_id:str,process_request:processRequest):
  chunk_size=process_request.chunk_size
  overlap_size=process_request.overlap_size
  do_reset=process_request.do_reset
  project_model=await ProjectModel.create_instance(db_client=request.app.db_client)
  project=await project_model.get_project_or_create_one(project_id=project_id)
  process_controller = ProcessController(project_id=project_id)
  asset_model=await AssetModel.create_instance(db_client=request.app.db_client)
  project_file_names={}
  if process_request.file_name:
    asset_record=await asset_model.get_asset_record(
      asset_project_id=project.id,
      asset_name=process_request.file_name
    )
    if asset_record is None:
      return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
          "signal":ResponseSignals.NO_FILE_NAME.value}
      )
    project_file_names={asset_record.id:asset_record.asset_name}
  else:
  
    project_files=await asset_model.get_all_assets(
      asset_project_id=project.id,
      asset_type=AssetTypesEnums.FILE.value
    )
    project_file_names={
      record.id:record.asset_name
      for record in project_files}
    
    if len(project_file_names) ==0:
      return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
          "signal":ResponseSignals.NO_FILES.value
        }
      )
  
 
  no_records=0
  no_files=0
  chunk_model= await ChunkModel.create_instance(request.app.db_client)
  if do_reset==1:
      _=await chunk_model.delete_chunks_by_project_id(project_id=project.id)
  for asset_id,file_name in project_file_names.items():

    file_content=process_controller.get_file_content(file_name=file_name)
    if file_content is None:
      logger.error(f"Error Processing File")
      continue

    file_chunks=process_controller.process_file_content(
      file_content=file_content,
      file_name=file_name,
      chunk_size=chunk_size,
      overlap_size=overlap_size
    )

    if file_chunks is None or len(file_chunks)==0:
      return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"signal":ResponseSignals.FILE_PROCESS_FAIL}
        
      )
    
    file_chunks_records=[
      DataChunk(
        chunk_text=chunk.page_content,
        chunk_metadata=chunk.metadata,
        chunk_order=i+1,
        chunk_project_id=project.id,
        chunk_asset_id=asset_id
      )

      for i,chunk in enumerate(file_chunks)
    ]

 
    
    no_records+=await chunk_model.insert_many_chunks(chunks=file_chunks_records)
    no_files+=1

  return JSONResponse(
    content={
      "signal":ResponseSignals.FILE_PROCESS_SUCCESS.value,
      "inserted_chunks":no_records,
      "processed_files":no_files
    }
    )
