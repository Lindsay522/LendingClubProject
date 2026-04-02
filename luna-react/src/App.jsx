import { useState } from "react";
import { LunaProvider } from "./context/LunaProvider.jsx";
import { useHashRoute } from "./hooks/useHashRoute.js";
import { Layout } from "./components/Layout.jsx";
import { Onboarding } from "./components/Onboarding.jsx";
import { RoomOverlay } from "./components/RoomOverlay.jsx";
import { Dashboard } from "./components/pages/Dashboard.jsx";
import { Closet } from "./components/pages/Closet.jsx";
import { Outfits } from "./components/pages/Outfits.jsx";
import { Planner } from "./components/pages/Planner.jsx";
import { Rooms } from "./components/pages/Rooms.jsx";
import { Settings } from "./components/pages/Settings.jsx";

function LunaApp() {
  const { route, navigate } = useHashRoute();
  const [roomId, setRoomId] = useState(null);

  let page = null;
  switch (route) {
    case "closet":
      page = <Closet />;
      break;
    case "outfit":
      page = <Outfits />;
      break;
    case "planner":
      page = <Planner />;
      break;
    case "rooms":
      page = <Rooms onOpenRoom={setRoomId} />;
      break;
    case "settings":
      page = <Settings />;
      break;
    default:
      page = <Dashboard navigate={navigate} />;
  }

  return (
    <>
      <Onboarding />
      <Layout route={route} navigate={navigate}>
        {page}
      </Layout>
      <RoomOverlay key={roomId || "closed"} roomId={roomId} onClose={() => setRoomId(null)} />
    </>
  );
}

export default function App() {
  return (
    <LunaProvider>
      <LunaApp />
    </LunaProvider>
  );
}
