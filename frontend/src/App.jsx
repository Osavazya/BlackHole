import React, { useState } from "react";
import "./App.css";
import PingButton from "./components/PingButton";

const BH = [
  {
    id: "sgrA",
    name: "Стрелец A* (Sagittarius A*)",
    img: new URL("./assets/sagittariusA.jpg", import.meta.url).href,
    distance_ly: 26000,
    mass_solar: 4.3e6,
    description:
      "Сверхмассивая чёрная дыра в центре Млечного Пути. Масса ~4,3 миллиона солнечных. Мы видим её влияние по орбитам звёзд S-кластера; в 2022 EHT получил её изображение-кольцо из горячего газа."
  },
  {
    id: "m87",
    name: "M87*",
    img: new URL("./assets/m87.jpg", import.meta.url).href,
    distance_ly: 53000000,
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
  const [current, setCurrent] = useState(BH[0].id);
  const selected = BH.find((b) => b.id === current);

  return (
    <div>
      <div className="header">
        <h1>Black Holes</h1>
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

        {/* Кнопка пинга API */}
        <div style={{ marginLeft: "1rem" }}>
          <PingButton />
        </div>
      </div>

      <section className="hero" role="region" aria-label={selected.name}>
        <img src={selected.img} alt={selected.name} />
        <div className="panel">
          <h2 className="title">{selected.name}</h2>
          <div className="meta">
            {selected.distance_ly && (
              <>
                Расстояние: {selected.distance_ly.toLocaleString("ru-RU")} св. лет ·{" "}
              </>
            )}
            {selected.mass_solar && <>Масса: {selected.mass_solar.toLocaleString("ru-RU")} M☉</>}
          </div>
          <p className="desc">{selected.description}</p>
        </div>
      </section>

      <footer
        style={{
          position: "fixed",
          bottom: 5,
          right: 10,
          color: "gray",
          fontSize: "12px"
        }}
      >
        Black Hole Gallery v0.1.1
      </footer>
    </div>
  );
}
