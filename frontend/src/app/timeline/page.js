"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function Timeline() {
  const [dateString, setDateString] = useState("");
  const [timelineData, setTimelineData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);

  // Fetch timeline data from API
  const fetchTimeline = async (targetDate) => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
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
    // Initial fetch defaults to most recent date
    fetchTimeline("");
  }, []);

  const handleDateChange = (e) => {
    const newDate = e.target.value;
    if (newDate) {
      setDateString(newDate);
      fetchTimeline(newDate);
    }
  };

  const navigateDays = (offset) => {
    if (!dateString) return;
    const currentDate = new Date(dateString);
    currentDate.setDate(currentDate.getDate() + offset);
    
    const yyyy = currentDate.getFullYear();
    const mm = String(currentDate.getMonth() + 1).padStart(2, "0");
    const dd = String(currentDate.getDate()).padStart(2, "0");
    const newDateStr = `${yyyy}-${mm}-${dd}`;
    
    setDateString(newDateStr);
    fetchTimeline(newDateStr);
  };

  const formatTime = (isoString) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (e) {
      return isoString;
    }
  };

  // Reassuring display text for actions
  const formatEventDescription = (evt) => {
    const object = evt.object.toLowerCase();
    const action = evt.action.toLowerCase().replace("_", " ");
    const actorText = evt.actor ? `by ${evt.actor}` : "";
    const zoneText = evt.zone ? `at the ${evt.zone}` : "";

    return (
      <span className="text-lg">
        The <strong className="text-teal-600 capitalize">{object}</strong> was <strong className="text-teal-600">{action}</strong> {actorText} {zoneText}.
      </span>
    );
  };

  const renderEventList = (events, emptyMessage) => {
    if (!events || events.length === 0) {
      return (
        <p className="text-dark/50 italic text-base py-2 pl-4 border-l-2 border-cream-darker">
          {emptyMessage}
        </p>
      );
    }

    return (
      <ul className="space-y-4">
        {events.map((evt) => (
          <li 
            key={evt.id} 
            className="flex items-start space-x-3 bg-white p-4 rounded-xl border border-cream-darker shadow-sm"
          >
            <span className="text-sm font-mono bg-teal-50 text-teal-600 px-2 py-1 rounded font-semibold whitespace-nowrap mt-0.5">
              {formatTime(evt.timestamp)}
            </span>
            <div className="flex-1 flex flex-col">
              {formatEventDescription(evt)}
              {evt.confidence < 0.7 && (
                <span className="text-xs text-gold font-medium mt-1">
                  Note: Muted confirmation record (confidence: {Math.round(evt.confidence * 100)}%)
                </span>
              )}
            </div>
          </li>
        ))}
      </ul>
    );
  };

  return (
    <div className="flex flex-col min-h-screen bg-cream">
      {/* Premium Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-teal-100 py-4 px-6 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-2xl" role="img" aria-label="flower">🌸</span>
          <span className="text-2xl font-semibold tracking-tight text-teal-600 font-sans">EchoMind</span>
        </div>
        <nav className="flex space-x-6 text-lg font-medium" aria-label="Primary Navigation">
          <Link 
            id="nav-chat" 
            href="/" 
            className="text-dark/70 hover:text-teal-600 transition-colors pb-1"
          >
            Ask Questions
          </Link>
          <Link 
            id="nav-timeline" 
            href="/timeline" 
            className="text-teal-600 border-b-2 border-teal-500 pb-1"
          >
            My Day's Timeline
          </Link>
        </nav>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-3xl w-full mx-auto p-4 sm:p-6 space-y-6">
        <h1 className="sr-only">EchoMind Caring Timeline</h1>

        {/* Date Selector Header Card */}
        <section className="bg-white rounded-2xl shadow-sm border border-teal-100 p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex flex-col">
            <h2 className="text-2xl font-semibold text-dark font-sans">Daily Activity Log</h2>
            <p className="text-base text-dark/60 mt-1">A simple timeline of events detected throughout your day.</p>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              id="btn-prev-day"
              onClick={() => navigateDays(-1)}
              className="bg-cream hover:bg-cream-darker text-dark px-4 py-2.5 rounded-xl border border-cream-darker text-lg font-medium transition-colors cursor-pointer"
              disabled={isLoading}
            >
              ⬅ Yesterday
            </button>
            <input
              id="timeline-date-picker"
              type="date"
              value={dateString}
              onChange={handleDateChange}
              className="bg-white border border-teal-500/30 text-dark rounded-xl px-4 py-2.5 text-lg font-medium text-center focus:outline-none focus:border-teal-500"
              disabled={isLoading}
            />
            <button
              id="btn-next-day"
              onClick={() => navigateDays(1)}
              className="bg-cream hover:bg-cream-darker text-dark px-4 py-2.5 rounded-xl border border-cream-darker text-lg font-medium transition-colors cursor-pointer"
              disabled={isLoading}
            >
              Tomorrow ➡
            </button>
          </div>
        </section>

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12 bg-white rounded-2xl border border-cream-darker shadow-sm flex flex-col items-center justify-center space-y-3">
            <div className="w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-lg text-dark/60 font-medium">Gathering notes about your day...</p>
          </div>
        )}

        {/* Error State */}
        {errorMsg && (
          <div 
            id="timeline-error-state"
            className="bg-red-50 border border-red-200 text-red-800 rounded-2xl p-6 shadow-sm"
            role="alert"
          >
            <h3 className="font-semibold text-lg mb-1">We had an issue reading the logs:</h3>
            <p className="text-base">{errorMsg}</p>
            <button 
              onClick={() => fetchTimeline(dateString)} 
              className="mt-3 bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg text-sm transition-colors"
            >
              Try Loading Again
            </button>
          </div>
        )}

        {/* Timeline Event Lists */}
        {!isLoading && !errorMsg && timelineData && (
          <div className="space-y-6">
            {/* Header displaying selected date */}
            <div className="text-center">
              <h3 className="text-xl font-medium text-dark bg-teal-50/50 inline-block px-6 py-2 rounded-full border border-teal-100/50">
                Timeline for <strong className="text-teal-600">{timelineData.date ? new Date(timelineData.date + "T00:00:00").toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) : ""}</strong>
              </h3>
            </div>

            {/* Morning Bucket */}
            <section className="bg-white rounded-2xl shadow-sm border border-cream-darker p-6 space-y-4">
              <h4 className="text-xl font-semibold text-teal-600 flex items-center gap-2">
                <span>🌅</span> Morning <span className="text-sm font-normal text-dark/50">(05:00 - 11:59)</span>
              </h4>
              {renderEventList(timelineData.morning, "It was a peaceful morning with no events recorded.")}
            </section>

            {/* Afternoon Bucket */}
            <section className="bg-white rounded-2xl shadow-sm border border-cream-darker p-6 space-y-4">
              <h4 className="text-xl font-semibold text-teal-600 flex items-center gap-2">
                <span>☀️</span> Afternoon <span className="text-sm font-normal text-dark/50">(12:00 - 14:59)</span>
              </h4>
              {renderEventList(timelineData.afternoon, "Everything was quiet during the afternoon.")}
            </section>

            {/* Evening Bucket */}
            <section className="bg-white rounded-2xl shadow-sm border border-cream-darker p-6 space-y-4">
              <h4 className="text-xl font-semibold text-teal-600 flex items-center gap-2">
                <span>🌇</span> Evening <span className="text-sm font-normal text-dark/50">(15:00 - 18:59)</span>
              </h4>
              {renderEventList(timelineData.evening, "No events logged for this evening.")}
            </section>

            {/* Night Bucket */}
            <section className="bg-white rounded-2xl shadow-sm border border-cream-darker p-6 space-y-4">
              <h4 className="text-xl font-semibold text-teal-600 flex items-center gap-2">
                <span>🌙</span> Night <span className="text-sm font-normal text-dark/50">(19:00 - 04:59)</span>
              </h4>
              {renderEventList(timelineData.night, "Sleep well! No events logged overnight.")}
            </section>
          </div>
        )}
      </main>

      {/* Reassuring Footer */}
      <footer className="py-6 border-t border-teal-100 text-center text-sm text-dark/50 mt-12">
        <p>EchoMind is always here to help you remember. Your privacy is fully protected.</p>
      </footer>
    </div>
  );
}
