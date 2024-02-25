import time
import uuid
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette.responses import PlainTextResponse, Response
from common.hdfs.client import HDFSClient
from common.jobs.job_executor import JobExecutor
from common.messaging.messages.ffmpeg import VideoChunk
from common.helpers import generate_live_playlist_from_available_chunks, publish_ffmpeg_tasks
from common.dependencies import DependenciesContainer

router = APIRouter(prefix="/video")


@router.get('/stream/{video_id}/{filename}')
@inject
async def stream(video_id, filename, hdfs_client: HDFSClient = Depends(Provide[DependenciesContainer.hdfs_client])):
    if filename.endswith(".m3u8"):
        video_chunks = hdfs_client.get_video_chunks(video_id)
        if len(video_chunks) == 0:
            return Response(status_code=404)
        else:
            generated_playlist = generate_live_playlist_from_available_chunks(video_id, video_chunks)
            return Response(content=generated_playlist, media_type="vnd.apple.mpegURL")
    else:
        requested_video_chunk = VideoChunk.create_from_filename(video_id, filename)
        video_chunk_data = hdfs_client.get_video_chunk_data(requested_video_chunk)
        if video_chunk_data:
            return Response(content=video_chunk_data, media_type="video/MP2T")


@router.get("/local/{source_video_id}", response_class=PlainTextResponse)
@inject
async def convert_video(source_video_id: str, hdfs_client: HDFSClient = Depends(Provide[DependenciesContainer.hdfs_client])):
    generated_movie_id = str(uuid.uuid4())
    hdfs_client.create_video_directory(generated_movie_id)
    await publish_ffmpeg_tasks(source_video_id, generated_movie_id)

    return generated_movie_id


@router.get("/live", response_class=PlainTextResponse)
@inject
async def convert_live_video(playlist_url: str, hdfs_client: HDFSClient = Depends(Provide[DependenciesContainer.hdfs_client])):
    source_video_id = str(uuid.uuid4())
    new_video_id = source_video_id + str(int(time.time()))
    hdfs_client.create_video_directory(source_video_id)
    hdfs_client.create_video_directory(new_video_id)

    command = ["poetry", "run", "python"]
    args = ["common/jobs/livestream.py", "--playlist_url", playlist_url, "--source_video_id", source_video_id, "--new_video_id", new_video_id]
    job_name = new_video_id + "livestream"
    JobExecutor().create_job(job_name, "streamer", command, args)

    return new_video_id
