# HLS Streamer
live conversion of an existing video or live stream

![diagram](/docs/diagram.png)


## Local video conversion
                    
```mermaid
sequenceDiagram
    participant UI
    participant Streamer
    participant Queue
    participant Converter
    participant HDFS



UI->>Streamer: video id 
Streamer->> UI: generated playlist 
Streamer->> Queue: convert chunk 0 message
Streamer->> Queue: convert chunk 1 message
Streamer->> Queue: ...
Streamer->> Queue: convert chunk 99 message
Queue->> Converter: convert chunk 0 message
HDFS->> Converter: load chunk 0
Converter->> HDFS: save converted chunk 0
UI->>Streamer: playlist request
HDFS->> Streamer: converted chunks list [0]
Streamer->> UI: updated playlist  [0]
Queue->> Converter: convert chunk 1 message
HDFS->> Converter: load chunk 1
Converter->> HDFS: save converted chunk 1
UI->> Streamer: converted chunk 0 request
HDFS->> Streamer: converted chunk 0
Streamer->> UI: converted chunk 0
UI->> Streamer: playlist request
HDFS->> Streamer: converted chunks list [0,1]
Streamer->> UI: updated playlist [0,1]
UI->> Streamer: converted chunk 1 request
HDFS->> Streamer: converted chunk 1
Streamer->> UI: chunk 1
```
