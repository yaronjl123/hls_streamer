###Local video conversion sequence diagram
                    
```seq
UI->Streamer: video id 
Streamer-> UI: generated playlist 
Streamer-> QUEUE: convert chunk [0-99]
QUEUE-> Converter: convert chunk 0
HDFS-> Converter: load chunk 0
Converter-> HDFS: save converted chunk 0
UI->Streamer: playlist request
Streamer-> UI: updated playlist  [0]
UI->Streamer: converted chunk 0 request
HDFS-> Streamer: chunk 0
Streamer-> UI: chunk 0
QUEUE-> Converter: convert chunk 1
HDFS-> Converter: load chunk 1
Converter-> HDFS: save converted chunk 1
UI->Streamer: playlist request
Streamer-> UI: updated playlist [0,1]
UI->Streamer: chunk 1 request
HDFS-> Streamer: chunk 1
Streamer-> UI: chunk 1
#Note right of China: China thinks\nabout it 
```

###End
