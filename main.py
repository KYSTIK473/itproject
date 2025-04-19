import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from db import create_tables, delete_tables
from rout import goida as film_router

@asynccontextmanager
async def lifespan(app: FastAPI):
   await create_tables()
   print("База готова")
   yield
   await delete_tables()
   print("База очищена")

app = FastAPI(lifespan=lifespan)
app.include_router(film_router)


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
