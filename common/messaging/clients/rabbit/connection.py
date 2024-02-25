import aio_pika


class RabbitConnection:
    def __init__(self, connection_url):
        self._connection_url = connection_url
        self._connection = None

    async def _get_connection(self):
        if not self._connection or self._connection.is_closed:
            await self._connect()
        return self._connection

    async def _connect(self):
        self._connection = await aio_pika.connect_robust(self._connection_url)

    async def declare_queue(self, queue_name, queue_args):
        connection = await self._get_connection()
        channel: aio_pika.abc.AbstractChannel = await connection.channel()

        return await channel.declare_queue(queue_name, arguments=queue_args)
