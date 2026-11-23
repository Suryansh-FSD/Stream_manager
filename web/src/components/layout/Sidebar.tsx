"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  Search,
  Library,
  BarChart2,
  Heart,
  TrendingUp,
  Disc3,
  ExternalLink,
  Music2,
  Database,
} from "lucide-react";
import { useAudio } from "@/components/player/AudioContext";

export function Sidebar() {
  const pathname = usePathname();
  const { likedTrackIds } = useAudio();

  const navItems = [
    { label: "Home", href: "/", icon: Home },
    { label: "Search", href: "/search", icon: Search },
    { label: "Your Library", href: "/library", icon: Library },
  ];

  return (
    <aside className="w-64 bg-black flex flex-col h-full border-r border-white/5 select-none flex-shrink-0">
      {/* Brand Header */}
      <div className="p-6 pb-4">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-primary to-emerald-300 flex items-center justify-center text-black font-black shadow-lg shadow-primary/20 group-hover:scale-105 transition-transform">
            <Music2 className="w-5 h-5 fill-black stroke-black" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-white tracking-tight text-lg">Spotify Trends</span>
              <span className="text-[10px] font-semibold bg-primary/20 text-primary border border-primary/30 px-1.5 py-0.2 rounded">
                PRO
              </span>
            </div>
            <p className="text-[11px] text-muted">Music & Audio Intelligence</p>
          </div>
        </Link>
      </div>

      {/* Main Navigation */}
      <nav className="px-3 py-2 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-4 px-3 py-2.5 rounded-md text-sm font-semibold transition-colors ${
                isActive
                  ? "bg-surface-elevated text-white"
                  : "text-muted hover:text-white hover:bg-surface/60"
              }`}
            >
              <Icon className={`w-5 h-5 ${isActive ? "text-primary" : ""}`} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Analytics Studio Highlight */}
      <div className="px-3 py-3">
        <div className="text-[11px] font-bold tracking-wider text-muted-dark uppercase px-3 mb-2">
          Analytics Engine
        </div>
        <Link
          href="/analytics"
          className={`flex items-center justify-between px-3 py-2.5 rounded-md text-sm font-semibold transition-all ${
            pathname === "/analytics"
              ? "bg-primary text-black font-bold shadow-md shadow-primary/25"
              : "text-white bg-surface-elevated hover:bg-surface-highlight border border-white/5"
          }`}
        >
          <div className="flex items-center gap-3">
            <BarChart2 className="w-5 h-5 text-emerald-400 group-hover:rotate-6 transition-transform" />
            <span>Analytics Studio</span>
          </div>
          <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-black/40 text-emerald-400">
            Streamlit
          </span>
        </Link>
      </div>

      {/* Quick Library Links */}
      <div className="px-3 py-2 flex-1 overflow-y-auto space-y-1">
        <div className="text-[11px] font-bold tracking-wider text-muted-dark uppercase px-3 mb-2">
          Playlists & Shortcuts
        </div>

        <Link
          href="/library?tab=liked"
          className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-muted hover:text-white hover:bg-surface/50 transition-colors group"
        >
          <div className="w-7 h-7 rounded bg-gradient-to-br from-indigo-600 to-emerald-400 flex items-center justify-center text-white">
            <Heart className="w-3.5 h-3.5 fill-white" />
          </div>
          <div className="overflow-hidden">
            <div className="text-sm font-medium text-white truncate">Liked Songs</div>
            <div className="text-xs text-muted">
              {likedTrackIds.size > 0 ? `${likedTrackIds.size} songs` : "Empty playlist"}
            </div>
          </div>
        </Link>

        <Link
          href="/search"
          className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-muted hover:text-white hover:bg-surface/50 transition-colors"
        >
          <div className="w-7 h-7 rounded bg-gradient-to-br from-purple-700 to-pink-600 flex items-center justify-center text-white">
            <TrendingUp className="w-3.5 h-3.5" />
          </div>
          <div className="overflow-hidden">
            <div className="text-sm font-medium text-white truncate">Trending Genres</div>
            <div className="text-xs text-muted">Electronic, Ambient & Pop</div>
          </div>
        </Link>

        <Link
          href="/library?tab=albums"
          className="flex items-center gap-3 px-3 py-2 rounded-md text-sm text-muted hover:text-white hover:bg-surface/50 transition-colors"
        >
          <div className="w-7 h-7 rounded bg-gradient-to-br from-blue-700 to-teal-500 flex items-center justify-center text-white">
            <Disc3 className="w-3.5 h-3.5" />
          </div>
          <div className="overflow-hidden">
            <div className="text-sm font-medium text-white truncate">Albums Catalog</div>
            <div className="text-xs text-muted">357 releases</div>
          </div>
        </Link>
      </div>

      {/* Dataset / Connection Status Footer */}
      <div className="p-4 border-t border-white/5 bg-surface/30">
        <div className="flex items-center justify-between text-xs text-muted">
          <div className="flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5 text-primary" />
            <span className="font-mono text-[11px]">Benchmark Dataset (495)</span>
          </div>
          <span className="inline-block w-2 h-2 rounded-full bg-primary animate-pulse" />
        </div>
      </div>
    </aside>
  );
}
