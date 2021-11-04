from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter(prefix="/healthcheck")


@router.get("/ping")
async def ping():
    return Response("ok", status_code=200)
