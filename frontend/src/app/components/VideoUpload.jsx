"use client";

import { useState, useRef } from "react";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

function UploadCloudIcon() {
  return (
    <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M20 16.2A5 5 0 0 0 18 6.5a7 7 0 0 0-13.5 2A4.5 4.5 0 0 0 6 17" />
      <polyline points="16 12 12 8 8 12" />
      <line x1="12" y1="8" x2="12" y2="18" />
    </svg>
  );
}

function CheckIcon({ size = 18 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function AlertIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="text-critical-700 flex-shrink-0" aria-hidden="true">
      <circle cx="12" cy="12" r="9" />
      <line x1="12" y1="8" x2="12" y2="13" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
}

function FilmIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className="text-teal-700 flex-shrink-0" aria-hidden="true">
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <line x1="3" y1="9" x2="21" y2="9" />
      <line x1="3" y1="15" x2="21" y2="15" />
      <line x1="8" y1="4" x2="8" y2="9" />
      <line x1="15" y1="4" x2="15" y2="9" />
    </svg>
  );
}

function XIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

function formatBytes(bytes) {
  if (!bytes) return "";
  const units = ["B", "KB", "MB", "GB"];
  let i = 0;
  let n = bytes;
  while (n >= 1024 && i < units.length - 1) {
    n /= 1024;
    i++;
  }
  return `${n.toFixed(n >= 10 || i === 0 ? 0 : 1)} ${units[i]}`;
}

export default function VideoUpload() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("idle");
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef(null);

  const applyFile = (selected) => {
    if (!selected) return;
    setFile(selected);
    setStatus("idle");
    setResult(null);
    setErrorMsg(null);
  };

  const handleFileSelect = (e) => {
    applyFile(e.target.files?.[0]);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!dragActive) setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const dropped = e.dataTransfer?.files?.[0];
    if (dropped && dropped.type.startsWith("video/")) {
      applyFile(dropped);
    } else if (dropped) {
      setErrorMsg("Please drop a video file (MP4, MOV, etc.).");
      setStatus("error");
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
      } catch {
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

  // IDLE
  if (status === "idle") {
    return (
      <div className="card-soft p-3 sm:p-4">
        <div
          onDragOver={handleDragOver}
          onDragEnter={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => !file && inputRef.current?.click()}
          className={`relative rounded-2xl transition-all border-2 border-dashed ${
            dragActive
              ? "border-teal-500 bg-teal-50/70 scale-[1.01]"
              : file
                ? "border-teal-100 bg-cream/30"
                : "border-teal-100 bg-cream/30 hover:border-teal-500 hover:bg-teal-50/40 cursor-pointer"
          }`}
        >
          <input
            ref={inputRef}
            id="video-file-input"
            type="file"
            accept="video/*"
            onChange={handleFileSelect}
            className="hidden"
          />

          {!file ? (
            <div className="flex flex-col items-start gap-4 p-10 sm:p-14">
              <div className="w-16 h-16 rounded-2xl bg-white border border-teal-100 flex items-center justify-center text-teal-600 shadow-sm">
                <UploadCloudIcon />
              </div>
              <div className="text-left">
                <p className="text-xl font-semibold text-dark tracking-tight">
                  {dragActive ? "Drop your video here" : "Drag & drop your video"}
                </p>
                <p className="text-sm text-dark/55 mt-1.5">
                  Or click anywhere in this box to browse. MP4, MOV, and other common formats.
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-2 pt-1">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    inputRef.current?.click();
                  }}
                  className="bg-teal-600 hover:bg-teal-700 text-white font-medium text-sm py-2.5 px-5 rounded-xl transition-all cursor-pointer"
                >
                  Choose a video
                </button>
                <span className="text-xs text-dark/45 pl-1">Max ~500 MB · Kept private</span>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-4 p-5">
              <div className="w-14 h-14 rounded-xl bg-teal-50 border border-teal-100 flex items-center justify-center flex-shrink-0">
                <FilmIcon />
              </div>
              <div className="flex-1 min-w-0 text-left">
                <p className="text-base font-medium text-dark truncate">{file.name}</p>
                <p className="text-xs text-dark/50 mt-0.5">{formatBytes(file.size)} · Ready to upload</p>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    reset();
                  }}
                  className="w-9 h-9 flex items-center justify-center rounded-lg bg-white border border-cream-darker hover:border-critical-500 hover:text-critical-700 text-dark/50 transition-colors cursor-pointer"
                  aria-label="Remove file"
                >
                  <XIcon />
                </button>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleUpload();
                  }}
                  className="bg-teal-600 hover:bg-teal-700 text-white font-medium text-sm py-2.5 px-5 rounded-xl transition-all cursor-pointer"
                >
                  Upload & process
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // UPLOADING / PROCESSING
  if (status === "uploading" || status === "processing") {
    return (
      <div className="card-soft p-6 sm:p-8">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-xl bg-teal-50 border border-teal-100 flex items-center justify-center flex-shrink-0">
            <div className="w-6 h-6 border-[3px] border-teal-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs uppercase tracking-widest text-teal-600 font-medium">
              {status === "uploading" ? "Uploading" : "Processing"}
            </p>
            <p className="text-base font-medium text-dark mt-1 truncate">
              {status === "uploading" ? file?.name : "Watching your video and noting what I see…"}
            </p>
            {status === "uploading" ? (
              <>
                <div className="w-full bg-cream-darker rounded-full h-2 mt-4 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-teal-500 to-teal-600 h-2 rounded-full transition-all"
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
                <div className="flex items-center justify-between mt-2 text-xs text-dark/50">
                  <span>{progress}%</span>
                  <span>{file && formatBytes(file.size)}</span>
                </div>
              </>
            ) : (
              <p className="text-sm text-dark/55 mt-2">
                This can take a minute or two for longer videos. You can keep this page open.
              </p>
            )}
          </div>
        </div>
      </div>
    );
  }

  // DONE
  if (status === "done" && result) {
    return (
      <div className="card-soft p-6 sm:p-8 fade-in">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-full bg-teal-600 text-white flex items-center justify-center flex-shrink-0 shadow-[0_4px_16px_rgba(29,107,92,0.3)]">
            <CheckIcon size={24} />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs uppercase tracking-widest text-teal-600 font-medium">Complete</p>
            <p className="text-lg font-semibold text-dark mt-1">Video processed successfully</p>
            <div className="flex items-center gap-2 mt-2 text-sm text-dark/60">
              <FilmIcon />
              <span className="truncate">{result.filename}</span>
            </div>

            <div className="grid grid-cols-2 gap-3 mt-5">
              <div className="rounded-xl bg-cream/60 border border-cream-darker p-3">
                <p className="text-[0.65rem] uppercase tracking-widest text-dark/45 font-medium">Detections</p>
                <p className="text-2xl font-semibold text-teal-700 mt-0.5">{result.detections_count}</p>
              </div>
              <div className="rounded-xl bg-cream/60 border border-cream-darker p-3">
                <p className="text-[0.65rem] uppercase tracking-widest text-dark/45 font-medium">Events logged</p>
                <p className="text-2xl font-semibold text-teal-700 mt-0.5">{result.events_count}</p>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 mt-5">
              <Link
                href="/timeline"
                className="bg-teal-600 hover:bg-teal-700 text-white font-medium text-sm py-2.5 px-5 rounded-xl transition-all cursor-pointer"
              >
                View updated timeline
              </Link>
              <button
                type="button"
                onClick={reset}
                className="bg-white hover:bg-cream text-dark/80 text-sm font-medium py-2.5 px-5 rounded-xl border border-cream-darker transition-colors cursor-pointer"
              >
                Upload another
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ERROR
  return (
    <div className="card-soft p-6 sm:p-8 fade-in">
      <div className="flex items-start gap-4">
        <div className="w-14 h-14 rounded-xl bg-critical-50 border border-critical-500/25 flex items-center justify-center flex-shrink-0">
          <AlertIcon />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs uppercase tracking-widest text-critical-700 font-medium">Trouble</p>
          <p className="text-base font-semibold text-dark mt-1">I had a little trouble</p>
          <p className="text-sm text-dark/65 mt-1">{errorMsg}</p>
          <button
            type="button"
            onClick={reset}
            className="mt-4 bg-critical-500 hover:bg-critical-700 text-white font-medium py-2 px-4 rounded-lg text-sm transition-colors cursor-pointer"
          >
            Try again
          </button>
        </div>
      </div>
    </div>
  );
}
