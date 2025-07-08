from fastapi import FastAPI,APIRouter,UploadFile,Request,Depends,status
from helpers.config import get_settings,Settings
from models.ProjectModel import ProjectModel
from models.AssetModel import AssetModel
from models.db_schemes import Asset
from models.enums.AssetTypeEnums import AssetTypesEnums
from controllers import DataController,ProjectController
from fastapi.responses import JSONResponse
from models import ResponseSignals
import uuid
import os 
import aiofiles
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
