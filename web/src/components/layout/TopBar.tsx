"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Search,
  Sparkles,
} from "lucide-react";

export function TopBar() {
  const router = useRouter();
  const [navSearch, setNavSearch] = useState("");

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (navSearch.trim()) {
      router.push(`/search?q=${encodeURIComponent(navSearch.trim())}`);
    }
  };

  return (
    <header className="h-16 bg-surface/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-40 border-b border-white/5 select-none">
      {/* Navigation history controls */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => router.back()}
            className="w-8 h-8 rounded-full bg-black/60 hover:bg-black/80 text-white flex items-center justify-center transition-colors"
            title="Go back"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <button
            onClick={() => router.forward()}
            className="w-8 h-8 rounded-full bg-black/60 hover:bg-black/80 text-white flex items-center justify-center transition-colors"
            title="Go forward"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        {/* Quick Search bar */}
        <form onSubmit={handleSearchSubmit} className="relative hidden sm:block w-72">
          <Search className="w-4 h-4 text-muted absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="What do you want to play?"
            value={navSearch}
            onChange={(e) => setNavSearch(e.target.value)}
            className="w-full bg-surface-elevated hover:bg-surface-highlight text-white text-xs rounded-full pl-9 pr-4 py-2 focus:outline-none focus:ring-2 focus:ring-white/20 transition-all placeholder:text-muted"
          />
        </form>
      </div>

      {/* Right Action buttons */}
      <div className="flex items-center gap-3">
        {/* Streamlit Studio Direct Launcher */}
        <a
          href="http://localhost:8501"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-full bg-surface-elevated hover:bg-surface-highlight border border-white/10 text-white transition-colors"
          title="Open Streamlit Studio in new tab (localhost:8501)"
        >
          <Sparkles className="w-3.5 h-3.5 text-primary" />
          <span className="hidden md:inline">Open Studio</span>
          <ExternalLink className="w-3 h-3 text-muted" />
        </a>

        {/* User Avatar */}
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center text-white font-bold text-xs ring-2 ring-black">
          ST
        </div>
      </div>
    </header>
  );
}
