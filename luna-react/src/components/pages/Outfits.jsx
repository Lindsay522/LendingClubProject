import { useState } from "react";
import { useLuna } from "../../hooks/useLuna.js";
import { newId } from "../../lib/newId.js";
import { OUTFIT_PROMPTS } from "../../lib/constants.js";

const OCCASIONS = ["Class", "Date", "Cafe", "Interview", "Workout", "Travel", "Other"];
const WEATHER = ["Spring-Fall", "Summer", "Winter"];

export function Outfits() {
  const luna = useLuna();
  const closet = luna.getCloset();
  const outfits = luna.getOutfits();

  const [name, setName] = useState("");
  const [namePh, setNamePh] = useState("e.g. Monday meetings");
  const [occasion, setOccasion] = useState("Class");
  const [weather, setWeather] = useState("Spring-Fall");
  const [mood, setMood] = useState("");
  const [picked, setPicked] = useState({});
  const [onePieceId, setOnePieceId] = useState("");

  const idToName = {};
  closet.forEach((c) => {
    idToName[c.id] = c.name;
  });

  let suggestion = "";
  if (onePieceId) {
    const item = closet.find((c) => c.id === onePieceId);
    if (item) {
      const matches = closet.filter(
        (c) => c.id !== onePieceId && (c.season === item.season || c.category !== item.category)
      );
      suggestion = "Pair with pieces from other categories (e.g. top + bottom) and similar season. ";
      if (matches.length) suggestion += `Try: ${matches.slice(0, 5).map((m) => m.name).join(", ")}`;
    }
  }

  const togglePick = (id) => {
    setPicked((p) => ({ ...p, [id]: !p[id] }));
  };

  const onSaveOutfit = (e) => {
    e.preventDefault();
    const n = name.trim();
    if (!n) return;
    const itemIds = Object.keys(picked).filter((id) => picked[id]);
    luna.setOutfits([
      ...outfits,
      {
        id: newId(),
        name: n,
        occasion,
        weather,
        mood: mood.trim(),
        itemIds,
      },
    ]);
    setName("");
    setMood("");
    setPicked({});
  };

  const removeOutfit = (id) => {
    if (!confirm("Remove this outfit?")) return;
    luna.setOutfits(outfits.filter((o) => o.id !== id));
  };

  const applyPrompt = (key) => {
    const p = OUTFIT_PROMPTS[key];
    if (!p) return;
    setNamePh(p.name);
    setOccasion(p.occasion);
  };

  return (
    <section className="page page-outfit active">
      <div className="section-head">
        <h2 className="section-title">Outfits</h2>
        <p className="section-desc">Save looks, get pairing ideas, and plan what to wear.</p>
      </div>
      <div className="card">
        <h3 className="card-title">Quick prompts</h3>
        <div className="outfit-prompts">
          {Object.keys(OUTFIT_PROMPTS).map((key) => (
            <button key={key} type="button" className="chip" onClick={() => applyPrompt(key)}>
              {key === "today" && "What to wear today"}
              {key === "onepiece" && "Build around one piece"}
              {key === "campus" && "Campus look"}
              {key === "interview" && "Interview ready"}
              {key === "weekend" && "Weekend reset"}
            </button>
          ))}
        </div>
      </div>
      <div className="card">
        <h3 className="card-title">New outfit</h3>
        <form className="form" onSubmit={onSaveOutfit}>
          <div className="form-row">
            <label>Name</label>
            <input
              type="text"
              className="input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={namePh}
              required
            />
          </div>
          <div className="form-row form-row-half">
            <label>Occasion</label>
            <select className="input" value={occasion} onChange={(e) => setOccasion(e.target.value)}>
              {OCCASIONS.map((o) => (
                <option key={o} value={o}>
                  {o}
                </option>
              ))}
            </select>
          </div>
          <div className="form-row form-row-half">
            <label>Season</label>
            <select className="input" value={weather} onChange={(e) => setWeather(e.target.value)}>
              <option value="Spring-Fall">Spring / Fall</option>
              <option value="Summer">Summer</option>
              <option value="Winter">Winter</option>
            </select>
          </div>
          <div className="form-row">
            <label>Items</label>
            <div className="outfit-picker">
              {closet.length === 0 ? (
                <p className="hint">Add pieces in Wardrobe first.</p>
              ) : (
                closet.map((c) => (
                  <label key={c.id}>
                    <input
                      type="checkbox"
                      checked={!!picked[c.id]}
                      onChange={() => togglePick(c.id)}
                    />{" "}
                    {c.name} ({c.category})
                  </label>
                ))
              )}
            </div>
          </div>
          <div className="form-row">
            <label>Vibe or notes</label>
            <input
              type="text"
              className="input"
              value={mood}
              onChange={(e) => setMood(e.target.value)}
              placeholder="e.g. Confident, minimal, cozy"
            />
          </div>
          <button type="submit" className="btn btn-primary">
            Save outfit
          </button>
        </form>
      </div>
      <div className="card">
        <h3 className="card-title">Style one piece</h3>
        <p className="hint">Pick an item and we’ll suggest pairings from your wardrobe.</p>
        <select className="input" value={onePieceId} onChange={(e) => setOnePieceId(e.target.value)}>
          <option value="">Choose a piece…</option>
          {closet.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name} · {c.category}
            </option>
          ))}
        </select>
        <div className="one-piece-suggestions">{suggestion}</div>
      </div>
      {outfits.length === 0 ? (
        <div className="empty-state">
          <p className="empty-state-title">No outfits yet</p>
          <p className="empty-state-desc">Create one above. Your future self will thank you on busy mornings.</p>
        </div>
      ) : (
        <div className="outfit-list">
          {outfits.map((o) => {
            const names = (o.itemIds || []).map((id) => idToName[id] || id);
            return (
              <div key={o.id} className="outfit-card" data-outfit-id={o.id}>
                <div className="outfit-card-head">
                  <div className="outfit-card-name">{o.name}</div>
                  <button
                    type="button"
                    className="outfit-card-del"
                    aria-label="Remove outfit"
                    onClick={() => removeOutfit(o.id)}
                  >
                    Remove
                  </button>
                </div>
                <div className="outfit-card-meta">
                  {o.occasion} · {o.weather}
                  {o.mood ? ` · ${o.mood}` : ""}
                </div>
                <div className="outfit-card-items">{names.length ? names.join(", ") : "—"}</div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
