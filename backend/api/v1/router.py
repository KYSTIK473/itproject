from fastapi import APIRouter, Request
from starlette.responses import HTMLResponse

router = APIRouter()


@router.get("/")
async def read_root(request: Request):
    return {'sucsess': True}
