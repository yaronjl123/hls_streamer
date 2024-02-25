from pydantic import BaseModel
from common.models.video_chunk import VideoChunk


class FFMPEGMessage(BaseModel):
    source_video_chunk: VideoChunk
    new_video_chunk: VideoChunk
