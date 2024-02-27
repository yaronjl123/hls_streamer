from dependency_injector.wiring import inject
from common.messaging.clients.rabbit.client import RabbitClient
from common.messaging.handlers.ffmpeg import FFMPEGMessageHandler
from common.messaging.listeners.base_listener import BaseListener


class RabbitListener(BaseListener):
    @inject
    def __init__(self, queue_name, queue_args, message_handler: FFMPEGMessageHandler):
        queue_client = RabbitClient(queue_name, queue_args)
        super().__init__(queue_client, message_handler, concurrent_handlers=4)
