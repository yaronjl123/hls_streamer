import asyncio
from dependency_injector.wiring import inject
from common.messaging.clients.rabbit.client import RabbitClient
from common.messaging.handlers.ffmpeg import FFMPEGMessageHandler
from common.messaging.listeners.base_listener import BaseListener


class RabbitListener(BaseListener):
    @inject
    def __init__(self, queue_name, queue_args, message_handler: FFMPEGMessageHandler):
        queue_client = RabbitClient(queue_name, queue_args)
        super().__init__(queue_name, queue_args, message_handler, queue_client)

    def start(self):
        asyncio.create_task(self._queue_listener())

    async def _queue_listener(self):
        task_futures = []
        while True:
            if len(task_futures) < 4: #TODO -configurable
                incoming_message = await self._queue_client.get()
                if incoming_message:
                    print("got from queue:", type(incoming_message))
                    task_future = await self._message_handler.handle_message(incoming_message)
                    task_futures.append(task_future)
            await asyncio.sleep(1) #needed otherwise stuck in loop and not going back to check on running events in loop
            #tODO- check for exception
            task_futures = [future for future in task_futures if not future.done()]
