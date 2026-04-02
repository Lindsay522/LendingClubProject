const ROOMS = [
  { id: "morning", icon: "☀️", name: "Morning start", desc: "Ease into the day" },
  { id: "study", icon: "📚", name: "Deep study", desc: "Focus mode" },
  { id: "creative", icon: "✨", name: "Creative focus", desc: "Ideas and flow" },
  { id: "yoga", icon: "🧘", name: "Stretch break", desc: "Breathe & move" },
  { id: "reset", icon: "🌙", name: "Soft reset", desc: "Clear your head" },
  { id: "sleep", icon: "🛏", name: "Wind down", desc: "Prepare for rest" },
];

export function Rooms({ onOpenRoom }) {
  return (
    <section className="page page-rooms active">
      <div className="section-head">
        <h2 className="section-title">Focus spaces</h2>
        <p className="section-desc">
          Step into a mode. Each space has its own vibe and a short timer to stay present.
        </p>
      </div>
      <div className="room-cards">
        {ROOMS.map((r) => (
          <button key={r.id} type="button" className="room-card" onClick={() => onOpenRoom(r.id)}>
            <span className="room-card-icon">{r.icon}</span>
            <span className="room-card-name">{r.name}</span>
            <span className="room-card-desc">{r.desc}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
