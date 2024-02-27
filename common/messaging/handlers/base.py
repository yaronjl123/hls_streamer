from aio_pika.abc import AbstractIncomingMessage


class BaseMessageHandler:
    async def handle_message(self, queue_message: AbstractIncomingMessage):
        message = self._unwrap_message(queue_message)
        await self._process_message(message)

    async def _process_message(self, message):
        raise NotImplementedError

    def _unwrap_message(self, message: AbstractIncomingMessage):
        raise NotImplementedError
