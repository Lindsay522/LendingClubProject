import { useCallback, useEffect, useState } from "react";
import { ROOM_NAMES, ROOM_GUIDANCE, ROOM_FOCUS_SECONDS } from "../lib/constants.js";

function formatTimer(sec) {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function RoomOverlay({ roomId, onClose }) {
  const focusSecs = roomId ? ROOM_FOCUS_SECONDS[roomId] || 0 : 0;
  const [remaining, setRemaining] = useState(focusSecs);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    if (!running) return;
    const id = setInterval(() => {
      setRemaining((r) => {
        if (r <= 1) {
          clearInterval(id);
          setRunning(false);
          try {
            window.navigator?.vibrate?.(200);
          } catch {
            /* ignore */
          }
          return 0;
        }
        return r - 1;
      });
    }, 1000);
    return () => clearInterval(id);
  }, [running]);

  const close = useCallback(() => {
    setRunning(false);
    onClose();
  }, [onClose]);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "Escape" && roomId) close();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [roomId, close]);

  if (!roomId) return null;

  const name = ROOM_NAMES[roomId] || roomId;
  const guidance = ROOM_GUIDANCE[roomId] || "";
  const showTimer = focusSecs > 0;

  const startTimer = () => {
    setRemaining(focusSecs);
    setRunning(true);
  };

  const resetTimer = () => {
    setRunning(false);
    setRemaining(focusSecs);
  };

  return (
    <div
      className="room-overlay show"
      aria-hidden="false"
      role="dialog"
      aria-label={name}
      onClick={(e) => e.target === e.currentTarget && close()}
    >
      <div className="room-scene" data-room={roomId}>
        <div className={`room-inner room-${roomId}`} />
        <button type="button" className="room-close" aria-label="Close" onClick={close}>
          ×
        </button>
        <p className={`room-guidance${roomId === "sleep" ? " room-guidance-dark" : ""}`}>{guidance}</p>
        {showTimer && (
          <div className="room-timer-wrap" style={{ display: "flex" }}>
            <div className="room-timer">{formatTimer(remaining)}</div>
            {!running ? (
              <button type="button" className="btn btn-primary btn-sm room-timer-start" onClick={startTimer}>
                {roomId === "morning" ? "Start 10 minutes" : "Start 25 minutes"}
              </button>
            ) : (
              <button type="button" className="btn btn-soft btn-sm room-timer-reset" onClick={resetTimer}>
                Reset
              </button>
            )}
          </div>
        )}
        <div className="room-name">{name}</div>
      </div>
    </div>
  );
}
