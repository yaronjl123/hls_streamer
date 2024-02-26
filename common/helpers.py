import asyncio
import time
import urllib.request
from typing import List

import m3u8
from dependency_injector.wiring import inject, Provide
from m3u8 import Segment

from common.hdfs.client import HDFSClient
from common.messaging.clients.base_client import QueueClient
from common.messaging.clients.rabbit.client import RabbitClient
from common.messaging.messages.ffmpeg import VideoChunk, FFMPEGMessage
from common.dependencies import DependenciesContainer

PLAYLIST_HEADER = "#EXTM3U\n" \
                  "#EXT-X-START:TIME-OFFSET=0\n" \
                  "#EXT-X-PLAYLIST-TYPE:EVENT\n" \
                  "#EXT-X-VERSION:6\n" \
                  "#EXT-X-TARGETDURATION:10\n" \
                  "#EXT-X-MEDIA-SEQUENCE:0\n"
PLAYLIST_CHUNK_TEMPLATE = "#EXTINF:10.000000,\n" \
                          "{video_id}{sequence_number}.ts\n"
PLAYLIST_MISSING_CHUNK_TEMPLATE = "#EXTINF:10.000000,\n" \
                                  "#EXT-X-GAP\n" \
                                  "{video_id}{sequence_number}.ts\n"
PLAYLIST_END = "#EXT-X-ENDLIST"


def generate_live_playlist_from_available_chunks(video_id, video_chunks):
    new_playlist = PLAYLIST_HEADER

    for chunk in video_chunks:
        new_playlist += PLAYLIST_CHUNK_TEMPLATE.format(video_id=video_id, sequence_number=chunk.sequence_number)

    return new_playlist


@inject
async def publish_ffmpeg_tasks(source_video_id, new_video_id, hdfs_client: HDFSClient = Provide[DependenciesContainer.hdfs_client]):
    rabbit_client = RabbitClient("ffmpeg", {"x-max-priority": 4})
    source_video_chunks: List[VideoChunk] = hdfs_client.get_video_chunks(source_video_id)
    for source_video_chunk in source_video_chunks:
        new_video_chunk = VideoChunk(video_id=new_video_id, sequence_number=source_video_chunk.sequence_number)
        await publish_ffmpeg_task(source_video_chunk, new_video_chunk, rabbit_client)

    await rabbit_client.close_channel()


@inject
def stream_active(video_id, hdfs_client: HDFSClient = Provide[DependenciesContainer.hdfs_client]):
    last_access_time = hdfs_client.video_last_access_time(video_id)
    return (time.time() - last_access_time) < 20


@inject
async def _process_new_segment(segment: Segment, video_id, new_video_id, queue_client, hdfs_client: HDFSClient = Provide[DependenciesContainer.hdfs_client]):
    video_chunk = VideoChunk(video_id=video_id, sequence_number=segment.media_sequence)

    with urllib.request.urlopen(segment.absolute_uri) as f:
        content = f.read()
        hdfs_client.write_file(video_chunk, content)
        new_video_chunk = VideoChunk(video_id=new_video_id, sequence_number=video_chunk.sequence_number)
        await publish_ffmpeg_task(video_chunk, new_video_chunk, queue_client)


@inject
async def process_livestream(url, video_id, new_video_id):
    rabbit_client = RabbitClient("ffmpeg", {"x-max-priority": 4})
    last_sequence = 0
    while True:
        print("reloading playlist...")
        playlist = m3u8.load(url)
        segments = list(filter(lambda x: x.media_sequence > last_sequence, playlist.segments))
        for segment in segments:
            await _process_new_segment(segment, video_id, new_video_id, rabbit_client)
            last_sequence = segment.media_sequence
        if not stream_active(new_video_id):
            await rabbit_client.close_channel()
            print("no clients consuming stream, disconnecting...")
            return

        await asyncio.sleep(1)


async def publish_ffmpeg_task(source_video_chunk: VideoChunk, new_video_chunk: VideoChunk, queue_client: QueueClient):
    sequence_number = source_video_chunk.sequence_number
    priority = (4 - sequence_number) if sequence_number in range(0, 4) else 0

    message = FFMPEGMessage(source_video_chunk=source_video_chunk, new_video_chunk=new_video_chunk)
    print("publishing message: ", sequence_number)
    await queue_client.publish(message=message, priority=priority)
