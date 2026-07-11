"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";

export default function Home() {
  const [messages, setMessages] = useState([
    {
      id: "initial-greet",
      sender: "system",
      text: "Hello! I am EchoMind, your memory companion. How can I help you feel comfortable and recall your day? You can ask me things like 'Where are my glasses?' or 'Did I take my medicine today?'",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  
  // Track expanded message IDs for referenced events
  const [expandedEvents, setExpandedEvents] = useState({});

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const toggleEvents = (msgId) => {
    setExpandedEvents(prev => ({
      ...prev,
      [msgId]: !prev[msgId]
    }));
  };

  const handleSend = async (e) => {
    e.preventDefault();
    const queryText = inputValue.trim();
    if (!queryText) return;

    // Clear error
    setErrorMsg(null);

    // Add user message
    const userMsgId = `user-${Date.now()}`;
    const userMessage = {
      id: userMsgId,
      sender: "user",
      text: queryText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
      const response = await fetch(`${apiUrl}/api/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: queryText }),
      });

      if (!response.ok) {
        throw new Error("I had a little trouble reaching my memory database. Could you try asking me again in a moment?");
      }

      const data = await response.json();
      
      const assistantMsgId = `assistant-${Date.now()}`;
      const assistantMessage = {
        id: assistantMsgId,
        sender: "assistant",
        text: data.answer || "I don't have a record of that yet",
        referencedEvents: data.referenced_events || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  // Human friendly formatting for event logs
  const formatTime = (isoString) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (e) {
      return isoString;
    }
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
            className="text-teal-600 border-b-2 border-teal-500 pb-1"
          >
            Ask Questions
          </Link>
          <Link 
            id="nav-timeline" 
            href="/timeline" 
            className="text-dark/70 hover:text-teal-600 transition-colors pb-1"
          >
            My Day's Timeline
          </Link>
          <Link 
            id="nav-upload" 
            href="/upload" 
            className="text-dark/70 hover:text-teal-600 transition-colors pb-1"
          >
            Upload Video
          </Link>
        </nav>
      </header>

      {/* Main chat window container */}
      <main className="flex-1 flex flex-col max-w-3xl w-full mx-auto p-4 sm:p-6 justify-between">
        <h1 className="sr-only">EchoMind Caring Chat Assistant</h1>
        
        {/* Messages List */}
        <div className="flex-1 overflow-y-auto mb-6 space-y-6 min-h-[400px] pr-2">
          {messages.map((msg) => {
            const isUser = msg.sender === "user";
            const isSystem = msg.sender === "system";
            
            return (
              <div 
                key={msg.id}
                className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}
              >
                {/* Bubble */}
                <div 
                  className={`max-w-[85%] rounded-2xl p-5 shadow-sm text-lg leading-relaxed ${
                    isUser 
                      ? "bg-teal-100 text-dark rounded-tr-none border border-teal-500/20"
                      : isSystem
                        ? "bg-teal-50/80 text-dark border-l-4 border-teal-500"
                        : "bg-white text-dark rounded-tl-none border border-cream-darker"
                  }`}
                >
                  <p>{msg.text}</p>
                  
                  {/* Referenced Events (collapsible) */}
                  {msg.referencedEvents && msg.referencedEvents.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-cream-darker text-base">
                      <button
                        id={`btn-toggle-events-${msg.id}`}
                        onClick={() => toggleEvents(msg.id)}
                        className="text-teal-600 hover:text-teal-500 font-medium flex items-center gap-1 focus:outline-none transition-colors cursor-pointer"
                        aria-expanded={!!expandedEvents[msg.id]}
                        aria-controls={`events-details-${msg.id}`}
                      >
                        <span>{expandedEvents[msg.id] ? "▼ Hide memory records" : "▶ Show memory records"}</span>
                        <span className="text-xs bg-teal-50 px-2 py-0.5 rounded-full text-teal-600 border border-teal-100">
                          {msg.referencedEvents.length}
                        </span>
                      </button>
                      
                      {expandedEvents[msg.id] && (
                        <div 
                          id={`events-details-${msg.id}`} 
                          className="mt-3 space-y-2 bg-cream/70 p-3 rounded-lg border border-cream-darker"
                        >
                          <p className="text-xs font-semibold uppercase tracking-wider text-dark/60 mb-2">
                            Events I remembered for this answer:
                          </p>
                          <ul className="space-y-2">
                            {msg.referencedEvents.map((evt, idx) => (
                              <li 
                                key={evt.id || idx}
                                className="text-sm text-dark bg-white/90 p-2.5 rounded border border-cream-darker"
                              >
                                <div className="font-semibold text-teal-600 capitalize">
                                  {evt.object} — {evt.action.replace('_', ' ')}
                                </div>
                                <div className="text-xs text-dark/70 mt-1 flex justify-between">
                                  <span>Location: {evt.zone || "Unknown Area"}</span>
                                  <span>Time: {formatTime(evt.timestamp)}</span>
                                </div>
                                {evt.actor && (
                                  <div className="text-xs text-dark/60 mt-0.5">
                                    Person involved: <span className="capitalize">{evt.actor}</span>
                                  </div>
                                )}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Time label */}
                  <span className="block text-right text-xs text-dark/40 mt-2 font-mono">
                    {msg.timestamp}
                  </span>
                </div>
              </div>
            );
          })}

          {/* Loading bubble */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-cream-darker rounded-2xl rounded-tl-none p-5 shadow-sm text-lg text-dark/60 flex items-center space-x-2">
                <div className="flex space-x-1" aria-hidden="true">
                  <div className="w-2.5 h-2.5 bg-teal-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2.5 h-2.5 bg-teal-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2.5 h-2.5 bg-teal-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
                <span>Checking my memories...</span>
              </div>
            </div>
          )}

          {/* Error Alert */}
          {errorMsg && (
            <div 
              id="chat-error-state" 
              className="bg-critical-50 border border-critical-500 text-critical-700 rounded-xl p-4 text-base shadow-sm"
              role="alert"
            >
              <div className="font-semibold text-lg mb-1">Oh dear, I had a little trouble:</div>
              <p>{errorMsg}</p>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSend} className="bg-white rounded-2xl shadow-md border border-teal-100 p-2 flex items-center space-x-2">
          <input
            id="chat-input-question"
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask me a question (e.g., 'Did I take my medicine?')"
            className="flex-1 bg-transparent py-4 px-4 text-lg border-0 focus:outline-none placeholder-dark/40 text-dark min-h-[56px]"
            disabled={isLoading}
            autoComplete="off"
          />
          <button
            id="btn-chat-send"
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="bg-teal-500 hover:bg-teal-600 text-white font-semibold text-lg py-3 px-6 rounded-xl transition-all shadow-sm disabled:opacity-40 disabled:cursor-not-allowed hover:shadow cursor-pointer flex items-center justify-center min-h-[48px]"
          >
            Ask Me
          </button>
        </form>
      </main>

      {/* Reassuring footer */}
      <footer className="py-6 border-t border-teal-100 text-center text-sm text-dark/50">
        <p>EchoMind is always here to help you remember. Your privacy is fully protected.</p>
      </footer>
    </div>
  );
}



