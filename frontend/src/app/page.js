"use client";

import { useState, useRef, useEffect } from "react";

const SUGGESTIONS = [
  "Where are my glasses?",
  "Did I take my medicine today?",
  "When did I last see my keys?",
  "What did I do this morning?",
];

function SendIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 19V5" />
      <polyline points="5 12 12 5 19 12" />
    </svg>
  );
}

function AssistantMark() {
  return (
    <div className="w-9 h-9 rounded-full bg-gradient-to-br from-teal-50 to-white border border-teal-100 flex items-center justify-center flex-shrink-0 mt-0.5 shadow-[0_2px_8px_rgba(29,107,92,0.12)]">
      <svg width="22" height="22" viewBox="0 0 32 32" fill="none" aria-hidden="true">
        {/* outer echo arc */}
        <path
          d="M6 16a10 10 0 0 1 3-7.1"
          stroke="#2E8B6F"
          strokeOpacity="0.55"
          strokeWidth="1.6"
          strokeLinecap="round"
        />
        <path
          d="M26 16a10 10 0 0 1-3 7.1"
          stroke="#2E8B6F"
          strokeOpacity="0.55"
          strokeWidth="1.6"
          strokeLinecap="round"
        />
        {/* inner echo arc */}
        <path
          d="M10 16a6 6 0 0 1 2-4.5"
          stroke="#1D6B5C"
          strokeWidth="1.8"
          strokeLinecap="round"
        />
        <path
          d="M22 16a6 6 0 0 1-2 4.5"
          stroke="#1D6B5C"
          strokeWidth="1.8"
          strokeLinecap="round"
        />
        {/* center heart */}
        <path
          d="M16 20.5s-4-2.6-4-5.7a2.4 2.4 0 0 1 4-1.7 2.4 2.4 0 0 1 4 1.7c0 3.1-4 5.7-4 5.7z"
          fill="#7A2E4A"
        />
      </svg>
    </div>
  );
}

export default function Home() {
  const [messages, setMessages] = useState([
    {
      id: "initial-greet",
      sender: "system",
      text: "Hello, I'm EchoMind — your gentle memory companion. Ask me anything about your day.",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [expandedEvents, setExpandedEvents] = useState({});
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const toggleEvents = (msgId) => {
    setExpandedEvents((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const submitQuery = async (queryText) => {
    if (!queryText) return;
    setErrorMsg(null);

    const userMsgId = `user-${Date.now()}`;
    setMessages((prev) => [
      ...prev,
      {
        id: userMsgId,
        sender: "user",
        text: queryText,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
    setInputValue("");
    setIsLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
      const response = await fetch(`${apiUrl}/api/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: queryText }),
      });

      if (!response.ok) {
        throw new Error("I had a little trouble reaching my memory database. Could you try asking me again in a moment?");
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          id: `assistant-${Date.now()}`,
          sender: "assistant",
          text: data.answer || "I don't have a record of that yet",
          referencedEvents: data.referenced_events || [],
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = (e) => {
    e.preventDefault();
    submitQuery(inputValue.trim());
  };

  const formatTime = (isoString) => {
    try {
      return new Date(isoString).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } catch {
      return isoString;
    }
  };

  const isEmptyState = messages.length === 1 && messages[0].sender === "system";

  return (
    <div className="flex-1 flex flex-col w-full min-h-[calc(100vh-64px)]">
      <h1 className="sr-only">EchoMind Caring Chat Assistant</h1>

      {/* Scrollable content area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto w-full px-5 sm:px-8 lg:px-12 py-10">
          {isEmptyState ? (
            <div className="text-center pt-16 pb-6">
              <p className="text-xs uppercase tracking-[0.22em] text-teal-600 font-medium mb-3">
                EchoMind
              </p>
              <h2 className="text-3xl sm:text-4xl font-semibold text-dark tracking-tight">
                How can I help you remember?
              </h2>
              <p className="text-base text-dark/55 mt-3 max-w-xl mx-auto">
                Ask me anything about your day — where you left something, what you did, or how it went.
              </p>
            </div>
          ) : (
            <div className="space-y-8">
              {messages.map((msg) => {
                if (msg.sender === "system" && msg.id === "initial-greet") return null;

                const isUser = msg.sender === "user";

                if (isUser) {
                  return (
                    <div key={msg.id} className="flex justify-end fade-in">
                      <div className="max-w-[85%] bg-teal-600 text-white rounded-3xl rounded-br-lg px-5 py-3 text-[1.02rem] leading-relaxed">
                        {msg.text}
                      </div>
                    </div>
                  );
                }

                return (
                  <div key={msg.id} className="flex gap-3 fade-in">
                    <AssistantMark />
                    <div className="flex-1 min-w-0">
                      <div className="text-[1.02rem] leading-relaxed text-dark whitespace-pre-wrap">
                        {msg.text}
                      </div>

                      {msg.referencedEvents && msg.referencedEvents.length > 0 && (
                        <div className="mt-4">
                          <button
                            id={`btn-toggle-events-${msg.id}`}
                            onClick={() => toggleEvents(msg.id)}
                            className="text-teal-700 hover:text-teal-500 font-medium text-sm flex items-center gap-2 cursor-pointer"
                            aria-expanded={!!expandedEvents[msg.id]}
                            aria-controls={`events-details-${msg.id}`}
                          >
                            <svg
                              width="14"
                              height="14"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="2.5"
                              className={`transition-transform ${expandedEvents[msg.id] ? "rotate-90" : ""}`}
                              aria-hidden="true"
                            >
                              <polyline points="9 18 15 12 9 6" />
                            </svg>
                            <span>{expandedEvents[msg.id] ? "Hide" : "Show"} memory records</span>
                            <span className="chip bg-teal-50 text-teal-700 border border-teal-100">
                              {msg.referencedEvents.length}
                            </span>
                          </button>

                          {expandedEvents[msg.id] && (
                            <div id={`events-details-${msg.id}`} className="mt-3 space-y-2 fade-in">
                              {msg.referencedEvents.map((evt, idx) => (
                                <div
                                  key={evt.id || idx}
                                  className="text-sm bg-cream/70 border border-cream-darker rounded-xl p-3"
                                >
                                  <div className="flex items-start justify-between gap-3">
                                    <div className="text-left">
                                      <div className="font-semibold text-teal-700 capitalize">
                                        {evt.object} — {evt.action.replace("_", " ")}
                                      </div>
                                      <div className="text-xs text-dark/60 mt-1">
                                        {evt.zone || "Unknown Area"}
                                        {evt.actor && (
                                          <>
                                            {" · "}
                                            <span className="capitalize">{evt.actor}</span>
                                          </>
                                        )}
                                      </div>
                                    </div>
                                    <span className="text-xs font-mono text-dark/50 whitespace-nowrap">
                                      {formatTime(evt.timestamp)}
                                    </span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}

              {isLoading && (
                <div className="flex gap-3 fade-in">
                  <AssistantMark />
                  <div className="flex items-center gap-2 text-dark/50 pt-1.5">
                    <div className="flex space-x-1.5" aria-hidden="true">
                      <div className="w-2 h-2 bg-teal-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
                      <div className="w-2 h-2 bg-teal-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                      <div className="w-2 h-2 bg-teal-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
                    </div>
                  </div>
                </div>
              )}

              {errorMsg && (
                <div
                  id="chat-error-state"
                  className="bg-critical-50 border border-critical-500/40 text-critical-700 rounded-2xl p-4 text-sm fade-in"
                  role="alert"
                >
                  <div className="font-semibold mb-0.5">I had a little trouble</div>
                  <p className="text-critical-700/85">{errorMsg}</p>
                </div>
              )}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Bottom input area — always at bottom, wider */}
      <div className="sticky bottom-0 bg-gradient-to-t from-cream via-cream/95 to-cream/0 pt-6 pb-5">
        <div className="max-w-5xl mx-auto w-full px-5 sm:px-8 lg:px-12">
          {isEmptyState && (
            <div className="mb-4 flex flex-wrap gap-2 justify-center">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => submitQuery(s)}
                  className="text-sm px-4 py-2 rounded-full bg-white border border-teal-100 text-dark/70 hover:border-teal-500 hover:text-teal-700 hover:bg-teal-50/40 transition-colors cursor-pointer"
                >
                  {s}
                </button>
              ))}
            </div>
          )}

          <form
            onSubmit={handleSend}
            className="w-full bg-white rounded-3xl border border-teal-100/70 shadow-[0_4px_30px_rgba(45,90,78,0.08)] flex items-end gap-2 p-2 pl-6 transition-all focus-within:border-teal-500/60 focus-within:shadow-[0_4px_30px_rgba(45,90,78,0.14)] min-h-[68px]"
          >
            <input
              id="chat-input-question"
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask EchoMind about your day..."
              className="flex-1 bg-transparent py-3 text-base border-0 focus:outline-none placeholder-dark/35 text-dark"
              disabled={isLoading}
              autoComplete="off"
            />
            <button
              id="btn-chat-send"
              type="submit"
              disabled={isLoading || !inputValue.trim()}
              aria-label="Send"
              className="bg-teal-600 hover:bg-teal-700 text-white h-12 w-12 rounded-2xl transition-all disabled:opacity-25 disabled:cursor-not-allowed cursor-pointer flex items-center justify-center flex-shrink-0"
            >
              <SendIcon />
            </button>
          </form>

          <p className="text-center text-[0.7rem] text-dark/35 mt-2">
            EchoMind can make mistakes. Please verify important details.
          </p>
        </div>
      </div>
    </div>
  );
}
