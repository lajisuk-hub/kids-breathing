# 선희 목소리(ko-KR-SunHiNeural, -8%)로 대본을 녹음 → voice/<캐릭터|common>/<key>.wav (앞뒤 빈 소리는 잘라냄)
import asyncio, subprocess, os, sys
import edge_tts, imageio_ffmpeg
from script import CHARS, lines, vpath

FF = imageio_ffmpeg.get_ffmpeg_exe()
TRIM = "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur=0.15"


async def rec(text, path, rate):
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mp3 = path[:-4] + ".mp3"
    await edge_tts.Communicate(text, "ko-KR-SunHiNeural", rate=rate).save(mp3)
    subprocess.run([FF, "-y", "-v", "error", "-i", mp3, "-af", TRIM, "-ac", "1", "-ar", "48000", path], check=True)
    os.remove(mp3)


async def main():
    for k in sys.argv[1:] or list(CHARS):
        for key, text in lines(CHARS[k]).items():
            rate = "-15%" if key.startswith("c_") else "-8%"
            await rec(text, vpath(k, key), rate)
        print(k, "ok")

asyncio.run(main())
