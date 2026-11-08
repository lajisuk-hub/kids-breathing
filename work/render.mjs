// player.html 을 한 컷씩 찍어 mp4(소리 없음)로. 사용:
//   node render.mjs <key> <fps> <out.mp4>
//   node render.mjs <key> shot 3,12,40 <폴더>   ← 몇 컷만 jpg로
import { spawn, execFileSync } from 'node:child_process';
import { mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const [KEY, MODE, A3, A4] = process.argv.slice(2);
const W = 1280, H = 720;
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const FFMPEG = execFileSync('python', ['-c', 'import imageio_ffmpeg as f;print(f.get_ffmpeg_exe())']).toString().trim();
const PORT = 9400 + Math.floor(Math.random() * 400);
const FRAMES = join(process.env.TEMP || here, 'breath-frames-' + KEY);
const sleep = ms => new Promise(r => setTimeout(r, ms));

const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${PORT}`, '--no-first-run', '--no-default-browser-check',
  `--window-size=${W},${H}`, '--hide-scrollbars', '--force-device-scale-factor=1', '--allow-file-access-from-files',
  '--user-data-dir=' + join(process.env.TEMP || here, 'breath-chrome-' + PORT), 'about:blank'], { stdio: 'ignore' });

async function getWs() {
  for (let i = 0; i < 60; i++) {
    try { const l = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json(); const p = l.find(t => t.type === 'page'); if (p) return p.webSocketDebuggerUrl; } catch {}
    await sleep(200);
  }
  throw new Error('chrome not ready');
}
const ws = new WebSocket(await getWs());
await new Promise(r => ws.onopen = r);
let id = 0; const pend = new Map();
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
const cdp = (method, params = {}) => new Promise(res => { const i = ++id; pend.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async (expr, aw = false) => (await cdp('Runtime.evaluate', { expression: expr, awaitPromise: aw, returnByValue: true })).result?.result?.value;

await cdp('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: 1, mobile: false });
await cdp('Page.enable');
await cdp('Page.navigate', { url: pathToFileURL(join(here, 'player.html')).href + `?render=1&k=${KEY}` });
await sleep(1500);
for (let i = 0; i < 50 && !(await ev('typeof window.READY')).includes('function'); i++) await sleep(200);
await ev('window.READY()', true);
await sleep(300);
const TOTAL = await ev('window.TOTAL');
const snap = async (t, path) => {
  await ev(`seek(${t})`);
  const s = await cdp('Page.captureScreenshot', { format: 'jpeg', quality: 92, clip: { x: 0, y: 0, width: W, height: H, scale: 1 } });
  writeFileSync(path, Buffer.from(s.result.data, 'base64'));
};

if (MODE === 'shot') {
  mkdirSync(A4, { recursive: true });
  for (const t of A3.split(',')) await snap(+t, join(A4, `${KEY}_${t}.jpg`));
  console.log('shots done');
} else {
  const FPS = +MODE; rmSync(FRAMES, { recursive: true, force: true }); mkdirSync(FRAMES, { recursive: true });
  const N = Math.ceil(TOTAL * FPS); const t0 = Date.now();
  for (let i = 0; i < N; i++) {
    await snap(i / FPS, join(FRAMES, `f${String(i).padStart(5, '0')}.jpg`));
    if (i % 300 === 0) console.log(`${KEY} ${i}/${N} (${((Date.now() - t0) / 1000) | 0}s)`);
  }
  mkdirSync(dirname(A3), { recursive: true });
  execFileSync(FFMPEG, ['-y', '-hide_banner', '-loglevel', 'error', '-framerate', String(FPS), '-i', join(FRAMES, 'f%05d.jpg'),
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium', A3], { stdio: 'inherit' });
  rmSync(FRAMES, { recursive: true, force: true });
  console.log('DONE', A3);
}
ws.close(); chrome.kill(); process.exit(0);
