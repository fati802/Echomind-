"use client";

import { useState, useRef } from "react";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

function UploadIcon() {
  return (
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-teal-500" aria-hidden="true">
      <path d="M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
      <polyline points="7 9 12 4 17 9" />
      <line x1="12" y1="4" x2="12" y2="16" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-teal-600 flex-shrink-0" aria-hidden="true">
      <circle cx="12" cy="12" r="9" />
      <polyline points="8 12.5 11 15.5 16 9.5" />
    </svg>
  );
}

function AlertIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-critical-700 flex-shrink-0" aria-hidden="true">
      <circle cx="12" cy="12" r="9" />
      <line x1="12" y1="8" x2="12" y2="13" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
}

function FilmIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-teal-600 flex-shrink-0" aria-hidden="true">
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <line x1="3" y1="9" x2="21" y2="9" />
      <line x1="3" y1="15" x2="21" y2="15" />
      <line x1="8" y1="4" x2="8" y2="9" />
      <line x1="15" y1="4" x2="15" y2="9" />
    </svg>
  );
}

export default function VideoUpload() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("idle");
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const inputRef = useRef(null);

  const handleFileSelect = (e) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      setStatus("idle");
      setResult(null);
      setErrorMsg(null);
    }
  };

  const handleUpload = () => {
    if (!file) return;

    setStatus("uploading");
    setProgress(0);
    setErrorMsg(null);

    const formData = new FormData();
    formData.append("file", file);

    const xhr = new XMLHttpRequest();

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        const pct = Math.round((e.loaded / e.total) * 100);
        setProgress(pct);
        if (pct >= 100) setStatus("processing");
      }
    };

    xhr.onload = () => {
      try {
        const data = JSON.parse(xhr.responseText);
        if (xhr.status >= 200 && xhr.status < 300) {
          setResult(data);
          setStatus("done");
        } else {
          setErrorMsg(data.detail || "Something went wrong processing your video.");
          setStatus("error");
        }
      } catch (err) {
        setErrorMsg("Something went wrong processing your video.");
        setStatus("error");
      }
    };

    xhr.onerror = () => {
      setErrorMsg("I had trouble reaching my memory database. Please check your connection and try again.");
      setStatus("error");
    };

    xhr.open("POST", `${API_BASE}/api/upload-video`);
    xhr.send(formData);
  };

  const reset = () => {
    setFile(null);
    setStatus("idle");
    setProgress(0);
    setResult(null);
    setErrorMsg(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <section className="bg-white rounded-2xl shadow-sm border border-cream-darker p-6 space-y-5">
      <div>
        <h2 className="text-2xl font-semibold text-dark font-sans">Upload a video</h2>
        <p className="text-base text-dark/60 mt-1">
          Share a video from your home camera and I will watch it for you, quietly noting where things end up.
        </p>
      </div>

      {status === "idle" && (
        <div className="flex flex-col items-center justify-center border-2 border-dashed border-teal-100 rounded-2xl py-10 px-6 text-center space-y-3">
          <UploadIcon />
          <div>
            <p className="text-lg font-medium text-dark">
              {file ? file.name : "Choose a video to upload"}
            </p>
            <p className="text-sm text-dark/50 mt-1">MP4, MOV, or other common video formats</p>
          </div>
          <input
            ref={inputRef}
            id="video-file-input"
            type="file"
            accept="video/*"
            onChange={handleFileSelect}
            className="hidden"
          />
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              className="bg-cream hover:bg-cream-darker text-dark px-5 py-2.5 rounded-xl border border-cream-darker text-base font-medium transition-colors cursor-pointer"
            >
              {file ? "Choose a different file" : "Browse files"}
            </button>
            {file && (
              <button
                type="button"
                onClick={handleUpload}
                className="bg-teal-500 hover:bg-teal-600 text-white font-semibold text-base py-2.5 px-6 rounded-xl transition-all shadow-sm cursor-pointer"
              >
                Upload and process
              </button>
            )}
          </div>
        </div>
      )}

      {(status === "uploading" || status === "processing") && (
        <div className="py-8 px-6 text-center space-y-4">
          <div className="w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          {status === "uploading" ? (
            <>
              <p className="text-lg font-medium text-dark">Uploading {file?.name}…</p>
              <div className="w-full bg-cream-darker rounded-full h-2.5 max-w-sm mx-auto overflow-hidden">
                <div className="bg-teal-500 h-2.5 rounded-full transition-all" style={{ width: `${progress}%` }}></div>
              </div>
            </>
          ) : (
            <>
              <p className="text-lg font-medium text-dark">Watching your video and noting what I see…</p>
              <p className="text-sm text-dark/50">This can take a minute or two for longer videos.</p>
            </>
          )}
        </div>
      )}

      {status === "done" && result && (
        <div className="bg-teal-50 border border-teal-100 rounded-xl p-5 space-y-3">
          <div className="flex items-center gap-2">
            <CheckIcon />
            <p className="font-medium text-teal-700">Video processed successfully</p>
          </div>
          <div className="flex items-center gap-2 text-sm text-dark/70">
            <FilmIcon />
            <span>{result.filename}</span>
          </div>
          <div className="flex gap-4 text-sm text-dark/70">
            <span>{result.detections_count} detections found</span>
            <span>{result.events_count} events logged</span>
          </div>
          <div className="flex gap-3 pt-1">
            <Link href="/timeline" className="bg-teal-500 hover:bg-teal-600 text-white font-semibold text-sm py-2 px-4 rounded-lg transition-all shadow-sm cursor-pointer">
              View updated timeline
            </Link>
            <button type="button" onClick={reset} className="bg-white hover:bg-cream text-dark text-sm py-2 px-4 rounded-lg border border-cream-darker transition-colors cursor-pointer">
              Upload another
            </button>
          </div>
        </div>
      )}

      {status === "error" && (
        <div className="bg-critical-50 border border-critical-500 text-critical-700 rounded-xl p-5 space-y-3">
          <div className="flex items-center gap-2">
            <AlertIcon />
            <p className="font-semibold">Oh dear, I had a little trouble:</p>
          </div>
          <p className="text-sm">{errorMsg}</p>
          <button type="button" onClick={reset} className="bg-critical-500 hover:bg-critical-700 text-white font-medium py-2 px-4 rounded-lg text-sm transition-colors cursor-pointer">
            Try again
          </button>
        </div>
      )}
    </section>
  );
}