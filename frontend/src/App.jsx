import React, { useState } from "react";
import "./styles.css";                       // <-- важно: подключаем ЭТОТ css
import PingButton from "./components/PingButton";
import VideoBackground from "./components/VideoBackground.jsx";

// id: sgra / m87 / cygx1
const BH = [
  {
    id: "sgra",
    name: "Стрелец A* (Sagittarius A*)",
    img: new URL("./assets/sagittariusA.jpg", import.meta.url).href, // больше не используется
    distance_ly: 26000,
    mass_solar: 4.3e6,
    description:
      "Сверхмассивая чёрная дыра в центре Млечного Пути. Масса ~4,3 миллиона солнечных. Мы видим её влияние по орбитам звёзд S-кластера; в 2022 EHT получил её изображение-кольцо из горячего газа."
  },
  {
    id: "m87",
    name: "M87*",
    img: new URL("./assets/m87.jpg", import.meta.url).href,
    distance_ly: 53_000_000,
    mass_solar: 6.5e9,
    description:
      "Сверхмассивая чёрная дыра в эллиптической галактике M87. Первая сфотографированная непосредственно (коллаборация Event Horizon Telescope, 2019). Известна гигантской релятивистской струёй (джетом)."
  },
  {
    id: "cygx1",
    name: "Лебедь X-1 (Cygnus X-1)",
    img: new URL("./assets/cygnusx1.jpg", import.meta.url).href,
    distance_ly: 7200,
    mass_solar: 21,
    description:
      "Одна из первых кандидатов в чёрные дыры звёздной массы. Находится в двойной системе; обнаружена по рентгеновскому излучению вещества, падающего с компаньона на аккреционный диск."
  }
];

export default function App() {
  const [current, setCurrent] = useState("sgra");
  const selected = BH.find((b) => b.id === current) ?? BH[0];

  return (
    <div className="page">
      {/* Фоновое видео */}
      <VideoBackground which={current} />

      {/* Верхняя панель */}
      <div className="header">
        <h1 style={{margin:0, fontSize:18, fontWeight:600}}>Black Holes</h1>
        <div className="spacer" />
        {BH.map((b) => (
          <button
            key={b.id}
            className={"btn " + (b.id === current ? "active" : "")}
            onClick={() => setCurrent(b.id)}
            aria-pressed={b.id === current}
          >
            {b.name.split(" (")[0]}
          </button>
        ))}
        <div style={{ marginLeft: 12 }}>
          <PingButton />
        </div>
      </div>

      {/* Текстовая карточка внизу */}
      <section className="hero" role="region" aria-label={selected.name}>
        <div className="panel">
          <h2 className="title">{selected.name}</h2>
          <div className="meta">
            {selected.distance_ly && (
              <>Расстояние: {selected.distance_ly.toLocaleString("ru-RU")} св. лет · </>
            )}
            {selected.mass_solar && <>Масса: {selected.mass_solar.toLocaleString("ru-RU")} M☉</>}
          </div>
          <p className="desc">{selected.description}</p>
        </div>
      </section>

      <footer
        style={{ position: "fixed", bottom: 5, right: 10, color: "gray", fontSize: 12 }}
      >
        Black Hole Gallery v0.1.1
      </footer>
    </div>
  );
}
