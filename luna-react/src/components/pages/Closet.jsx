import { useState } from "react";
import { useLuna } from "../../hooks/useLuna.js";
import { newId } from "../../lib/newId.js";
import { CATEGORY_ICONS } from "../../lib/constants.js";

const CATEGORIES = ["Tops", "Bottoms", "Outerwear", "Shoes & Bags", "Accessories"];
const SEASONS = ["Spring", "Summer", "Fall", "Winter", "All-year"];

export function Closet() {
  const luna = useLuna();
  const [filterCategory, setFilterCategory] = useState("");
  const [filterSeason, setFilterSeason] = useState("");

  const list = luna.getCloset();
  const filtered = list.filter((c) => {
    if (filterCategory && c.category !== filterCategory) return false;
    if (filterSeason && c.season !== filterSeason) return false;
    return true;
  });

  const removeItem = (id) => {
    luna.setCloset(list.filter((c) => c.id !== id));
  };

  const onSubmit = (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const name = (fd.get("name") || "").trim();
    if (!name) return;
    const priceRaw = fd.get("price");
    const item = {
      id: newId(),
      name,
      brand: (fd.get("brand") || "").trim(),
      category: fd.get("category") || "Tops",
      season: fd.get("season") || "All-year",
      styleTags: (fd.get("styleTags") || "").trim(),
      price: priceRaw ? parseInt(String(priceRaw), 10) : null,
      link: (fd.get("link") || "").trim() || null,
      dupeNote: (fd.get("dupeNote") || "").trim() || null,
    };
    luna.setCloset([...list, item]);
    e.target.reset();
  };

  return (
    <section className="page page-closet active">
      <div className="section-head">
        <h2 className="section-title">Wardrobe</h2>
        <p className="section-desc">Your pieces, organized. Build outfits and track what you love.</p>
      </div>
      <div className="card">
        <h3 className="card-title">Add a piece</h3>
        <form className="form form-closet" onSubmit={onSubmit}>
          <div className="form-row">
            <label>Name</label>
            <input type="text" className="input" name="name" placeholder="e.g. Cream knit cardigan" required />
          </div>
          <div className="form-row">
            <label>Brand</label>
            <input type="text" className="input" name="brand" placeholder="Optional" />
          </div>
          <div className="form-row form-row-half">
            <label>Category</label>
            <select className="input" name="category" defaultValue="Tops">
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
          <div className="form-row form-row-half">
            <label>Season</label>
            <select className="input" name="season" defaultValue="Spring">
              {SEASONS.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
          <div className="form-row">
            <label>Style tags</label>
            <input type="text" className="input" name="styleTags" placeholder="e.g. Minimal, casual, cozy" />
          </div>
          <div className="form-row form-row-half">
            <label>Price</label>
            <input type="number" className="input" name="price" placeholder="Optional" min="0" step="1" />
          </div>
          <div className="form-row form-row-half">
            <label>Link</label>
            <input type="url" className="input" name="link" placeholder="Optional" />
          </div>
          <div className="form-row">
            <label>Notes</label>
            <input type="text" className="input" name="dupeNote" placeholder="Dupes, care, or reminders" />
          </div>
          <button type="submit" className="btn btn-primary">
            Add to wardrobe
          </button>
        </form>
      </div>
      <div className="card">
        <h3 className="card-title">Filter</h3>
        <div className="filter-row">
          <select
            className="input input-sm"
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
          >
            <option value="">All categories</option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <select className="input input-sm" value={filterSeason} onChange={(e) => setFilterSeason(e.target.value)}>
            <option value="">All seasons</option>
            {SEASONS.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
      </div>
      {filtered.length === 0 ? (
        <div className="empty-state">
          <p className="empty-state-title">Your wardrobe is empty</p>
          <p className="empty-state-desc">Add your first piece above. Every outfit starts with one item.</p>
        </div>
      ) : (
        <div className="closet-grid">
          {filtered.map((c) => {
            const tags = (c.styleTags || "")
              .split(/[,，]/)
              .map((t) => t.trim())
              .filter(Boolean);
            const price = c.price ? `$${c.price}` : "";
            const thumbIcon = CATEGORY_ICONS[c.category] || "✨";
            return (
              <div key={c.id} className="closet-item" data-id={c.id}>
                <div className="closet-item-thumb">{thumbIcon}</div>
                <div className="closet-item-name">{c.name}</div>
                <div className="closet-item-meta">
                  {c.brand || ""}
                  {price ? ` · ${price}` : ""} · {c.season || ""}
                </div>
                {tags.length > 0 && (
                  <div className="closet-item-tags">
                    {tags.map((t) => (
                      <span key={t} className="closet-item-tag">
                        {t}
                      </span>
                    ))}
                  </div>
                )}
                <button type="button" className="closet-item-del" onClick={() => removeItem(c.id)}>
                  Remove
                </button>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
