from fastapi import FastAPI

from . import models

from . import routers

app = FastAPI()
app.include_router(routers.router)

models.create_db_and_tables()

@app.get("/")
def read_root():
    return {"Hello": "World"}
