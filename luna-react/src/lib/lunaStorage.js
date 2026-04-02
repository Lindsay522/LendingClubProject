import { KEYS } from "./constants.js";
import { todayStr } from "./dates.js";

export function readJson(key, defaultVal) {
  try {
    const raw = localStorage.getItem(key);
    if (raw == null) return defaultVal;
    return JSON.parse(raw);
  } catch {
    return defaultVal;
  }
}

export function writeJson(key, val) {
  try {
    localStorage.setItem(key, JSON.stringify(val));
  } catch {
    /* quota */
  }
}

export function allStorageKeyValues() {
  return Object.values(KEYS);
}

export function buildExportPayload() {
  const stores = {};
  allStorageKeyValues().forEach((key) => {
    const raw = localStorage.getItem(key);
    try {
      stores[key] = raw ? JSON.parse(raw) : null;
    } catch {
      stores[key] = raw;
    }
  });
  return {
    luna_export_version: 1,
    exportedAt: new Date().toISOString(),
    stores,
  };
}

export function downloadJson(filename, obj) {
  const blob = new Blob([JSON.stringify(obj, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

export function applyImportStores(stores) {
  allStorageKeyValues().forEach((key) => {
    if (!Object.prototype.hasOwnProperty.call(stores, key)) {
      localStorage.removeItem(key);
      return;
    }
    const v = stores[key];
    if (v === null || v === undefined) localStorage.removeItem(key);
    else localStorage.setItem(key, typeof v === "string" ? v : JSON.stringify(v));
  });
}

export function clearAllLunaKeys() {
  allStorageKeyValues().forEach((key) => localStorage.removeItem(key));
}

export function exportBackupFile() {
  downloadJson(`luna-backup-${todayStr()}.json`, buildExportPayload());
}
