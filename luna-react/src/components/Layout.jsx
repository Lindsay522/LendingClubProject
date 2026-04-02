import { VALID_ROUTES } from "../lib/constants.js";

const NAV = [
  { id: "dashboard", label: "Home", icon: "◉" },
  { id: "closet", label: "Wardrobe", icon: "◇" },
  { id: "outfit", label: "Outfits", icon: "◆" },
  { id: "planner", label: "Plan", icon: "▣" },
  { id: "rooms", label: "Focus", icon: "◎" },
];

export function Layout({ route, navigate, children }) {
  const safeRoute = VALID_ROUTES.includes(route) ? route : "dashboard";

  return (
    <div className="app">
      <header className="site-header">
        <div className="site-header-inner">
          <button type="button" className="logo" onClick={() => navigate("dashboard")}>
            Luna
          </button>
          <button type="button" className="header-about" onClick={() => navigate("settings")}>
            About
          </button>
          <p className="tagline">Wardrobe · Rhythm · Wellness</p>
        </div>
      </header>

      <main className="main">{children}</main>

      <nav className="nav-bottom">
        {NAV.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`nav-item${safeRoute === item.id ? " active" : ""}`}
            onClick={() => navigate(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}
