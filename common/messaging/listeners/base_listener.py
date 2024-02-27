import asyncio
from aio_pika import IncomingMessage
from common.messaging.handlers.base import BaseMessageHandler


class BaseListener:
    def __init__(self, queue_client, message_handler: BaseMessageHandler, concurrent_handlers):
        self._message_handler = message_handler
        self._queue_client = queue_client
        self._number_of_handlers = concurrent_handlers
        self._handlers = None

    async def _handler(self):
        while True:
            try:
                message: IncomingMessage = await self._queue_client.get()
                if message:
                    print("got message")
                    await self._message_handler.handle_message(message)
                    await message.ack()
            except Exception as e:
                print("Got exception in message handling...: ", e)
            await asyncio.sleep(1)

    async def start(self):
        self._handlers = [asyncio.create_task(self._handler()) for _ in range(self._number_of_handlers)]
        await asyncio.gather(*self._handlers)

    def stop(self):
        for handler in self._handlers:
            handler.cancel()
        print("Stopped listener")
