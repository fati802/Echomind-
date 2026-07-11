"use client";

import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

const POSITIVE_MESSAGES = [
  "Everything's right where it should be.",
  "All clear — nothing to worry about today.",
  "Your items are all accounted for. You're all set!",
  "Nothing out of place — enjoy your day.",
];

function LeafIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-teal-600 flex-shrink-0" aria-hidden="true">
      <path d="M4 20c8 0 14-6 14-14 0-1 0-2-.3-3C9 4 4 10 4 18v2z" />
      <path d="M4 20c2-6 6-10 12-12" />
    </svg>
  );
}

function WarningIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-warning-700 flex-shrink-0" aria-hidden="true">
      <path d="M12 3l10 18H2L12 3z" strokeLinejoin="round" />
      <line x1="12" y1="9" x2="12" y2="14" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  );
}

function CriticalIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-critical-700 flex-shrink-0" aria-hidden="true">
      <circle cx="12" cy="12" r="9" />
      <line x1="12" y1="8" x2="12" y2="13" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
}

export default function AlertBanner() {
  const [alerts, setAlerts] = useState([]);
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(true);
  const [positiveMsg] = useState(
    POSITIVE_MESSAGES[Math.floor(Math.random() * POSITIVE_MESSAGES.length)]
  );

  const fetchAlerts = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/alerts`);
      if (!res.ok) throw new Error("Failed to fetch alerts");
      const data = await res.json();
      setAlerts(data);
    } catch (err) {
      console.error("Alert fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return null;

  const hasAlerts = alerts.length > 0;
  const hasCritical = alerts.some((a) => a.severity === "critical");
  const topAlert = alerts[0];

  if (!hasAlerts) {
    return (
      <div className="w-full rounded-lg border px-4 py-3 mb-4 bg-teal-50 border-teal-100 text-teal-700">
        <div className="flex items-center gap-2">
          <LeafIcon />
          <span className="font-medium text-sm">{positiveMsg}</span>
        </div>
      </div>
    );
  }

  return (
    <div
      onClick={() => setExpanded(!expanded)}
      className={`w-full cursor-pointer transition-all rounded-lg border px-4 py-3 mb-4 ${
        hasCritical
          ? "bg-critical-50 border-critical-500 text-critical-700"
          : "bg-warning-50 border-warning-500 text-warning-700"
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {hasCritical ? <CriticalIcon /> : <WarningIcon />}
          <span className="font-medium text-sm">
            {alerts.length === 1
              ? topAlert.message
              : `${alerts.length} items need your attention — ${topAlert.object
                  .trim()
                  .toLowerCase()
                  .replace(/^\w/, (c) => c.toUpperCase())} the longest.`}
          </span>
        </div>
        <span className="text-xs opacity-70">
          {expanded ? "▲ collapse" : "▼ details"}
        </span>
      </div>

      {expanded && (
        <div className="mt-3 space-y-2 border-t border-current/20 pt-3">
          {alerts.map((a, i) => {
            const hours = Math.floor(a.minutes_elapsed / 60);
            const mins = Math.round(a.minutes_elapsed % 60);
            const timeStr = hours > 0 ? `${hours}h ${mins}m` : `${mins} min`;
            const displayName = a.object.trim().toLowerCase().replace(/^\w/, (c) => c.toUpperCase());

            return (
              <div
                key={i}
                className="flex items-center justify-between text-xs bg-white/50 rounded px-3 py-2"
              >
                <div>
                  <span className="font-semibold">{displayName}</span>{" "}
                  — {a.last_action.replace(/_/g, " ")}
                  {a.zone && <span className="opacity-70"> in {a.zone}</span>}
                </div>
                <span
                  className={`px-2 py-0.5 rounded-full font-medium ${
                    a.severity === "critical"
                      ? "bg-critical-500/20 text-critical-700"
                      : "bg-warning-500/20 text-warning-700"
                  }`}
                >
                  {timeStr}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}