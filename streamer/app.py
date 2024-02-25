import uvicorn
from starlette.templating import Jinja2Templates
from fastapi import FastAPI, Request

from routers.video import router
from common.dependencies import DependenciesContainer

app = FastAPI()
app.include_router(router)

templates = Jinja2Templates(directory="templates")

container = DependenciesContainer()
container.wire(modules=["routers.video", "common.messaging.clients.rabbit.client"])
container.config.from_yaml("./config.yml")
# container.config.from_yaml("../debug.yml")


@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html",context={"request": request})


@app.get('/live')
def live(request: Request):
    return templates.TemplateResponse("live.html",context={"request": request})


if __name__ == '__main__':
    uvicorn.run(app="app:app", host="0.0.0.0", port=5000)
