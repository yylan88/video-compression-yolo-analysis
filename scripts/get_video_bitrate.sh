#!/bin/bash

ROOT_DIR="/home/bobo/yyl/proj/original_video/drristd4/trim1/"

find "$ROOT_DIR" -type f -name "*.mp4" | while read -r video; do
    folder_name=$(basename "$(dirname "$video")")

    # 影片長度（秒）
    duration=$(ffprobe -v error -show_entries format=duration \
      -of default=noprint_wrappers=1:nokey=1 "$video")

    # 檔案大小（bytes）
    filesize=$(stat -c %s "$video")

    # bitrate = bits / seconds
    bitrate=$(awk -v s="$filesize" -v t="$duration" 'BEGIN{
        if (t>0) printf "%.2f", (s*8)/t;
        else printf "0"
    }')

    echo "$folder_name $bitrate"
done
