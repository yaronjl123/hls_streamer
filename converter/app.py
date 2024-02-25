from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from common.messaging.handlers.ffmpeg import FFMPEGMessageHandler
from common.messaging.listeners.rabbit_listener import RabbitListener
from common.dependencies import DependenciesContainer


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = DependenciesContainer()
    container.wire(modules=["common.messaging.handlers.ffmpeg", "common.messaging.clients.rabbit.client"])
    container.config.from_yaml("./config.yml")
    # container.config.from_yaml("../debug.yml")

    pool = ProcessPoolExecutor(max_workers=4)
    ffmpeg_message_listener = RabbitListener("ffmpeg", {"x-max-priority": 4}, FFMPEGMessageHandler(executor_pool=pool))
    ffmpeg_message_listener.start()

    yield


app = FastAPI(lifespan=lifespan)


if __name__ == '__main__':
    uvicorn.run(app="app:app", host="0.0.0.0", port=5001)