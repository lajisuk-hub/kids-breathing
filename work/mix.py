# 선희 내레이션 + 직접 합성한 잔잔한 배경음(저작권 없음) → audio_<key>.wav
import sys, wave
import numpy as np
from script import CHARS, timeline, vpath

SR = 48000


def load(path):
    with wave.open(path) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


def note(f, dur, amp=1.0, decay=1.5):
    t = np.arange(int(dur * SR)) / SR
    env = np.minimum(1, t / 0.01) * np.exp(-t * decay)
    return amp * env * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t))


def pad(total):
    t = np.arange(int(total * SR)) / SR
    out = np.zeros_like(t)
    chords = [(261.6, 329.6, 392.0), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (196.0, 246.9, 293.7)]
    L = 5.0
    for i in range(int(total / L) + 1):
        a = int(i * L * SR); b = min(len(t), int((i * L + L + 1.5) * SR))
        if a >= len(t): break
        tt = t[a:b] - i * L
        env = np.minimum(1, tt / 1.2) * np.minimum(1, np.maximum(0, (L + 1.5 - tt) / 1.5))
        s = sum(np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 0.5 * tt) for f in chords[i % 4])
        out[a:b] += env * s
    return out / np.max(np.abs(out) + 1e-9)


def main(k):
    tl = timeline(k)
    total = tl["total"]
    mix = np.zeros(int((total + 1) * SR), np.float32)
    def put(sig, t, gain):
        a = int(t * SR); b = min(len(mix), a + len(sig)); mix[a:b] += gain * sig[: b - a]
    mix += 0.07 * pad(total + 1).astype(np.float32)
    # 단계가 바뀔 때 작은 종소리
    for (a, b, f, g) in tl["size"]:
        if any(abs(a - s) < 0.01 or abs(a - s - 6) < 0.01 for s in tl["cycleStarts"]):
            put(note(1046.5 if g > f else 784.0, 2.0, decay=2.5), a, 0.05)
    # 숫자 셀 때 아주 작은 톡 소리
    for (a, v) in tl["cnt"]:
        if v: put(note(1318.5, 0.3, decay=14), a, 0.035)
    # 제목·끝 반짝 소리
    for i, f in enumerate([784, 988, 1175, 1568]):
        put(note(f, 1.5, decay=3), 0.2 + i * 0.12, 0.06)
    for j in range(10):
        put(note([1568, 1760, 2093, 2349, 2637][j % 5], 1.2, decay=4), tl["fireworks"] + j * 0.35, 0.05)
    for e in tl["ev"]:
        put(load(vpath(k, e["key"])), e["t"], 1.25)
    # 끝 페이드
    n = int(1.2 * SR); mix[int(total * SR) - n:int(total * SR)] *= np.linspace(1, 0, n); mix[int(total * SR):] = 0
    mix = np.clip(mix, -0.98, 0.98)
    with wave.open(f"audio_{k}.wav", "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print("audio", k, round(total, 1))


if __name__ == "__main__":
    for k in sys.argv[1:]:
        main(k)
