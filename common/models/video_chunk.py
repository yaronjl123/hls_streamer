import re
from pydantic import BaseModel


class VideoChunk(BaseModel):
    video_id: str
    sequence_number: int

    @property
    def filename(self):
        return "{}{}.ts".format(self.video_id, self.sequence_number)

    def __lt__(self, other):
        return self.sequence_number < other.sequence_number

    @classmethod
    def create_from_filename(cls, video_id, filename):
        pattern = r'{video_id}(\d+).ts'.format(video_id=video_id)
        sequence_number = re.search(pattern, filename).group(1)
        return cls(video_id=video_id,
                   sequence_number=int(sequence_number))

