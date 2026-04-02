import { useMemo, useState } from "react";
import { useLuna } from "../../hooks/useLuna.js";
import { newId } from "../../lib/newId.js";
import { MONTH_NAMES, WEEKDAYS } from "../../lib/constants.js";
import { todayStr } from "../../lib/dates.js";

function buildCalendarCells(calYear, calMonth) {
  const first = new Date(calYear, calMonth, 1);
  const last = new Date(calYear, calMonth + 1, 0);
  const startDay = first.getDay();
  const days = last.getDate();
  const prevMonth = new Date(calYear, calMonth, 0);
  const prevDays = prevMonth.getDate();
  const cells = [];

  for (let i = 0; i < startDay; i++) {
    const d = prevDays - startDay + i + 1;
    const dateStr = `${prevMonth.getFullYear()}-${String(prevMonth.getMonth() + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
    cells.push({ d, dateStr, other: true });
  }
  for (let d = 1; d <= days; d++) {
    const dateStr = `${calYear}-${String(calMonth + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
    cells.push({ d, dateStr, other: false });
  }
  const nextY = calMonth === 11 ? calYear + 1 : calYear;
  const nextM = calMonth === 11 ? 0 : calMonth + 1;
  const total = startDay + days;
  const nextCount = total % 7 === 0 ? 0 : 7 - (total % 7);
  for (let i = 0; i < nextCount; i++) {
    const d = i + 1;
    const dateStr = `${nextY}-${String(nextM + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
    cells.push({ d, dateStr, other: true });
  }
  return cells;
}

export function Planner() {
  const luna = useLuna();
  const today = todayStr();

  const now = new Date();
  const [calYear, setCalYear] = useState(now.getFullYear());
  const [calMonth, setCalMonth] = useState(now.getMonth());
  const [selectedDate, setSelectedDate] = useState(null);

  const [evTime, setEvTime] = useState("09:00");
  const [evTitle, setEvTitle] = useState("");
  const [evType, setEvType] = useState("default");

  const [reflectionDraft, setReflectionDraft] = useState("");

  const events = luna.getEvents();
  const cells = useMemo(() => buildCalendarCells(calYear, calMonth), [calYear, calMonth]);

  const dayEvents = useMemo(() => {
    if (!selectedDate) return [];
    return events
      .filter((e) => e.date === selectedDate)
      .sort((a, b) => (a.time || "").localeCompare(b.time || ""));
  }, [events, selectedDate]);

  const openDay = (dateStr) => {
    setSelectedDate(dateStr);
    const o = luna.getReflections();
    const t = typeof o === "object" && o[dateStr] != null ? o[dateStr] : "";
    setReflectionDraft(t);
  };

  const addEvent = (e) => {
    e.preventDefault();
    if (!selectedDate) return;
    const title = evTitle.trim();
    if (!title) return;
    luna.setEvents([...events, { id: newId(), date: selectedDate, time: evTime, title, type: evType }]);
    setEvTitle("");
  };

  const removeEvent = (eid) => {
    if (!confirm("Remove this event?")) return;
    luna.setEvents(events.filter((x) => x.id !== eid));
  };

  const saveReflection = () => {
    if (!selectedDate) return;
    const o = luna.getReflections();
    const next = typeof o === "object" && o ? { ...o } : {};
    next[selectedDate] = reflectionDraft.trim();
    luna.setReflections(next);
  };

  const calPrev = () => {
    let m = calMonth - 1;
    let y = calYear;
    if (m < 0) {
      m = 11;
      y--;
    }
    setCalMonth(m);
    setCalYear(y);
  };

  const calNext = () => {
    let m = calMonth + 1;
    let y = calYear;
    if (m > 11) {
      m = 0;
      y++;
    }
    setCalMonth(m);
    setCalYear(y);
  };

  const [sportType, setSportType] = useState("Yoga");
  const [sportDuration, setSportDuration] = useState("");
  const [sportDate, setSportDate] = useState(todayStr());

  const logSport = (e) => {
    e.preventDefault();
    const duration = parseInt(sportDuration, 10) || 0;
    if (!sportDate || duration <= 0) return;
    luna.setSport([...luna.getSport(), { id: newId(), type: sportType, duration, date: sportDate }]);
    setSportDuration("");
    setSportDate(todayStr());
  };

  const [sleepStart, setSleepStart] = useState("");
  const [sleepEnd, setSleepEnd] = useState("");
  const [sleepDate, setSleepDate] = useState(todayStr());

  const logSleep = (e) => {
    e.preventDefault();
    if (!sleepStart || !sleepEnd || !sleepDate) return;
    const s = sleepStart.split(":").map(Number);
    const e2 = sleepEnd.split(":").map(Number);
    let mins = e2[0] * 60 + e2[1] - (s[0] * 60 + s[1]);
    if (mins <= 0) mins += 24 * 60;
    const hours = (mins / 60).toFixed(1);
    luna.setSleep([
      ...luna.getSleep(),
      { id: newId(), date: sleepDate, start: sleepStart, end: sleepEnd, hours },
    ]);
    setSleepStart("");
    setSleepEnd("");
    setSleepDate(todayStr());
  };

  const sportList = luna.getSport().slice().reverse().slice(0, 20);
  const sleepList = luna.getSleep().slice().reverse().slice(0, 14);

  return (
    <section className="page page-planner active">
      <div className="section-head">
        <h2 className="section-title">Plan &amp; wellness</h2>
        <p className="section-desc">Your day, your rhythm. Schedule, reflect, and track what supports you.</p>
      </div>

      <div className="card card-calendar">
        <div className="cal-header">
          <h3 className="cal-title">
            {MONTH_NAMES[calMonth]} {calYear}
          </h3>
          <div className="cal-nav">
            <button type="button" className="btn-icon" aria-label="Previous month" onClick={calPrev}>
              ‹
            </button>
            <button type="button" className="btn-icon" aria-label="Next month" onClick={calNext}>
              ›
            </button>
          </div>
        </div>
        <div className="cal-weekdays">
          {WEEKDAYS.map((w) => (
            <div key={w} className="cal-weekday">
              {w}
            </div>
          ))}
        </div>
        <div className="cal-days">
          {cells.map(({ d, dateStr, other }) => {
            const hasEv = events.some((ev) => ev.date === dateStr);
            let cls = "cal-day";
            if (other) cls += " other-month";
            if (dateStr === today) cls += " today";
            if (hasEv) cls += " has-events";
            return (
              <button key={`${dateStr}-${d}`} type="button" className={cls} onClick={() => openDay(dateStr)}>
                {d}
              </button>
            );
          })}
        </div>
      </div>

      {selectedDate && (
        <div className="card day-detail">
          <h3 className="card-title">
            {MONTH_NAMES[parseInt(selectedDate.split("-")[1], 10) - 1]} {parseInt(selectedDate.split("-")[2], 10)}
          </h3>
          <div className="day-events">
            {dayEvents.length === 0 ? (
              <p className="hint">Nothing scheduled yet. Add something above.</p>
            ) : (
              dayEvents.map((ev) => (
                <div key={ev.id} className="day-event">
                  <span className="day-event-main">
                    <span className="day-event-time">{ev.time}</span> <span className="day-event-title">{ev.title}</span>
                  </span>
                  <button type="button" className="day-event-del" onClick={() => removeEvent(ev.id)}>
                    Remove
                  </button>
                </div>
              ))
            )}
          </div>
          <form className="form form-inline" onSubmit={addEvent}>
            <input
              type="time"
              className="input input-sm"
              value={evTime}
              onChange={(e) => setEvTime(e.target.value)}
              required
            />
            <input
              type="text"
              className="input input-sm"
              value={evTitle}
              onChange={(e) => setEvTitle(e.target.value)}
              placeholder="Event"
              required
            />
            <select className="input input-sm" value={evType} onChange={(e) => setEvType(e.target.value)}>
              <option value="default">General</option>
              <option value="yoga">Yoga</option>
              <option value="gym">Workout</option>
              <option value="study">Study</option>
              <option value="sleep">Rest</option>
            </select>
            <button type="submit" className="btn btn-primary btn-sm">
              Add
            </button>
          </form>
          <div className="form-row">
            <label>Today’s reflection</label>
            <textarea
              className="input"
              value={reflectionDraft}
              onChange={(e) => setReflectionDraft(e.target.value)}
              placeholder="How did today go? A few lines is enough."
              rows={3}
            />
          </div>
          <button type="button" className="btn btn-soft" onClick={saveReflection}>
            Save reflection
          </button>
        </div>
      )}

      <div className="card">
        <h3 className="card-title">Movement</h3>
        <p className="card-hint">Log sessions to see your week at a glance on Home.</p>
        <form className="form form-row-inline" onSubmit={logSport}>
          <select className="input input-sm" value={sportType} onChange={(e) => setSportType(e.target.value)}>
            <option value="Yoga">Yoga</option>
            <option value="Run">Run</option>
            <option value="Gym">Gym</option>
            <option value="Other">Other</option>
          </select>
          <input
            type="number"
            className="input input-sm"
            value={sportDuration}
            onChange={(e) => setSportDuration(e.target.value)}
            placeholder="min"
            min="1"
          />
          <input
            type="date"
            className="input input-sm"
            value={sportDate}
            onChange={(e) => setSportDate(e.target.value)}
          />
          <button type="submit" className="btn btn-primary btn-sm">
            Log
          </button>
        </form>
        <ul className="log-list">
          {sportList.length === 0 ? (
            <li className="hint">No sessions yet. Log one above.</li>
          ) : (
            sportList.map((s) => (
              <li key={s.id}>
                {s.type} {s.duration || 0} min · {s.date}
              </li>
            ))
          )}
        </ul>
      </div>

      <div className="card">
        <h3 className="card-title">Sleep</h3>
        <p className="card-hint">Track rest to spot patterns and protect your energy.</p>
        <form className="form form-row-inline" onSubmit={logSleep}>
          <input
            type="time"
            className="input input-sm"
            value={sleepStart}
            onChange={(e) => setSleepStart(e.target.value)}
          />
          <input
            type="time"
            className="input input-sm"
            value={sleepEnd}
            onChange={(e) => setSleepEnd(e.target.value)}
          />
          <input
            type="date"
            className="input input-sm"
            value={sleepDate}
            onChange={(e) => setSleepDate(e.target.value)}
          />
          <button type="submit" className="btn btn-primary btn-sm">
            Save
          </button>
        </form>
        <ul className="log-list">
          {sleepList.length === 0 ? (
            <li className="hint">No entries yet. Log last night above.</li>
          ) : (
            sleepList.map((s) => (
              <li key={s.id}>
                {s.start} → {s.end} · {s.hours} hrs · {s.date}
              </li>
            ))
          )}
        </ul>
      </div>
    </section>
  );
}
