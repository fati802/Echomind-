"use client";

import { useState, useRef, useEffect, useMemo } from "react";

const DAY_LABELS = ["S", "M", "T", "W", "T", "F", "S"];
const MONTH_LABELS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

function toDateString(d) {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

function CalendarIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      <rect x="3" y="4" width="18" height="18" rx="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  );
}

function ChevronLeft() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <polyline points="15 18 9 12 15 6" />
    </svg>
  );
}

function ChevronRight() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <polyline points="9 18 15 12 9 6" />
    </svg>
  );
}

export default function MiniCalendar({ value, onChange, disabled }) {
  const [open, setOpen] = useState(false);
  const [viewYear, setViewYear] = useState(() => (value ? new Date(value).getFullYear() : new Date().getFullYear()));
  const [viewMonth, setViewMonth] = useState(() => (value ? new Date(value).getMonth() : new Date().getMonth()));
  const rootRef = useRef(null);

  useEffect(() => {
    if (value) {
      const d = new Date(value);
      setViewYear(d.getFullYear());
      setViewMonth(d.getMonth());
    }
  }, [value]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (rootRef.current && !rootRef.current.contains(e.target)) setOpen(false);
    };
    const handleEsc = (e) => {
      if (e.key === "Escape") setOpen(false);
    };
    if (open) {
      document.addEventListener("mousedown", handleClickOutside);
      document.addEventListener("keydown", handleEsc);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEsc);
    };
  }, [open]);

  const grid = useMemo(() => {
    const firstOfMonth = new Date(viewYear, viewMonth, 1);
    const startWeekday = firstOfMonth.getDay();
    const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();
    const cells = [];
    for (let i = 0; i < startWeekday; i++) cells.push(null);
    for (let day = 1; day <= daysInMonth; day++) {
      const d = new Date(viewYear, viewMonth, day);
      cells.push({
        day,
        dateStr: toDateString(d),
        weekday: d.getDay(),
      });
    }
    while (cells.length % 7 !== 0) cells.push(null);
    return cells;
  }, [viewYear, viewMonth]);

  const todayStr = toDateString(new Date());

  const changeMonth = (delta) => {
    let m = viewMonth + delta;
    let y = viewYear;
    if (m < 0) { m = 11; y -= 1; }
    if (m > 11) { m = 0; y += 1; }
    setViewMonth(m);
    setViewYear(y);
  };

  const changeYear = (delta) => {
    setViewYear(viewYear + delta);
  };

  const pick = (dateStr) => {
    onChange(dateStr);
    setOpen(false);
  };

  const displayLabel = value
    ? new Date(value + "T00:00:00").toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })
    : "Pick a date";

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        disabled={disabled}
        className="flex items-center gap-2 bg-white border border-cream-darker hover:border-teal-500 rounded-xl px-3.5 h-10 text-sm font-medium text-dark transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
        aria-haspopup="dialog"
        aria-expanded={open}
      >
        <span className="text-teal-700"><CalendarIcon /></span>
        <span>{displayLabel}</span>
      </button>

      {open && (
        <div
          role="dialog"
          aria-label="Choose a date"
          className="absolute right-0 mt-2 z-50 w-[320px] bg-white rounded-2xl border border-teal-100 shadow-[0_10px_40px_rgba(45,90,78,0.18)] p-4 fade-in"
        >
          {/* Header — month + year with navigation */}
          <div className="flex items-center justify-between mb-3">
            <button
              type="button"
              onClick={() => changeYear(-1)}
              className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-teal-50 text-dark/60 hover:text-teal-700 transition-colors cursor-pointer"
              aria-label="Previous year"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <polyline points="11 17 6 12 11 7" />
                <polyline points="18 17 13 12 18 7" />
              </svg>
            </button>
            <button
              type="button"
              onClick={() => changeMonth(-1)}
              className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-teal-50 text-dark/60 hover:text-teal-700 transition-colors cursor-pointer"
              aria-label="Previous month"
            >
              <ChevronLeft />
            </button>

            <div className="flex-1 text-center">
              <p className="text-sm font-semibold text-dark tracking-tight">
                {MONTH_LABELS[viewMonth]} <span className="text-dark/50 font-medium">{viewYear}</span>
              </p>
            </div>

            <button
              type="button"
              onClick={() => changeMonth(1)}
              className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-teal-50 text-dark/60 hover:text-teal-700 transition-colors cursor-pointer"
              aria-label="Next month"
            >
              <ChevronRight />
            </button>
            <button
              type="button"
              onClick={() => changeYear(1)}
              className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-teal-50 text-dark/60 hover:text-teal-700 transition-colors cursor-pointer"
              aria-label="Next year"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <polyline points="13 17 18 12 13 7" />
                <polyline points="6 17 11 12 6 7" />
              </svg>
            </button>
          </div>

          {/* Weekday labels */}
          <div className="grid grid-cols-7 gap-1 mb-1">
            {DAY_LABELS.map((d, i) => (
              <div key={i} className="text-[0.65rem] uppercase tracking-wider text-dark/40 font-semibold text-center py-1">
                {d}
              </div>
            ))}
          </div>

          {/* Day grid */}
          <div className="grid grid-cols-7 gap-1">
            {grid.map((cell, idx) => {
              if (!cell) return <div key={idx}></div>;
              const isSelected = cell.dateStr === value;
              const isToday = cell.dateStr === todayStr;
              const isWeekend = cell.weekday === 0 || cell.weekday === 6;

              return (
                <button
                  key={idx}
                  type="button"
                  onClick={() => pick(cell.dateStr)}
                  className={`h-9 w-full flex items-center justify-center text-sm rounded-lg transition-all cursor-pointer relative ${
                    isSelected
                      ? "bg-teal-600 text-white font-semibold shadow-[0_2px_8px_rgba(29,107,92,0.35)]"
                      : isToday
                        ? "bg-teal-50 text-teal-700 font-semibold border border-teal-100"
                        : isWeekend
                          ? "text-dark/50 hover:bg-cream-darker hover:text-teal-700"
                          : "text-dark/80 hover:bg-cream-darker hover:text-teal-700"
                  }`}
                  aria-pressed={isSelected}
                  aria-label={cell.dateStr}
                >
                  {cell.day}
                </button>
              );
            })}
          </div>

          {/* Footer — quick actions */}
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-cream-darker">
            <button
              type="button"
              onClick={() => pick(todayStr)}
              className="text-xs font-medium text-teal-700 hover:text-teal-500 cursor-pointer"
            >
              Jump to today
            </button>
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="text-xs font-medium text-dark/50 hover:text-dark cursor-pointer"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
