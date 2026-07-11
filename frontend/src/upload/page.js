"use client";

import Link from "next/link";
import VideoUpload from "@/app/components/VideoUpload";

function FlowerIcon() {
  return (
    <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-rose-600" aria-hidden="true">
      <circle cx="12" cy="12" r="2.5" />
      <path d="M12 2a3 3 0 0 1 0 6 3 3 0 0 1 0-6zM12 16a3 3 0 0 1 0 6 3 3 0 0 1 0-6zM2 12a3 3 0 0 1 6 0 3 3 0 0 1-6 0zM16 12a3 3 0 0 1 6 0 3 3 0 0 1-6 0z" />
    </svg>
  );
}

export default function Upload() {
  return (
    <div className="flex flex-col min-h-screen bg-cream">
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-teal-100 py-4 px-6 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <FlowerIcon />
          <span className="text-2xl font-semibold tracking-tight text-teal-600 font-sans">EchoMind</span>
        </div>
        <nav className="flex space-x-6 text-lg font-medium" aria-label="Primary Navigation">
          <Link id="nav-chat" href="/" className="text-dark/70 hover:text-teal-600 transition-colors pb-1">
            Ask Questions
          </Link>
          <Link id="nav-timeline" href="/timeline" className="text-dark/70 hover:text-teal-600 transition-colors pb-1">
            My Day's Timeline
          </Link>
          <Link id="nav-upload" href="/upload" className="text-teal-600 border-b-2 border-teal-500 pb-1">
            Upload Video
          </Link>
        </nav>
      </header>

      <main className="flex-1 max-w-3xl w-full mx-auto p-4 sm:p-6 space-y-6">
        <h1 className="sr-only">Upload a video to EchoMind</h1>
        <VideoUpload />
      </main>

      <footer className="py-6 border-t border-teal-100 text-center text-sm text-dark/50 mt-12">
        <p>EchoMind is always here to help you remember. Your privacy is fully protected.</p>
      </footer>
    </div>
  );
}