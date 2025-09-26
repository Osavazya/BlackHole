import React from "react";

const MEDIA = {
  sgra: { mp4:"/media/sgra/sgra-1080.mp4",  webm:"/media/sgra/sgra-720.webm",  poster:"/media/sgra/sgra-poster.jpg" },
  m87:  { mp4:"/media/m87/m87-1080.mp4",    webm:"/media/m87/m87-720.webm",    poster:"/media/m87/m87-poster.jpg" },
  cygx1:{ mp4:"/media/cygx1/cygx1-1080.mp4", webm:"/media/cygx1/cygx1-720.webm", poster:"/media/cygx1/cygx1-poster.jpg" },
};

// Тут задаём «яркость» и силу затемнения по каждому ролику:
const TUNE = {
  sgra:  { bright: 1.00, overlay: 0.30 }, // ярче — поднять bright, меньше «тени» — снизить overlay
  m87:   { bright: 1.00, overlay: 0.30 },
  cygx1: { bright: 1.00, overlay: 0.30 },
};

export default function VideoBackground({ which = "sgra" }) {
  const m = MEDIA[which] ?? MEDIA.sgra;
  const { bright, overlay } = TUNE[which] ?? TUNE.sgra;

  return (
    <div className="video-bg" aria-hidden="true">
      <video
        key={which}
        className="video-bg__video"
        autoPlay
        muted
        loop
        playsInline
        preload="auto"
        poster={m.poster}
        style={{ filter: `brightness(${bright}) contrast(1.03) saturate(1.05)` }}
      >
        <source src={m.webm} type="video/webm" />
        <source src={m.mp4}  type="video/mp4" />
      </video>

      {/* общий градиент оставляем, а силу затемнения регулируем opacity */}
      <div className="video-bg__overlay" style={{ opacity: overlay }} />
    </div>
  );
}
