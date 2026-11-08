import './globals.css';

export const metadata = {
  title: '숨쉬기 친구들 · 어린이 호흡 놀이',
  description: '별·달·비행기·풍선·꽃·구름 친구를 골라, 커지면 들이쉬고 작아지면 내쉬는 어린이 호흡 연습 영상',
};

export const viewport = { width: 'device-width', initialScale: 1 };

export default function RootLayout({ children }) {
  return (
    <html lang="ko">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link href="https://fonts.googleapis.com/css2?family=Jua&family=Gowun+Dodum&display=swap" rel="stylesheet" />
      </head>
      <body>{children}</body>
    </html>
  );
}
