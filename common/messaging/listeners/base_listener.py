from common.messaging.handlers.base import BaseMessageHandler


class BaseListener:
    def __init__(self, queue_name, queue_args, message_handler: BaseMessageHandler, queue_client):
        self._queue_name = queue_name
        self._queue_args = queue_args
        self._message_handler = message_handler
        self._queue_client = queue_client

    def start(self):
        raise NotImplementedError
