import asyncio
import functools

from aio_pika.abc import AbstractIncomingMessage


class BaseMessageHandler:
    async def handle_message(self, queue_message: AbstractIncomingMessage):
        message = self._unwrap_message(queue_message)
        task_future = asyncio.create_task(self._process_message(message))
        task_future.add_done_callback(functools.partial(self._ack_message, queue_message))
        return task_future

    async def _process_message(self, message):
        raise NotImplementedError

    def _ack_message(self, message: AbstractIncomingMessage, done_future):
        asyncio.create_task(message.ack())

    def _unwrap_message(self, message: AbstractIncomingMessage):
        raise NotImplementedError
