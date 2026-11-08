# 1) Flow 영상(또는 그림)에서 초록 배경을 빼서 frames/<key>/fNNN.png 로
# 2) 대본 시간표를 data.js 로
# 사용: python build.py <key> [영상.mp4]
import sys, os, json, glob, subprocess, shutil
import numpy as np
from PIL import Image
import imageio_ffmpeg
from script import CHARS, timeline, IN, HOLD

FF = imageio_ffmpeg.get_ffmpeg_exe()
FPS = 24
SIZE = 560


def key_out(im):
    # 배경색(구석 4곳의 중간값)과 얼마나 다른지로 투명도를 정함 → 초록 잎사귀는 살아남음
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    h, w = a.shape[:2]
    corners = np.concatenate([a[:20, :20].reshape(-1, 3), a[:20, -20:].reshape(-1, 3), a[-20:, :20].reshape(-1, 3), a[-20:, -20:].reshape(-1, 3)])
    bg = np.median(corners, axis=0)
    d = np.sqrt(((a - bg) ** 2).sum(-1))
    alpha = np.clip((d - 70) / 40, 0, 1)
    alpha[:, : int(w * 0.18)] = 0; alpha[:, int(w * 0.82):] = 0   # 가장자리(Flow 반짝 표시) 지우기
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    # 반투명 가장자리만 초록 번짐 빼기
    edge = alpha < 0.98
    g2 = np.where(edge, np.minimum(g, np.maximum(r, b) + 10), g)
    out = np.dstack([r, g2, b, alpha * 255]).clip(0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def crop_box(frames):
    # 모든 프레임에 걸친 캐릭터 영역(정사각)
    xs, ys = [], []
    for f in frames[:: max(1, len(frames) // 12)]:
        al = np.asarray(f)[..., 3]
        yy, xx = np.where(al > 40)
        if len(xx):
            xs += [xx.min(), xx.max()]; ys += [yy.min(), yy.max()]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    s = max(x1 - x0, y1 - y0) * 1.08
    return int(cx - s / 2), int(cy - s / 2), int(cx + s / 2), int(cy + s / 2)


def make_frames(k, src):
    out = f"frames/{k}"
    shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    if src.lower().endswith(".png"):
        raw = [Image.open(src)]
    else:
        tmp = f"tmp_{k}"; shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
        subprocess.run([FF, "-v", "error", "-i", src, "-vf", f"fps={FPS}", f"{tmp}/r%03d.png"], check=True)
        raw = [Image.open(p) for p in sorted(glob.glob(f"{tmp}/r*.png"))]
    keyed = [key_out(im) for im in raw]
    box = crop_box(keyed)
    for i, im in enumerate(keyed):
        canvas = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]))
        canvas.paste(im.crop(box), (0, 0))
        canvas.resize((SIZE, SIZE), Image.LANCZOS).save(f"{out}/f{i:03d}.png", optimize=True)
    return len(keyed)


def make_data(k, n):
    c = CHARS[k]; tl = timeline(k)
    d = dict(key=k, title=c["title"], theme=c["theme"], frames=n, fps=FPS, IN=IN, HOLD=HOLD, **tl)
    open(f"data_{k}.js", "w", encoding="utf-8").write("window.DATA=" + json.dumps(d, ensure_ascii=False) + ";")


if __name__ == "__main__":
    k = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == "data":
        make_data(k, len(glob.glob(f"frames/{k}/f*.png"))); print("data", k); sys.exit()
    src = sys.argv[2] if len(sys.argv) > 2 else f"chars/{k}.png"
    n = make_frames(k, src)
    make_data(k, n)
    print(k, n, "frames")
