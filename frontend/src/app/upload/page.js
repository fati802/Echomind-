import VideoUpload from "@/app/components/VideoUpload";

function StepDot({ n }) {
  return (
    <div className="w-8 h-8 rounded-full bg-teal-600 text-white flex items-center justify-center flex-shrink-0 text-sm font-semibold shadow-[0_2px_10px_rgba(29,107,92,0.25)]">
      {n}
    </div>
  );
}

function LockIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="4" y="11" width="16" height="10" rx="2" />
      <path d="M8 11V7a4 4 0 1 1 8 0v4" />
    </svg>
  );
}

export default function Upload() {
  return (
    <div className="w-full px-5 sm:px-8 lg:px-12 pt-6 pb-16">
      <h1 className="sr-only">Upload a video to EchoMind</h1>

      {/* HEADER */}
      <div className="mb-6">
        <p className="text-xs uppercase tracking-[0.22em] text-teal-600 font-medium">Upload</p>
        <h2 className="text-3xl font-semibold text-dark mt-1 tracking-tight">Share a moment from your day</h2>
        <p className="text-sm text-dark/55 mt-1.5 max-w-2xl">
          Send a video from your home camera and I&apos;ll quietly watch it — noting where things end up so you don&apos;t have to remember.
        </p>
      </div>

      {/* MAIN GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-[1.6fr_1fr] gap-6 items-start">
        {/* LEFT — Uploader */}
        <VideoUpload />

        {/* RIGHT — Steps + Privacy */}
        <aside className="space-y-4">
          <div className="card-soft p-5">
            <p className="text-xs uppercase tracking-[0.18em] text-teal-600 font-medium">How it works</p>
            <ol className="mt-4 space-y-4">
              <li className="flex items-start gap-3">
                <StepDot n={1} />
                <div className="text-left">
                  <p className="text-sm font-semibold text-dark">Watch quietly</p>
                  <p className="text-xs text-dark/55 mt-0.5">I go through your video scene by scene.</p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <StepDot n={2} />
                <div className="text-left">
                  <p className="text-sm font-semibold text-dark">Note gently</p>
                  <p className="text-xs text-dark/55 mt-0.5">Objects, people, and actions are noted.</p>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <StepDot n={3} />
                <div className="text-left">
                  <p className="text-sm font-semibold text-dark">Update your timeline</p>
                  <p className="text-xs text-dark/55 mt-0.5">Your day&apos;s timeline reflects what I saw.</p>
                </div>
              </li>
            </ol>
          </div>

          <div className="rounded-2xl bg-rose-50/60 border border-rose-100 p-5">
            <div className="flex items-center gap-2 text-rose-600">
              <LockIcon />
              <p className="text-xs uppercase tracking-[0.15em] font-semibold">Private by design</p>
            </div>
            <p className="mt-2 text-sm text-dark/70 leading-relaxed">
              Videos stay yours. Nothing is shared, and you can remove anything I remember at any time.
            </p>
          </div>

          <div className="rounded-2xl bg-teal-50/40 border border-teal-100 p-5">
            <p className="text-xs uppercase tracking-[0.15em] text-teal-700 font-semibold">Tip</p>
            <p className="mt-2 text-sm text-dark/70 leading-relaxed">
              Shorter clips process faster. Try uploading 1–3 minute segments for the smoothest experience.
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}
