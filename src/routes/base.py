from fastapi import FastAPI,APIRouter,Depends
from helpers.config import get_settings,Settings
base_router=APIRouter(
    prefix="/base"
)

@base_router.get("/welcome")
async def welcome(app_settings:Settings=Depends(get_settings)):
    app_name=app_settings.APP_NAME
    app_version=app_settings.APP_VERSION

    return{
        "appName":app_name,
        "appVersion":app_version
    }