"use client";

import { useState, useEffect, useMemo } from "react";
import MiniCalendar from "@/app/components/MiniCalendar";

function ArrowLeftIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <polyline points="15 18 9 12 15 6" />
    </svg>
  );
}

function ArrowRightIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <polyline points="9 18 15 12 9 6" />
    </svg>
  );
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

function MorningIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
      <circle cx="12" cy="14" r="4" />
      <line x1="12" y1="2" x2="12" y2="6" />
      <line x1="4.2" y1="9.2" x2="6.3" y2="10.6" />
      <line x1="19.8" y1="9.2" x2="17.7" y2="10.6" />
      <line x1="3" y1="19" x2="21" y2="19" />
    </svg>
  );
}

function AfternoonIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
      <circle cx="12" cy="12" r="4" />
      <line x1="12" y1="2" x2="12" y2="4" />
      <line x1="12" y1="20" x2="12" y2="22" />
      <line x1="4.2" y1="4.2" x2="5.6" y2="5.6" />
      <line x1="18.4" y1="18.4" x2="19.8" y2="19.8" />
      <line x1="2" y1="12" x2="4" y2="12" />
      <line x1="20" y1="12" x2="22" y2="12" />
      <line x1="4.2" y1="19.8" x2="5.6" y2="18.4" />
      <line x1="18.4" y1="5.6" x2="19.8" y2="4.2" />
    </svg>
  );
}

function EveningIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
      <circle cx="12" cy="10" r="4" />
      <line x1="4.2" y1="14.8" x2="6.3" y2="13.4" />
      <line x1="19.8" y1="14.8" x2="17.7" y2="13.4" />
      <line x1="12" y1="22" x2="12" y2="18" />
      <line x1="3" y1="18" x2="21" y2="18" />
    </svg>
  );
}

function NightIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
      <path d="M20 14.5A8.5 8.5 0 1 1 9.5 4a7 7 0 0 0 10.5 10.5z" />
    </svg>
  );
}

const SEGMENTS = [
  {
    key: "morning",
    label: "Morning",
    range: "05:00 – 11:59",
    Icon: MorningIcon,
    empty: "A peaceful morning — nothing recorded.",
    accent: "warning",
  },
  {
    key: "afternoon",
    label: "Afternoon",
    range: "12:00 – 14:59",
    Icon: AfternoonIcon,
    empty: "Everything was quiet this afternoon.",
    accent: "teal",
  },
  {
    key: "evening",
    label: "Evening",
    range: "15:00 – 18:59",
    Icon: EveningIcon,
    empty: "No events logged for the evening.",
    accent: "rose",
  },
  {
    key: "night",
    label: "Night",
    range: "19:00 – 04:59",
    Icon: NightIcon,
    empty: "Sleep well — no events overnight.",
    accent: "teal-dark",
  },
];

const ACCENT_MAP = {
  warning: {
    dot: "bg-warning-500",
    ring: "ring-warning-500/25",
    text: "text-warning-700",
    softBg: "bg-warning-50/60",
    border: "border-warning-500/25",
  },
  teal: {
    dot: "bg-teal-500",
    ring: "ring-teal-500/25",
    text: "text-teal-700",
    softBg: "bg-teal-50",
    border: "border-teal-500/25",
  },
  rose: {
    dot: "bg-rose-600",
    ring: "ring-rose-600/20",
    text: "text-rose-600",
    softBg: "bg-rose-50/60",
    border: "border-rose-600/25",
  },
  "teal-dark": {
    dot: "bg-teal-700",
    ring: "ring-teal-700/25",
    text: "text-teal-700",
    softBg: "bg-teal-50/60",
    border: "border-teal-700/25",
  },
};

const DAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

function toDateString(d) {
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

export default function Timeline() {
  const [dateString, setDateString] = useState("");
  const [timelineData, setTimelineData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  const fetchTimeline = async (targetDate) => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
      const queryParam = targetDate ? `?date=${targetDate}` : "";
      const response = await fetch(`${apiUrl}/api/timeline${queryParam}`);
      if (!response.ok) {
        throw new Error("I could not load the timeline. Please check your connection and try again.");
      }
      const data = await response.json();
      setTimelineData(data);
      setDateString(data.date);
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || "Failed to load timeline data.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTimeline("");
  }, []);

  const handleDateChange = (newDate) => {
    if (newDate) {
      setDateString(newDate);
      fetchTimeline(newDate);
    }
  };

  const navigateDays = (offset) => {
    if (!dateString) return;
    const currentDate = new Date(dateString);
    currentDate.setDate(currentDate.getDate() + offset);
    const newDateStr = toDateString(currentDate);
    setDateString(newDateStr);
    fetchTimeline(newDateStr);
  };

  const jumpTo = (dateStr) => {
    setDateString(dateStr);
    fetchTimeline(dateStr);
  };

  const formatTime = (isoString) => {
    try {
      return new Date(isoString).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } catch {
      return isoString;
    }
  };

  // Build a 7-day strip centered on the selected date
  const weekStrip = useMemo(() => {
    if (!dateString) return [];
    const base = new Date(dateString);
    const days = [];
    for (let i = -3; i <= 3; i++) {
      const d = new Date(base);
      d.setDate(base.getDate() + i);
      days.push({
        dateStr: toDateString(d),
        day: d.getDate(),
        weekday: DAY_LABELS[d.getDay()],
        isToday: toDateString(new Date()) === toDateString(d),
        isSelected: toDateString(d) === dateString,
      });
    }
    return days;
  }, [dateString]);

  const totalEvents = timelineData
    ? SEGMENTS.reduce((sum, s) => sum + (timelineData[s.key]?.length || 0), 0)
    : 0;

  const prettyDate = timelineData?.date
    ? new Date(timelineData.date + "T00:00:00").toLocaleDateString(undefined, {
        weekday: "long",
        month: "long",
        day: "numeric",
      })
    : "";

  const prettyMonthYear = timelineData?.date
    ? new Date(timelineData.date + "T00:00:00").toLocaleDateString(undefined, {
        month: "long",
        year: "numeric",
      })
    : "";

  const firstEventTime = useMemo(() => {
    if (!timelineData) return null;
    for (const seg of SEGMENTS) {
      const list = timelineData[seg.key];
      if (list && list.length > 0) return formatTime(list[0].timestamp);
    }
    return null;
  }, [timelineData]);

  const lastEventTime = useMemo(() => {
    if (!timelineData) return null;
    for (let i = SEGMENTS.length - 1; i >= 0; i--) {
      const list = timelineData[SEGMENTS[i].key];
      if (list && list.length > 0) return formatTime(list[list.length - 1].timestamp);
    }
    return null;
  }, [timelineData]);

  return (
    <div className="w-full px-5 sm:px-8 lg:px-12 pt-6 pb-16">
      <h1 className="sr-only">EchoMind Timeline</h1>

      {/* HEADER — title left, date controls right */}
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-6">
        <div>
          <p className="text-xs uppercase tracking-[0.22em] text-teal-600 font-medium">Timeline</p>
          <h2 className="text-3xl font-semibold text-dark mt-1 tracking-tight">Your day, gently</h2>
          <p className="text-sm text-dark/55 mt-1.5">
            {prettyMonthYear && <span className="font-medium text-dark/70">{prettyMonthYear} · </span>}
            A calm view of what happened throughout the day.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => navigateDays(-1)}
            className="flex items-center justify-center w-10 h-10 rounded-xl bg-white border border-cream-darker hover:border-teal-500 hover:text-teal-700 text-dark/70 transition-colors cursor-pointer disabled:opacity-40"
            disabled={isLoading}
            aria-label="Previous day"
          >
            <ArrowLeftIcon />
          </button>
          <MiniCalendar
            value={dateString}
            onChange={handleDateChange}
            disabled={isLoading}
          />
          <div id="timeline-date-picker" className="hidden" data-value={dateString} />
          <button
            onClick={() => navigateDays(1)}
            className="flex items-center justify-center w-10 h-10 rounded-xl bg-white border border-cream-darker hover:border-teal-500 hover:text-teal-700 text-dark/70 transition-colors cursor-pointer disabled:opacity-40"
            disabled={isLoading}
            aria-label="Next day"
          >
            <ArrowRightIcon />
          </button>
          <button
            onClick={() => jumpTo(toDateString(new Date()))}
            className="ml-1 px-4 h-10 rounded-xl bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium transition-colors cursor-pointer disabled:opacity-40"
            disabled={isLoading}
          >
            Today
          </button>
        </div>
      </div>

      {/* WEEK STRIP */}
      <div className="card-soft p-3 mb-6">
        <div className="flex items-stretch gap-2">
          {weekStrip.map((d) => (
            <button
              key={d.dateStr}
              onClick={() => jumpTo(d.dateStr)}
              disabled={isLoading}
              className={`flex-1 flex flex-col items-center justify-center py-3 rounded-xl transition-all cursor-pointer ${
                d.isSelected
                  ? "bg-teal-600 text-white shadow-[0_4px_16px_rgba(29,107,92,0.25)]"
                  : d.isToday
                    ? "bg-teal-50 text-teal-700 border border-teal-100"
                    : "bg-cream/50 text-dark/70 hover:bg-cream-darker/60"
              } disabled:opacity-40`}
            >
              <span className={`text-[0.65rem] uppercase tracking-wider font-medium ${d.isSelected ? "text-white/80" : "opacity-70"}`}>
                {d.weekday}
              </span>
              <span className="text-lg font-semibold mt-0.5">{d.day}</span>
              {d.isToday && !d.isSelected && (
                <span className="w-1 h-1 rounded-full bg-teal-600 mt-1"></span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* STATS ROW */}
      {timelineData && !isLoading && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6 fade-in">
          <div className="card-soft p-4">
            <p className="text-[0.7rem] uppercase tracking-widest text-dark/45 font-medium">Viewing</p>
            <p className="text-sm font-semibold text-teal-700 mt-1">{prettyDate}</p>
          </div>
          <div className="card-soft p-4">
            <p className="text-[0.7rem] uppercase tracking-widest text-dark/45 font-medium">Events</p>
            <p className="text-2xl font-semibold text-dark mt-0.5">{totalEvents}</p>
          </div>
          <div className="card-soft p-4">
            <p className="text-[0.7rem] uppercase tracking-widest text-dark/45 font-medium">First activity</p>
            <p className="text-2xl font-semibold text-dark mt-0.5 font-mono">{firstEventTime || "—"}</p>
          </div>
          <div className="card-soft p-4">
            <p className="text-[0.7rem] uppercase tracking-widest text-dark/45 font-medium">Last activity</p>
            <p className="text-2xl font-semibold text-dark mt-0.5 font-mono">{lastEventTime || "—"}</p>
          </div>
        </div>
      )}

      {/* MAIN */}
      {isLoading && (
        <div className="card-soft py-16 flex items-center justify-start gap-3 pl-8">
          <div className="w-6 h-6 border-[3px] border-teal-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm text-dark/60">Gathering notes about your day…</p>
        </div>
      )}

      {errorMsg && (
        <div
          id="timeline-error-state"
          className="bg-critical-50 border border-critical-500/40 text-critical-700 rounded-2xl p-5"
          role="alert"
        >
          <h3 className="font-semibold mb-1">We had trouble reading the logs</h3>
          <p className="text-sm text-critical-700/85">{errorMsg}</p>
          <button
            onClick={() => fetchTimeline(dateString)}
            className="mt-3 bg-critical-500 hover:bg-critical-700 text-white font-medium py-2 px-4 rounded-lg text-sm transition-colors cursor-pointer"
          >
            Try again
          </button>
        </div>
      )}

      {!isLoading && !errorMsg && timelineData && (
        <div className="card-soft p-6 sm:p-8 fade-in">
          <div className="relative">
            {/* Vertical rail */}
            <div className="absolute left-[15px] top-2 bottom-2 w-px bg-gradient-to-b from-teal-100 via-cream-darker to-teal-100 hidden sm:block" aria-hidden="true"></div>

            <div className="space-y-8">
              {SEGMENTS.map((seg) => {
                const events = timelineData[seg.key] || [];
                const accent = ACCENT_MAP[seg.accent];

                return (
                  <section key={seg.key} className="relative sm:pl-12">
                    {/* Segment dot on rail */}
                    <div className={`hidden sm:flex absolute left-0 top-0 w-8 h-8 rounded-full items-center justify-center ${accent.softBg} ${accent.text} ring-4 ${accent.ring}`}>
                      <seg.Icon />
                    </div>

                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className={`sm:hidden ${accent.text}`}><seg.Icon /></span>
                        <h4 className={`text-base font-semibold ${accent.text}`}>{seg.label}</h4>
                        <span className={`chip ${accent.softBg} ${accent.text} border ${accent.border}`}>
                          {events.length}
                        </span>
                      </div>
                      <span className="text-xs text-dark/40 font-mono">{seg.range}</span>
                    </div>

                    {events.length === 0 ? (
                      <p className="text-dark/45 italic text-sm py-2 pl-4 border-l-2 border-cream-darker">
                        {seg.empty}
                      </p>
                    ) : (
                      <ul className="space-y-2.5">
                        {events.map((evt) => (
                          <li
                            key={evt.id}
                            className="group relative flex items-start gap-4 bg-cream/50 hover:bg-cream/80 transition-colors p-3.5 rounded-xl border border-cream-darker/60"
                          >
                            <span className="text-xs font-mono bg-white text-teal-700 px-2.5 py-1 rounded-md font-semibold whitespace-nowrap mt-0.5 border border-teal-100">
                              {formatTime(evt.timestamp)}
                            </span>
                            <div className="flex-1 text-left">
                              <span className="text-[0.98rem] leading-relaxed">
                                <strong className="text-teal-700 capitalize">{evt.object}</strong>{" "}
                                <span className="text-dark/70">was</span>{" "}
                                <strong className="text-teal-700">
                                  {evt.action.toLowerCase().replace("_", " ")}
                                </strong>
                                {evt.actor && <span className="text-dark/60"> by {evt.actor}</span>}
                                {evt.zone && <span className="text-dark/60"> at the {evt.zone}</span>}
                              </span>
                              {evt.confidence < 0.7 && (
                                <span className="block text-xs text-rose-600 font-medium mt-1">
                                  Muted confirmation ({Math.round(evt.confidence * 100)}% confidence)
                                </span>
                              )}
                            </div>
                          </li>
                        ))}
                      </ul>
                    )}
                  </section>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
