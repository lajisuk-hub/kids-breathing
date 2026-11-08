#!/bin/bash
# 사용: bash make_video.sh <key>  → out/<key>.mp4
set -e
k=$1
FF=$(python -c "import imageio_ffmpeg as f;print(f.get_ffmpeg_exe())")
mkdir -p out
python mix.py $k
node render.mjs $k 30 out/${k}_silent.mp4
"$FF" -y -v error -i out/${k}_silent.mp4 -i audio_$k.wav -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart out/$k.mp4
rm out/${k}_silent.mp4
echo "VIDEO_DONE $k"
