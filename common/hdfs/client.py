from hdfs import InsecureClient
from common.messaging.messages.ffmpeg import VideoChunk
import time


class HDFSClient:
    HDFS_VIDEOS_DIR = "/videos/"

    def __init__(self, connection_url):
        self._client = InsecureClient(connection_url, user='root')

    def get_video_chunk_data(self, video_chunk):
        self._touch_video_directory(video_chunk.video_id)
        path = self.HDFS_VIDEOS_DIR + video_chunk.video_id + "/" + video_chunk.filename
        return self._read_file(path)

    def get_video_chunks(self, video_id):
        self._touch_video_directory(video_id)
        filenames = self._client.list(self.HDFS_VIDEOS_DIR + video_id)
        video_filenames = filter(lambda x: x.endswith(".ts"), filenames)
        video_chunks = [VideoChunk.create_from_filename(video_id, filename) for filename in video_filenames]
        return sorted(video_chunks)

    def create_video_directory(self, video_id):
        path = self.HDFS_VIDEOS_DIR + video_id
        self._client.makedirs(path)

    def save_video_chunk(self, video_chunk: VideoChunk, local_filepath):
        path = self.HDFS_VIDEOS_DIR + video_chunk.video_id + "/" + video_chunk.filename
        self._client.upload(path, local_filepath, replication=1, overwrite=True)

    def delete_video_chunk(self, video_chunk: VideoChunk):
        path = self.HDFS_VIDEOS_DIR + video_chunk.video_id + "/" + video_chunk.filename
        self._client.delete(path)

    def write_file(self, video_chunk: VideoChunk, data):
        path = self.HDFS_VIDEOS_DIR + video_chunk.video_id + "/" + video_chunk.filename
        self._client.write(path, data=data, replication=1, overwrite=True)

    def _read_file(self, path):
        if self._client.status(path, strict=False):
            with self._client.read(path) as reader:
                content = reader.read()
                return content
        else:
            return None

    def video_last_access_time(self, video_id):
        path = self.HDFS_VIDEOS_DIR + video_id + "/"
        result = self._client.status(path)
        return result['accessTime']

    def _touch_video_directory(self, video_id):
        path = self.HDFS_VIDEOS_DIR + video_id
        self._client.set_times(path, access_time=int(time.time()))
