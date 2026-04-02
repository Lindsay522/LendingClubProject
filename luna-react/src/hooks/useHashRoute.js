import { useCallback, useEffect, useState } from "react";
import { VALID_ROUTES } from "../lib/constants.js";

function normalizeHash() {
  let h = window.location.hash.replace(/^#/, "");
  if (!h || !VALID_ROUTES.includes(h)) return "dashboard";
  return h;
}

export function useHashRoute() {
  const [route, setRoute] = useState(normalizeHash);

  useEffect(() => {
    const onHash = () => setRoute(normalizeHash());
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  useEffect(() => {
    const h = window.location.hash.replace(/^#/, "");
    if (!h || !VALID_ROUTES.includes(h)) window.location.hash = "dashboard";
  }, []);

  const navigate = useCallback((id) => {
    const next = VALID_ROUTES.includes(id) ? id : "dashboard";
    if (window.location.hash !== `#${next}`) window.location.hash = next;
    else setRoute(next);
  }, []);

  return { route, navigate };
}
