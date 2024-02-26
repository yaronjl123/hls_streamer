import argparse
import asyncio
from common.helpers import process_livestream
from common.dependencies import DependenciesContainer


container = DependenciesContainer()
container.wire(modules=["common.helpers", "common.messaging.clients.rabbit.client"])
container.config.from_yaml("./config.yml")


if __name__ == "__main__":
    parser = argparse.ArgumentParser("simple_example")
    parser.add_argument("--playlist_url", type=str)
    parser.add_argument("--source_video_id", type=str)
    parser.add_argument("--new_video_id", type=str)
    args = parser.parse_args()

    asyncio.run(process_livestream(args.playlist_url, args.source_video_id, args.new_video_id))
