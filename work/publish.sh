#!/bin/bash
# out/<key>.mp4 → ../public/videos/<key>.mp4 (모든 기기 호환 형식) + 표지 jpg
FF=$(python -c "import imageio_ffmpeg as f;print(f.get_ffmpeg_exe())")
for k in "$@"; do
  "$FF" -y -v error -i out/$k.mp4 -vf "scale=out_range=tv,format=yuv420p" -c:v libx264 -crf 23 -preset medium -profile:v high -c:a copy -movflags +faststart ../public/videos/$k.mp4
  "$FF" -y -v error -ss 13 -i out/$k.mp4 -frames:v 1 -q:v 4 ../public/videos/$k.jpg
  echo "published $k $(du -h ../public/videos/$k.mp4 | cut -f1)"
done
