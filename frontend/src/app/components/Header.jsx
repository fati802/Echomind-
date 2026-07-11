"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import Logo from "./Logo";

const NAV = [
  { href: "/", label: "Ask" },
  { href: "/timeline", label: "Timeline" },
  { href: "/upload", label: "Upload" },
];

export default function Header() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 bg-cream/85 backdrop-blur-xl border-b border-teal-100/60">
      <div className="w-full flex items-center justify-between px-5 sm:px-8 lg:px-12 h-16 overflow-visible">
        <Link href="/" className="flex items-center focus:outline-none -my-10" aria-label="EchoMind home">
          <Logo height={130} />
        </Link>

        <nav className="flex items-center gap-1" aria-label="Primary Navigation">
          {NAV.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                id={`nav-${item.label.toLowerCase()}`}
                href={item.href}
                className={`relative px-4 py-2 rounded-full text-sm font-medium transition-all ${
                  active
                    ? "text-teal-700 bg-teal-50 shadow-sm"
                    : "text-dark/60 hover:text-teal-700 hover:bg-teal-50/50"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
