import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api.v1.router import router as base_router
from app.api.v1 import auth, films, ratings, users
from app.db.setup import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    print("База готова")
    yield
    # await delete_tables()
    # print("База очищена")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Замените на ссылку на Ваш сайт
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(base_router)
app.include_router(auth.auth)
app.include_router(users.usr)
app.include_router(ratings.rtng)
app.include_router(films.flm)

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
