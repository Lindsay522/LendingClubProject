import { applyImportStores, clearAllLunaKeys, exportBackupFile } from "../../lib/lunaStorage.js";

export function Settings() {

  const onImport = (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const data = JSON.parse(reader.result);
        const stores = data?.stores;
        if (!stores || typeof stores !== "object") {
          alert("This file doesn’t look like a Luna backup.");
          return;
        }
        if (!confirm("Replace all Luna data in this browser with the backup? This cannot be undone.")) return;
        applyImportStores(stores);
        window.location.reload();
      } catch {
        alert("Could not read that file. Check that it’s valid JSON.");
      }
      e.target.value = "";
    };
    reader.readAsText(f);
  };

  const onClear = () => {
    if (!confirm("Delete all Luna data on this device? Wardrobe, outfits, plans, and logs will be gone."))
      return;
    clearAllLunaKeys();
    window.location.reload();
  };

  return (
    <section className="page page-settings active">
      <div className="section-head">
        <h2 className="section-title">About Luna</h2>
        <p className="section-desc">A lifestyle app for wardrobe, planning, wellness, and focus.</p>
      </div>
      <div className="card">
        <div className="settings-row">
          <span>Version</span>
          <span>2.0 (React)</span>
        </div>
        <div className="settings-row">
          <span>Data</span>
          <span>Stored locally in your browser</span>
        </div>
        <div className="settings-row">
          <span>Stack</span>
          <span>Vite + React</span>
        </div>
      </div>
      <div className="card">
        <h3 className="card-title">Your data</h3>
        <p className="card-hint">
          Export a backup, restore on another device, or reset the app. Import replaces all Luna data in this browser.
        </p>
        <div className="settings-actions">
          <button type="button" className="btn btn-soft" onClick={exportBackupFile}>
            Export backup
          </button>
          <label className="btn btn-soft settings-file-label">
            Import backup
            <input type="file" accept="application/json" className="visually-hidden" onChange={onImport} />
          </label>
          <button type="button" className="btn btn-ghost" onClick={onClear}>
            Clear all data…
          </button>
        </div>
      </div>
      <div className="settings-credit-block">
        <p className="settings-credit-text">Designed with care</p>
        <p className="settings-credit-name">Designed by Lindsay</p>
      </div>
    </section>
  );
}
