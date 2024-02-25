import asyncio
import functools
import subprocess
import tempfile

from aio_pika.abc import AbstractIncomingMessage
from dependency_injector.wiring import Provide

from common.hdfs.client import HDFSClient
from common.messaging.messages.ffmpeg import VideoChunk, FFMPEGMessage
from common.messaging.handlers.base import BaseMessageHandler
from common.dependencies import DependenciesContainer


class FFMPEGMessageHandler(BaseMessageHandler):
    def __init__(self, executor_pool, hdfs_client: HDFSClient = Provide[DependenciesContainer.hdfs_client]):
        self._executor_pool = executor_pool
        self._hdfs_client = hdfs_client
        super().__init__()

    async def _process_message(self, ffmpeg_message: FFMPEGMessage):
        with tempfile.NamedTemporaryFile(delete=False) as fp:
            data = self._hdfs_client.get_video_chunk_data(ffmpeg_message.source_video_chunk)
            fp.write(data)
            output_filename = await self._run_ffmpeg(fp.name)
            self._hdfs_client.save_video_chunk(ffmpeg_message.new_video_chunk, output_filename)
        print("finished: ", ffmpeg_message.new_video_chunk.sequence_number)

    async def _run_ffmpeg(self, input_filename,):
        output_filename = input_filename + "_output.ts"
        args = ["ffmpeg", "-i", input_filename, "-copyts", "-vf", "vflip", "-c:a", "copy", "-codec:v", "libx264", output_filename]
        loop = asyncio.get_running_loop()
        #TODO - just asyncio.run_in_thread since it starts a process in it anyway???
        ffmpeg_future = loop.run_in_executor(self._executor_pool, functools.partial(subprocess.call, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT), args)
        print("running ffmpeg task in executor .....")
        await asyncio.wait([ffmpeg_future], timeout=5)
        return output_filename

    def _extract_video_chunks_from_queue_message(self, message):
        source_video_chunk = VideoChunk.from_json(message['source_chunk'])
        new_video_chunk = VideoChunk.from_json(message['new_chunk'])
        return source_video_chunk, new_video_chunk

    def _unwrap_message(self, message: AbstractIncomingMessage):
        message_json = message.body.decode()
        return FFMPEGMessage.parse_raw(message_json)
