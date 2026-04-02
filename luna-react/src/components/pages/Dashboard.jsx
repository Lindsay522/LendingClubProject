import { useMemo } from "react";
import { useLuna } from "../../hooks/useLuna.js";
import { todayStr, getMonday } from "../../lib/dates.js";

const ENERGY = [
  { key: "low", label: "Tired" },
  { key: "ok", label: "Okay" },
  { key: "good", label: "Good" },
  { key: "great", label: "Great" },
];

function pickInsight(mood) {
  const lines = [
    "A small step today is still progress. Be kind to yourself.",
    "You don’t have to do it all. Just the next right thing.",
    "Rest is part of the plan.",
    "Your best today might look different from yesterday. That’s okay.",
  ];
  if (mood === "low" || mood === "ok") lines.push("It’s okay to take things slow. You’re still moving.");
  if (mood === "good" || mood === "great") lines.push("You’re in a good place. Use it gently.");
  return lines[Math.floor(Math.random() * lines.length)];
}

export function Dashboard({ navigate }) {
  const luna = useLuna();
  const today = todayStr();

  const greeting = useMemo(() => {
    const h = new Date().getHours();
    if (h < 12) return "Good morning";
    if (h < 18) return "Good afternoon";
    return "Good evening";
  }, []);

  const dateLine = useMemo(
    () =>
      new Date().toLocaleDateString("en-US", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      }),
    []
  );

  const focus = luna.getFocus();
  const mood = typeof focus === "object" && focus[today] ? focus[today] : null;

  // eslint-disable-next-line react-hooks/exhaustive-deps -- luna.version bumps after import backup
  const insight = useMemo(() => pickInsight(mood), [mood, luna.version]);

  const sleepList = luna.getSleep().slice();
  sleepList.sort((a, b) => {
    const da = (a.date || "").localeCompare(b.date || "");
    if (da !== 0) return -da;
    return (b.id || "").localeCompare(a.id || "");
  });
  const lastSleep = sleepList[0];
  const sleepLabel = lastSleep ? `${lastSleep.hours || "—"} hrs` : "—";

  const sportList = luna.getSport();
  const mon = getMonday(new Date());
  const weekSport = sportList.filter((s) => getMonday(new Date(s.date)).getTime() === mon.getTime());
  const mins = weekSport.reduce((sum, s) => sum + (s.duration || 0), 0);
  const moveLabel =
    weekSport.length === 0 && mins === 0 ? "—" : `${weekSport.length} sessions · ${mins} min`;

  const setEnergy = (key) => {
    const o = luna.getFocus();
    const next = typeof o === "object" && o ? { ...o } : {};
    next[todayStr()] = key;
    luna.setFocus(next);
  };

  return (
    <section className="page page-dashboard active">
      <div className="dashboard-hero">
        <p className="dashboard-greeting">{greeting}</p>
        <p className="dashboard-date">{dateLine}</p>
        <p className="dashboard-subline">Here’s what matters today.</p>
      </div>
      <div className="dashboard-cards">
        <div className="card dashboard-card-mini card-sleep">
          <h3 className="card-label">Last night</h3>
          <p className="card-value">{sleepLabel}</p>
          <p className="card-hint">Sleep</p>
        </div>
        <div className="card dashboard-card-mini card-movement">
          <h3 className="card-label">This week</h3>
          <p className="card-value">{moveLabel}</p>
          <p className="card-hint">Movement</p>
        </div>
      </div>
      <div className="card card-focus">
        <h3 className="card-label">How are you feeling?</h3>
        <div className="focus-options">
          {ENERGY.map(({ key, label }) => (
            <button
              key={key}
              type="button"
              className={`focus-btn${mood === key ? " active" : ""}`}
              onClick={() => setEnergy(key)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>
      <div className="dashboard-insight">
        <span>{insight}</span>
      </div>
      <div className="card card-tomorrow">
        <h3 className="card-label">First thing tomorrow</h3>
        <p className="card-hint">One small win to make the morning easier.</p>
        <input
          key={`tomorrow-${luna.version}`}
          type="text"
          className="input input-inline"
          defaultValue={luna.getTomorrow()}
          onBlur={(e) => luna.setTomorrow(e.target.value.trim())}
          placeholder="e.g. Drink water, then open my notes"
        />
      </div>
      <div className="dashboard-actions">
        <button type="button" className="btn btn-soft" onClick={() => navigate("planner")}>
          Today’s plan
        </button>
        <button type="button" className="btn btn-soft" onClick={() => navigate("closet")}>
          Wardrobe
        </button>
        <button type="button" className="btn btn-soft" onClick={() => navigate("rooms")}>
          Focus space
        </button>
      </div>
      <p className="dashboard-copy">You’re doing enough.</p>
      <footer className="app-footer">
        <p className="app-footer-credit">
          Designed by <strong>Lindsay</strong>
        </p>
      </footer>
    </section>
  );
}
