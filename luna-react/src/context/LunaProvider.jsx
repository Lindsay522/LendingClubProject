import { useMemo, useState, useCallback } from "react";
import { KEYS } from "../lib/constants.js";
import { readJson, writeJson } from "../lib/lunaStorage.js";
import { LunaContext } from "./lunaContext.js";

export function LunaProvider({ children }) {
  const [version, setVersion] = useState(0);
  const bump = useCallback(() => setVersion((v) => v + 1), []);

  const value = useMemo(
    () => ({
      version,
      bump,
      getCloset: () => readJson(KEYS.closet, []),
      setCloset: (v) => {
        writeJson(KEYS.closet, v);
        bump();
      },
      getOutfits: () => readJson(KEYS.outfits, []),
      setOutfits: (v) => {
        writeJson(KEYS.outfits, v);
        bump();
      },
      getEvents: () => readJson(KEYS.events, []),
      setEvents: (v) => {
        writeJson(KEYS.events, v);
        bump();
      },
      getSleep: () => readJson(KEYS.sleep, []),
      setSleep: (v) => {
        writeJson(KEYS.sleep, v);
        bump();
      },
      getSport: () => readJson(KEYS.sport, []),
      setSport: (v) => {
        writeJson(KEYS.sport, v);
        bump();
      },
      getReflections: () => readJson(KEYS.reflections, {}),
      setReflections: (v) => {
        writeJson(KEYS.reflections, v);
        bump();
      },
      getFocus: () => readJson(KEYS.focus, {}),
      setFocus: (v) => {
        writeJson(KEYS.focus, v);
        bump();
      },
      getTomorrow: () => localStorage.getItem(KEYS.tomorrow) || "",
      setTomorrow: (s) => {
        localStorage.setItem(KEYS.tomorrow, s);
        bump();
      },
      getOnboardingDone: () => !!localStorage.getItem(KEYS.onboarding),
      setOnboardingDone: () => {
        localStorage.setItem(KEYS.onboarding, "1");
        bump();
      },
    }),
    [version, bump]
  );

  return <LunaContext.Provider value={value}>{children}</LunaContext.Provider>;
}
