"use client";

import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

const POSITIVE_MESSAGES = [
  "Everything's right where it should be. 🌿",
  "All clear — nothing to worry about today.",
  "Your items are all accounted for. You're all set!",
  "Nothing out of place — enjoy your day.",
];

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

  // No alerts — positive/reassuring state
  if (!hasAlerts) {
    return (
      <div className="w-full rounded-lg border px-4 py-3 mb-4 bg-emerald-50 border-emerald-200 text-emerald-800">
        <div className="flex items-center gap-2">
          <span className="text-lg">🌿</span>
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
          ? "bg-red-50 border-red-300 text-red-800"
          : "bg-amber-50 border-amber-300 text-amber-800"
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">{hasCritical ? "🔴" : "⚠️"}</span>
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
                      ? "bg-red-200 text-red-900"
                      : "bg-amber-200 text-amber-900"
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