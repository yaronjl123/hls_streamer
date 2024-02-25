from pydantic import BaseModel


class QueueClient:
    async def get(self):
        raise NotImplementedError

    async def publish(self, message: BaseModel, *args, **kwargs):
        raise NotImplementedError
