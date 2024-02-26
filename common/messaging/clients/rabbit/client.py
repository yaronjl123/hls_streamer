import aio_pika
from aio_pika import IncomingMessage
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel

from common.dependencies import DependenciesContainer
from common.messaging.clients.base_client import QueueClient
from common.messaging.clients.rabbit.connection import RabbitConnection


class RabbitClient(QueueClient):
    @inject
    def __init__(self, queue_name, queue_args, connection: RabbitConnection = Provide[DependenciesContainer.rabbit_connection]):
        self._queue_name = queue_name
        self._queue_args = queue_args
        self._connection = connection
        self._queue = None

    async def _get_queue(self):
        if not self._queue:
            self._queue = await self._connection.declare_queue(self._queue_name, self._queue_args)
        return self._queue

    async def get(self) -> IncomingMessage:
        queue = await self._get_queue()
        return await queue.get(fail=False)

    async def publish(self, message: BaseModel, priority=0, routing_key=None):
        routing_key = routing_key or self._queue_name
        queue = await self._get_queue()

        await queue.channel.default_exchange.publish(
            aio_pika.Message(
                body=message.model_dump_json().encode(),
                priority=priority
            ),
            routing_key=routing_key
        )

    async def close_channel(self):
        if self._queue:
            await self._queue.channel.close()
