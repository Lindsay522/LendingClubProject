import { useContext } from "react";
import { LunaContext } from "../context/lunaContext.js";

export function useLuna() {
  const ctx = useContext(LunaContext);
  if (!ctx) throw new Error("useLuna must be used within LunaProvider");
  return ctx;
}
