import React, { useEffect, useState } from "react";
import { apiGet, apiPost } from "./api";

export default function App() {
  const [health, setHealth] = useState("unknown");
  const [version, setVersion] = useState("?");
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({ name: "", distance_ly: "", mass_solar: "", description: "" });
  const [error, setError] = useState("");

  async function load() {
    try {
      setError("");
      const [h, v, list] = await Promise.all([
        apiGet("/health"),
        apiGet("/version"),
        apiGet("/api/v1/blackholes"),
      ]);
      setHealth(h.status);
      setVersion(v.version);
      setItems(list);
    } catch (e) {
      setError(String(e));
    }
  }

  useEffect(() => { load(); }, []);

  async function submit(e) {
    e.preventDefault();
    try {
      await apiPost("/api/v1/blackholes", {
        name: form.name,
        distance_ly: form.distance_ly ? Number(form.distance_ly) : null,
        mass_solar: form.mass_solar ? Number(form.mass_solar) : null,
        description: form.description || null,
      });
      setForm({ name: "", distance_ly: "", mass_solar: "", description: "" });
      load();
    } catch (e) {
      setError(String(e));
    }
  }

  return (
    <div style={{ fontFamily: "system-ui, sans-serif", margin: "2rem auto", maxWidth: 900 }}>
      <h1>BlackHole — демо сайт</h1>
      <p>API health: <b>{health}</b> | version: <b>{version}</b></p>
      {error && <p style={{color:"crimson"}}>Ошибка: {error}</p>}

      <h2>Добавить чёрную дыру</h2>
      <form onSubmit={submit} style={{ display: "grid", gap: ".6rem", maxWidth: 500 }}>
        <input required placeholder="Название" value={form.name} onChange={e=>setForm({...form, name:e.target.value})} />
        <input placeholder="Расстояние (св. лет)" value={form.distance_ly} onChange={e=>setForm({...form, distance_ly:e.target.value})} />
        <input placeholder="Масса (в массах Солнца)" value={form.mass_solar} onChange={e=>setForm({...form, mass_solar:e.target.value})} />
        <textarea placeholder="Описание" value={form.description} onChange={e=>setForm({...form, description:e.target.value})} />
        <button>Добавить</button>
      </form>

      <h2 style={{marginTop:"1.5rem"}}>Каталог чёрных дыр</h2>
      <ul>
        {items.map(bh => (
          <li key={bh.id} style={{ marginBottom: ".8rem" }}>
            <b>{bh.name}</b><br/>
            <small>
              {bh.distance_ly != null && <>Расстояние: {bh.distance_ly.toLocaleString("ru-RU")} св. лет | </>}
              {bh.mass_solar != null && <>Масса: {bh.mass_solar.toLocaleString("ru-RU")} M☉</>}
            </small>
            <div>{bh.description || "—"}</div>
          </li>
        ))}
      </ul>

      <p><a href="/" onClick={(e)=>{e.preventDefault(); load();}}>Обновить данные</a> · <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">Swagger</a></p>
    </div>
  );
}
