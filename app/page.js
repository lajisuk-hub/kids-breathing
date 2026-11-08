'use client';
import { useEffect, useRef, useState } from 'react';
import { FRIENDS } from './friends';

export default function Home() {
  const [sel, setSel] = useState(null);
  const videoRef = useRef(null);

  // 주소에 ?c=star 처럼 있으면 그 친구 영상으로 바로
  useEffect(() => {
    const c = new URLSearchParams(location.search).get('c');
    if (c && FRIENDS.some(f => f.key === c)) setSel(c);
    const onPop = () => {
      const k = new URLSearchParams(location.search).get('c');
      setSel(FRIENDS.some(f => f.key === k) ? k : null);
    };
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  const open = (k) => {
    setSel(k);
    history.pushState(null, '', `?c=${k}`);
    window.scrollTo(0, 0);
  };
  const close = () => {
    setSel(null);
    history.pushState(null, '', location.pathname);
  };
  const full = () => {
    const v = videoRef.current; if (!v) return;
    (v.requestFullscreen || v.webkitEnterFullscreen || v.webkitRequestFullscreen)?.call(v);
  };

  const f = FRIENDS.find(x => x.key === sel);

  if (f) {
    return (
      <main className="watch" style={{ '--accent': f.color }}>
        <div className="watchTop">
          <button className="back" onClick={close}>← 다른 친구 고르기</button>
          <h1 className="watchTitle"><img src={`/chars/${f.key}.png`} alt="" />{f.title}</h1>
        </div>
        <div className="player">
          <video ref={videoRef} key={f.key} src={`/videos/${f.key}.mp4`} poster={`/videos/${f.key}.jpg`}
            controls autoPlay playsInline preload="auto" />
        </div>
        <div className="watchBtns">
          <button className="big" onClick={full}>⛶ 크게 보기</button>
        </div>
        <p className="how">
          <b>{f.name}</b>{/[가-힣]$/.test(f.name) && hasBatchim(f.name) ? '이' : '가'} 커지면 <b>코로 들이쉬고</b> ·
          멈추면 <b>잠깐 참고</b> · 작아지면 <b>후우~ 입으로 내쉬어요</b>
        </p>
        <div className="others">
          {FRIENDS.filter(x => x.key !== f.key).map(x => (
            <button key={x.key} className="mini" onClick={() => open(x.key)}>
              <img src={`/chars/${x.key}.png`} alt="" /><span>{x.name}</span>
            </button>
          ))}
        </div>
      </main>
    );
  }

  return (
    <main className="home">
      <Stars />
      <header className="hero">
        <p className="kicker">마음이 차분해지는 어린이 호흡 놀이</p>
        <h1>숨쉬기 친구들</h1>
        <p className="lead">함께 숨 쉴 친구를 골라 보세요!<br />친구가 <b>커지면 들이쉬고</b>, <b>작아지면 내쉬어요</b>.</p>
      </header>
      <section className="grid">
        {FRIENDS.map((x, i) => (
          <button key={x.key} className="card" onClick={() => open(x.key)}
            style={{ '--bg': x.bg, '--accent': x.color, animationDelay: `${i * -0.7}s` }}>
            <img src={`/chars/${x.key}.png`} alt={x.name} style={{ animationDelay: `${i * -0.9}s` }} />
            <span className="name">{x.name}</span>
            <span className="sub">{x.title} ▶</span>
          </button>
        ))}
      </section>
      <footer className="foot">영상마다 약 1분 40초 · 소리를 켜고 함께 따라 해요</footer>
    </main>
  );
}

function hasBatchim(word) {
  const c = word.charCodeAt(word.length - 1) - 0xac00;
  return c >= 0 && c % 28 !== 0;
}

function Stars() {
  const s = Array.from({ length: 40 }, (_, i) => {
    const r = (n) => { const x = Math.sin(i * 127.1 + n * 311.7) * 43758.5453; return x - Math.floor(x); };
    return { left: r(1) * 100 + '%', top: r(2) * 100 + '%', d: 1.5 + r(3) * 3 + 's', s: 2 + r(4) * 3 + 'px' };
  });
  return <div className="stars" aria-hidden>{s.map((p, i) => (
    <i key={i} style={{ left: p.left, top: p.top, width: p.s, height: p.s, animationDuration: p.d }} />
  ))}</div>;
}
