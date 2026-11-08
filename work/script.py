# 호흡 영상 대본·시간표 (참고 영상 「별반짝 호흡」과 같은 순서)
# 캐릭터마다 이름만 바꿔 같은 패턴으로 만든다. 시간은 실제 목소리 길이에 맞춰 자동으로 잡는다.
import os, wave

CHARS = {
    "star":    dict(title="별반짝 호흡", obj="별을",     sub="별이",     theme="night"),
    "moon":    dict(title="달님 호흡",   obj="달님을",   sub="달님이",   theme="night"),
    "plane":   dict(title="비행기 호흡", obj="비행기를", sub="비행기가", theme="sky"),
    "balloon": dict(title="풍선 호흡",   obj="풍선을",   sub="풍선이",   theme="sky"),
    "flower":  dict(title="꽃향기 호흡", obj="꽃을",     sub="꽃이",     theme="garden"),
    "cloud":   dict(title="구름 호흡",   obj="구름을",   sub="구름이",   theme="sky"),
}
COMMON = {"c_in", "c_hold", "c_out", "ready", "again", "last", "great"}
IN, HOLD, OUT = 4, 2, 4          # 들이쉬기 4초 · 멈추기 2초 · 내쉬기 4초
CYCLE = IN + HOLD + OUT


def lines(c):
    return {
        "title": c["title"] + ".",
        "intro": f"지금부터 이 {c['obj']} 따라, 숨을 들이쉬고 내쉬는 연습을 할 거예요.",
        "big":   f"{c['sub']} 커지면, 코로 숨을 들이쉬고,",
        "stop":  f"{c['sub']} 멈추면, 숨을 잠시 참아 보세요.",
        "small": f"{c['sub']} 작아지면, 후우~ 하고 입으로 숨을 내쉬는 거예요.",
        "ready": "따라 할 수 있나요?",
        "watch": f"지금부터 시작할 테니, 눈을 크게 뜨고 {c['obj']} 지켜보세요.",
        "c_in":  "코로 천천히 들이쉬어요.",
        "c_hold": "잠깐 멈추고,",
        "c_out": "후우~ 입으로 천천히 내쉬어요.",
        "again": "어때요? 처음엔 조금 어려울 수 있어요. 한 번 더 해 볼까요?",
        "last":  "마지막이에요.",
        "great": "정말 잘했어요! 훌륭해요!",
    }


def vpath(k, key):
    return f"voice/{'common' if key in COMMON else k}/{key}.wav"


def dur(k, key):
    p = vpath(k, key)
    if not os.path.exists(p):
        return 2.0
    with wave.open(p) as w:
        return w.getnframes() / w.getframerate()


def timeline(k):
    c = CHARS[k]; L = lines(c)
    ev, size, cnt, tag = [], [], [], []
    d = lambda key: dur(k, key)
    def say(t, key, cap="="):
        ev.append(dict(t=round(t, 3), key=key, text=L[key], cap=L[key] if cap == "=" else cap))
        return t + d(key)

    say(0.8, "title", cap="")
    t = say(5.0, "intro") + 0.6
    # 커지기 시범
    size.append((t + 0.4, t + 4.4, 0, 1))
    t = max(say(t, "big"), t + 4.6) + 0.3
    t = max(say(t, "stop"), t + 2.0) + 0.4
    size.append((t + 0.6, t + 4.6, 1, 0))
    t = max(say(t, "small"), t + 4.8) + 0.6
    t = say(t, "ready") + 0.8
    t = say(t, "watch") + 1.0

    def cycle(t0, last=False):
        size.append((t0, t0 + IN, 0, 1))
        size.append((t0 + IN + HOLD, t0 + CYCLE, 1, 0))
        say(t0 + 0.1, "c_in", cap="코로 천천히 숨을 들이쉬어요")
        say(t0 + IN + 0.1, "c_hold", cap=f"{HOLD}초간 잠시 숨을 멈췄다가")
        say(t0 + IN + HOLD + 0.1, "c_out", cap="후우~ 입으로 천천히 숨을 내쉬어요")
        for i in range(IN): cnt.append((t0 + i, i + 1))
        for i in range(HOLD): cnt.append((t0 + IN + i, i + 1))
        for i in range(OUT): cnt.append((t0 + IN + HOLD + i, i + 1))
        cnt.append((t0 + CYCLE, 0))
        if last: tag.append((t0 - 2.2, t0 + CYCLE, "마지막"))
        return t0 + CYCLE

    starts = []
    for _ in range(3):
        starts.append(t); t = cycle(t) + 1.0
    t = say(t, "again") + 0.8
    starts.append(t); t = cycle(t) + 0.6
    t = say(t, "last") + 0.3
    starts.append(t); t = cycle(t, last=True) + 1.0
    fw = t
    t = say(t, "great")
    return dict(ev=ev, size=size, cnt=cnt, tag=tag, fireworks=fw, total=max(t, fw + 5) + 1.5, cycleStarts=starts)
